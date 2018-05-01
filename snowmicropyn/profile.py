import configparser
import csv
import logging
from datetime import datetime
from os.path import exists, splitext, split, join

import pandas as pd
import pytz
from pandas import np as np

from .detection import detect_ground, detect_surface
from .loewe2011 import shotnoise
from .proksch2015 import model_ssa_and_density
from .pnt import Pnt
from . import __version__, githash

log = logging.getLogger(__name__)


class Profile(object):
    """ Represents a loaded pnt file.

    SnowMicroPen stores a recorded profile in a proprietary and binary format
    with a ``pnt`` file extension. A pnt file consists of a header with meta
    information and the recorded force measurement values. When a pnt file is
    loaded using this class, it reads this data. Meta information then can be
    accessed by many properties like :attr:`timestamp` or :attr:`overload`.
    The measurement data is called "samples". Its accessed using the property
    :attr:`samples` or methods prefix with ``samples_``.

    The class supports the settings of "markers". They identified by name and
    mark a certain distance value on the profile. You can set markers, read
    marker values, and remove markers. The two *well known* markers called
    "surface" and "ground" are used to determine the snowpack. Markers are not
    stored in a pnt file. As a fact, the pnt file is always just read and never
    written by the *snowmicropyn* package. To store marker values, this class
    writes ini files (``*.ini``) named same as the pnt file (but with its
    ini file extension, of course). Use the method :meth:`save` to save your
    markers.

    When a profile is loaded, the class tries to find a
    ini file named as the pnt file. In case one is found, it's read
    automatically and your prior set markers are available again.

    To improve readability of your code, your encouraged to load a profile using
    its static method :meth:`load`. Here's an example::

        import snowmicropyn
        p = snowmicropyn.Profile.load('./S13M0013.pnt')

    After this call you can access the profile's meta properties::

        p.name
        p.timestamp  # Timezone aware :)
        p.coordinates  # WGS 84 latitude and longitude
        p.spatial_resolution  # [mm]
        p.overload

    ... and plenty more (not complete list).

    To get the measurement values, you use the :meth:`samples` property::

        s = p.samples  # It's a pandas dataframe
        print(s)

    Export of data can be achieved using the methods :meth:`export_meta` and
    :meth:`export_samples`. Each method writes a file in CSV format::

        p.export_meta()
        p.export_samples()

    """

    def __init__(self, pnt_filename, name=None):
        # Load pnt file, returns header (dict) and force samples
        self._pnt_filename = pnt_filename
        self._pnt_header, pnt_samples = Pnt.load(pnt_filename)

        # Get clean WGS84 coordinates (use +/- instead of N/E)
        self._latitude = self.pnt_header_value(Pnt.Header.GPS_WGS84_LATITUDE)
        self._longitude = self.pnt_header_value(Pnt.Header.GPS_WGS84_LONGITUDE)
        north = self.pnt_header_value(Pnt.Header.GPS_WGS84_NORTH)
        east = self.pnt_header_value(Pnt.Header.GPS_WGS84_EAST)
        if north.upper() != 'N':
            self._latitude = -self._latitude
        if east.upper() != 'E':
            self._longitude = -self._longitude
        if abs(self._latitude) > 90:
            log.warning('Latitude value {} invalid, replacing by None'.format(self._latitude))
            self._latitude = None
        if abs(self._longitude) > 90:
            log.warning('Longitude value {} invalid, replacing by None'.format(self._longitude))
            self._longitude = None

        # Get a proper timestamp by putting pnt entries together
        self._timestamp = None
        year = self.pnt_header_value(Pnt.Header.TIMESTAMP_YEAR)
        month = self.pnt_header_value(Pnt.Header.TIMESTAMP_MONTH)
        day = self.pnt_header_value(Pnt.Header.TIMESTAMP_DAY)
        hour = self.pnt_header_value(Pnt.Header.TIMESTAMP_HOUR)
        minute = self.pnt_header_value(Pnt.Header.TIMESTAMP_MINUTE)
        second = self.pnt_header_value(Pnt.Header.TIMESTAMP_SECOND)
        try:
            self._timestamp = datetime(year, month, day, hour, minute, second, tzinfo=pytz.UTC)
            log.info('Timestamp of profile as reported by pnt header is {}'.format(self.timestamp))
        except ValueError:
            log.warning('Unable to build timestamp from pnt header fields')

        # Set name of profile (by default a entry from pnt header)
        self._name = self.pnt_header_value(Pnt.Header.FILENAME)
        if name:
            self._name = name

        # Get other important entries from header
        self._samples_count = self.pnt_header_value(Pnt.Header.SAMPLES_COUNT_FORCE)
        self._spatial_resolution = self.pnt_header_value(Pnt.Header.SAMPLES_SPATIALRES)
        self._overload = self.pnt_header_value(Pnt.Header.SENSOR_OVERLOAD)
        self._speed = self.pnt_header_value(Pnt.Header.SAMPLES_SPEED)

        self._smp_firmware = self.pnt_header_value(Pnt.Header.FIRMWARE)
        self._smp_serial = self.pnt_header_value(Pnt.Header.SMP_SERIAL)
        self._smp_length = self.pnt_header_value(Pnt.Header.SMP_LENGTH)
        self._smp_tipdiameter = self.pnt_header_value(Pnt.Header.TIP_DIAMETER)

        self._gps_pdop = self.pnt_header_value(Pnt.Header.GPS_PDOP)
        self._gps_numsats = self.pnt_header_value(Pnt.Header.GPS_NUMSATS)
        self._amplifier_range = self.pnt_header_value(Pnt.Header.AMPLIFIER_RANGE)
        self._amplifier_serial = self.pnt_header_value(Pnt.Header.AMPLIFIER_SERIAL)
        self._sensor_sensivity = self.pnt_header_value(Pnt.Header.SENSOR_SENSITIVITIY)

        # Create a pandas dataframe with distance and force
        distances = np.arange(0, self._samples_count) * self._spatial_resolution
        forces = np.asarray(pnt_samples) * self.pnt_header_value(
            Pnt.Header.SAMPLES_CONVFACTOR_FORCE)
        stacked = np.column_stack([distances, forces])
        self._samples = pd.DataFrame(stacked, columns=('distance', 'force'))

        self._ini = configparser.ConfigParser()

        # Look out for corresponding ini file
        self._ini_filename = splitext(self._pnt_filename)[0] + '.ini'
        if exists(self._ini_filename):
            log.info('Reading ini file {} for {}'.format(self._ini_filename, self))
            self._ini.read(self._ini_filename)

        # Ensure a section called 'markers' does exist
        if not self._ini.has_section('markers'):
            self._ini.add_section('markers')

        # Check for invalid values in 'markers' section
        for k, v in self._ini.items('markers'):
            try:
                float(v)
            except ValueError:
                log.warning(
                    'Ignoring value {} for marker {}, not float value'.format(repr(v), repr(k)))
                self._ini.remove_option('markers', k)

    def __str__(self):
        first = self.samples.distance.iloc[0]
        last = self.samples.distance.iloc[-1]
        length = last - first
        return 'Profile(name={}, {:.3f} mm, {} samples)'.format(repr(self.name), length, len(self))

    def __len__(self):
        return len(self.samples.distance)

    @property
    def name(self):
        """ Name of this profile. Can be specified when profile is loaded or,
        by default, "filename" header entry of the pnt file is used. """
        return self._name

    @property
    def pnt_filename(self):
        """ Name of the pnt file this data was loaded from. """
        return self._pnt_filename

    @property
    def ini_filename(self):
        """ Name of the ini file in which markers are saved. """
        return self._ini_filename

    @property
    def timestamp(self):
        """ Returns the timestamp when this profile was recorded. The timestamp
        is timezone aware.
        """
        return self._timestamp

    @property
    def overload(self):
        """ Returns the overload value configured when this profile was
        recorded.

        The unit of this value is N (Newton).
        """
        return self._overload

    @property
    def spatial_resolution(self):
        """ Returns the spatial resolution of this profile in mm (millimeters).
        """
        return self._spatial_resolution

    @property
    def speed(self):
        """ Returns the speed used to record this profile in mm/s (millimeters
        per second). """
        return self._speed

    @property
    def smp_length(self):
        """ Returns the length on the SnowMicroPen used. """
        return self._smp_length

    @property
    def smp_tipdiameter(self):
        """ Returns the tip diameter of SnowMicroPen used. """
        return self._smp_tipdiameter

    @property
    def smp_serial(self):
        """ Returns the serial number of the SnowMicroPen used to record this
        profile.
        """
        return self._smp_serial

    @property
    def smp_firmware(self):
        """ Returns the firmware version of the SnowMicroPen at the time of
        recording this profile.
        """
        return self._smp_firmware

    @property
    def gps_numsats(self):
        """ Returns the number of satellites available when location was
        determined using GPS. Acts as an indicator of location's quality.
        """
        return self._gps_numsats

    @property
    def gps_pdop(self):
        """ Returns positional DOP (dilution of precision) value when location
        was determined using GPS. Acts as an indicator of location's quality.
        """
        return self._gps_pdop

    @property
    def amplifier_serial(self):
        """ Returns the amplifier's serial number of the SnowMicroPen used to
        record this profile.
        """
        return self._amplifier_serial

    @property
    def amplifier_range(self):
        """ Returns the amplifier's range of the SnowMicroPen used to record
        this profile.
        """
        return self._amplifier_range

    @property
    def coordinates(self):
        """ Returns WGS 84 coordinates (latitude, longitude) of this profile in
        decimal format as a tuple of ``(float, float)`` or ``None`` when no
        coordinates are available.

        The coordinates are constructed by header fields of the pnt file. In
        case these header fields are empty or contain garbage, ``None`` is
        returned. You always can read the header fields yourself using the
        :meth:`pnt_header_value` of this class for investigating what's
        present in the pnt header fields.
        """
        if self._latitude and self._longitude:
            return self._latitude, self._longitude
        return None

    def pnt_header_value(self, pnt_header_id):
        """ Return the value of the pnt header by its ID.

        For a list of available IDs, see :class:`snowmicropyn.Pnt.Header`.
         """
        return self._pnt_header[pnt_header_id].value

    @property
    def samples(self):
        """ Returns the samples. This is a pandas dataframe."""
        return self._samples

    def default_filename(self, suffix, extension='.csv'):
        head, tail = split(self._pnt_filename)
        return join(head, self.name + '_' + suffix + extension)

    @property
    def markers(self):
        """ Returns a list of all markers. The lists contains tuples of name
        and value and its type is ``(str, float)``.
        """
        markers = self._ini.items('markers')
        markers = [(k, self.marker(k)) for k, v in markers]
        return markers

    # configparser._UNSET as default value for fallback is required to enable
    # None as a valid value to pass
    def marker(self, name, fallback=configparser._UNSET):
        """ Returns the value of a marker as a ``float``. In case a
        fallback value is provided and no marker is present, the fallback value
        is returned. It's recommended to pass a ``float`` fallback value.
        ``None`` is a valid fallback value.

        :param name: Name of the marker requested.
        :param fallback: Fallback value returned in case no marker exists for
               the provided name.
        """
        try:
            # Always return floats
            return self._ini.getfloat('markers', name, fallback=fallback)
        except configparser.NoOptionError:
            raise KeyError('No marker named {} available'.format(name))

    def set_marker(self, name, value):
        """ Sets a marker value.

        The provided value is converted into a ``float``. Raises
        :exc:`ValueError` in case this fails.

        :param name: Name of the marker.
        :param value: Value for the marker. Passing a ``float`` is recommended.
        """
        # Make sure value is a float, ValueError is raised otherwise,
        # None is ok too
        value = float(value)
        self._ini.set('markers', name, str(value))

    def remove_marker(self, name):
        """ Remove a marker.

        Raises :exc:`KeyError` in case no such marker is present.

        :param name: Name (``str``) of the marker to remove.
        """
        return float(self._ini.remove_option('markers', name))

    @property
    def surface(self):
        """ Convenience property to access value of 'surface' marker. """
        return self.marker('surface')

    @property
    def ground(self):
        """ Convenience property to access value of 'ground' marker. """
        return self.marker('ground')

    def max_force(self):
        """ Get maximum force value of this profile. """
        return self.samples.force.max()

    @staticmethod
    def load(pnt_filename, name=None):
        """ Loads a pnt file and its corresponding ini file too.

        :param pnt_filename:
        :param name: A
        """
        return Profile(pnt_filename, name)

    def save(self):
        """ Save markers of this profile to a ini file.

        .. warning::
           An already existing ini file is overwritten with no warning.

        When no markers are set on the profile, the resulting file will be
        empty.
        """
        with open(self._ini_filename, 'w') as f:
            log.info('Saving ini info of {} to file {}'.format(self, self._ini_filename))
            self._ini.write(f)

    def export_samples(self, filename=None, precision=4, snowpack_only=False):
        """ Export the samples of this profile into a CSV file.

        :param filename: Name of CSV file.
        :param precision: Precision (number of digits after comma) of the
               values. Default value is 4.
        :param snowpack_only: In case set to true, only samples within the
               markers surface and ground are exported.
        """

        if not filename:
            filename = splitext(self._pnt_filename)[0] + '_samples.csv'
        log.info('Exporting samples of {} to {}'.format(self, filename))
        samples = self.samples
        if snowpack_only:
            samples = self.samples_within_snowpack()
        fmt = '%.{}f'.format(precision)
        with open(filename, 'w') as f:
            # Write version and git hash as comment for tracking
            crumbs = '# Exported by snowmicropyn {} (git hash {})\n'.format(__version__, githash())
            f.write(crumbs)
            samples.to_csv(f, header=True, index=False, float_format=fmt)
        return filename

    def export_meta(self, filename=None, include_pnt_header=False):
        if not filename:
            filename = splitext(self._pnt_filename)[0] + '_meta.csv'
        log.info('Exporting meta information of {} to {}'.format(self, filename))
        with open(filename, 'w') as f:
            writer = csv.writer(f)
            # Write version and git hash as comment for tracking
            crumbs = '# Exported by snowmicropyn {} (git hash {})\n'.format(__version__, githash())
            f.write(crumbs)
            # CSV header
            writer.writerow(['key', 'value'])
            # Export important properties of profile
            writer.writerow(('name', self.name))
            writer.writerow(('pnt_file', self._pnt_filename))
            writer.writerow(('gps.coords.lat', self._latitude))
            writer.writerow(('gps.coords.long', self._longitude))
            writer.writerow(('gps.numsats', self.gps_numsats))
            writer.writerow(('gps.pdop', self.gps_pdop))
            writer.writerow(('smp.serial', self.smp_serial))
            writer.writerow(('smp.length', self.smp_length))
            # Export markers
            for k, v in self.markers:
                writer.writerow(('ini.marker.' + k, v))
            # Export pnt header entries
            if include_pnt_header:
                for header_id, (label, value, unit) in self._pnt_header.items():
                    writer.writerow(['pnt.' + header_id.name, str(value)])
        return filename

    def samples_within_distance(self, begin=None, end=None, relativize=False):
        """ Get samples within a certain distance, specified by parameters
        ``begin`` and ``end``

        Default value for both is ``None`` and results to returns values from
        beginning or to the end of the profile.

        Use parameter ``relativize`` in case you want to have the returned
        samples with distance values beginning from zero.

        :param begin: Start of distance of interest. Default is ``None``.
        :param end: End of distance of interest. Default is ``None``.
        :param relativize: When set to ``True``, the distance in the samples
               returned starts with 0.
        """

        # In case limits are None, use start begin or end of profile
        if begin is None:
            begin = self.samples.distance.iloc[0]
        if end is None:
            end = self.samples.distance.iloc[-1]

        # Flip range if necessary, so lower number is always first
        if begin >= end:
            end, begin = begin, end

        distance = self.samples.distance
        within = (distance >= begin) & (distance < end)
        samples = pd.DataFrame(self.samples[within])

        # Subtract offset to get relative distance
        if relativize:
            offset = samples.distance.iloc[0]
            samples.distance = samples.distance - offset

        return samples.reset_index(drop=True)

    def samples_within_snowpack(self, relativize=True):
        """ Returns samples within the snowpack, meaning between the values of
        marker "surface" and "ground". """
        try:
            s = self.marker('surface')
            g = self.marker('ground')
            return self.samples_within_distance(s, g, relativize)
        except KeyError as e:
            raise KeyError('Required marker missing in {}. Error: {}'.format(self, str(e)))

    def detect_surface(self):
        """ Convenience method to detect the surface. This also sets the marker
        called "surface". """
        surface = detect_surface(self.samples.values)
        self.set_marker('surface', surface)
        return surface

    def detect_ground(self):
        """ Convenience method to detect the ground. This also sets the marker
        called "surface". """
        ground = detect_ground(self.samples.values, self.overload)
        self.set_marker('ground', ground)
        return ground

    def model_shotnoise(self, save_to_file=False, filename_suffix='shotnoise'):
        sn = shotnoise(self.samples)
        if save_to_file:
            fname = self.default_filename(suffix=filename_suffix)
            log.info('Saving shot noise dataframe to {} to {}'.format(self, fname))
            with open(fname, 'w') as f:
                # Write version and git hash as comment for tracking
                crumbs = '# Exported by snowmicropyn {} (git hash {})\n'.format(__version__, githash())
                f.write(crumbs)
                sn.to_csv(f, index=False)
        return sn

    def model_ssa(self, save_to_file=False, filename_suffix='ssa'):
        ssa = model_ssa_and_density(self.samples)
        if save_to_file:
            fname = self.default_filename(suffix=filename_suffix)
            log.info('Saving ssa + density dataframe to {} to {}'.format(self, fname))
            with open(fname, 'w') as f:
                # Write version and git hash as comment for tracking
                crumbs = '# Exported by snowmicropyn {} (git hash {})\n'.format(__version__, githash())
                f.write(crumbs)
                ssa.to_csv(f, index=False)
        return ssa

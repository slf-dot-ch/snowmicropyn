import configparser
import csv
import logging
from datetime import datetime
from os.path import exists, splitext, split, join

import pandas as pd
import pytz

from .analysis import detect_surface, detect_ground
from .models import model_shotnoise, model_ssa_and_density
from .pnt import Pnt

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
    writes ini files (``*.ini``), usually named alike the pnt file but with its
    ini file extension. However, you can specify a different filename, but it's not
    recommended to do so. Use the method :meth:`save` to save your markers.

    When a profile is loaded, the class tries to find a
    ini file named as the pnt file. In case one is found, it's read
    automatically and your prior set markers are available again.

    To improve readability of the code, your encouraged to load a profile using
    the static method :meth:`load`. Here's an example::

        import snowmicropyn
        p = snowmicropyn.Profile.load('./S13M0013.pnt')
    """

    def __init__(self, pnt_filename, ini_filename=None, name=None):
        # Set name of profile (by default pnt filename without extension)
        self._name = name
        if not self._name:
            self._name = splitext(split(pnt_filename)[1])[0]

        # Load pnt file, returns samples and header (dict)
        self._pnt_filename = pnt_filename
        samples, self._pnt_header = Pnt.load_pnt(pnt_filename)
        # Create data frame of samples
        self._samples = pd.DataFrame(samples, columns=('distance', 'force'))

        # Get clean WGS84 coordinates (use +/- instead of N/E)
        self._latitude = self.pnt_header_value(Pnt.GPS_WGS84_LATITUDE)
        self._longitude = self.pnt_header_value(Pnt.GPS_WGS84_LONGITUDE)
        north = self.pnt_header_value(Pnt.GPS_WGS84_NORTH)
        east = self.pnt_header_value(Pnt.GPS_WGS84_EAST)
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
        year = self.pnt_header_value(Pnt.TIMESTAMP_YEAR)
        month = self.pnt_header_value(Pnt.TIMESTAMP_MONTH)
        day = self.pnt_header_value(Pnt.TIMESTAMP_DAY)
        hour = self.pnt_header_value(Pnt.TIMESTAMP_HOUR)
        minute = self.pnt_header_value(Pnt.TIMESTAMP_MINUTE)
        second = self.pnt_header_value(Pnt.TIMESTAMP_SECOND)
        try:
            self._timestamp = datetime(year, month, day, hour, minute, second, tzinfo=pytz.UTC)
            log.info('Timestamp of profile as reported by pnt header is {}'.format(self.timestamp))
        except ValueError:
            log.warning('Unable to build timestamp from pnt header fields')

        # Get other important entries from header
        self._smp_firmware = self.pnt_header_value(Pnt.FIRMWARE)
        self._smp_serial = self.pnt_header_value(Pnt.SMP_SERIAL)
        self._smp_length = self.pnt_header_value(Pnt.SMP_LENGTH)
        self._smp_tipdiameter = self.pnt_header_value(Pnt.TIP_DIAMETER)
        self._spatial_resolution = self.pnt_header_value(Pnt.SAMPLES_SPATIALRES)
        self._overload = self.pnt_header_value(Pnt.SENSOR_OVERLOAD)
        self._speed = self.pnt_header_value(Pnt.SAMPLES_SPEED)
        self._gps_pdop = self.pnt_header_value(Pnt.GPS_PDOP)
        self._gps_numsats = self.pnt_header_value(Pnt.GPS_NUMSATS)
        self._amplifier_range = self.pnt_header_value(Pnt.AMPLIFIER_RANGE)
        self._amplifier_serial = self.pnt_header_value(Pnt.AMPLIFIER_SERIAL)
        self._sensor_sensivity = self.default_filename(Pnt.SENSOR_SENSITIVITIY)

        # When no ini file provided, use default name which
        # is same as pnt file but ini extension
        self._ini_filename = ini_filename
        if not self._ini_filename:
            self._ini_filename = splitext(self._pnt_filename)[0] + '.ini'

        self._ini = configparser.ConfigParser()

        # Load ini file, if available
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
        """ Returns the name of this profile as ``str``. """
        return self._name

    @property
    def timestamp(self):
        """ Returns the timestamp when this profile was recorded. The timestamp
        is timezone aware.
        """
        return self._timestamp

    @property
    def overload(self):
        """ Returns the overload configured when this profile was recorded. The
        unit of this value is N (Newton).
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
    def samples(self):
        """ Returns the samples. This is a pandas dataframe."""
        return self._samples

    def default_filename(self, suffix, extension='.csv'):
        head, tail = split(self._pnt_filename)
        return join(head, self.name + '_' + suffix + extension)

    def pnt_header_value(self, pnt_header_id):
        """ Return the value of the pnt header by its ID which is a string. """
        return self._pnt_header[pnt_header_id].value

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
        fallback value is provided and no marker is found, the fallback value
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

        Raises :exc:`KeyError` in case no such marker is found.

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

    @staticmethod
    def load(pnt_filename, ini_filename=None):
        """ Loads a pnt file and its corresponding ini file too.

        :param pnt_filename:
        :param ini_filename:
        :return: A new instance of the ``Profile`` class.
        """
        return Profile(pnt_filename, ini_filename)

    def save(self, ini_filename=None):
        """ Save markers of this profile in a INI file.

        :param ini_filename:
        :return:
        """
        filename = self.ini_filename
        if ini_filename:
            filename = ini_filename
        # Only write file if markers are present
        markers = self._ini.items('markers')
        if not markers:
            raise ValueError('Nothing to save, set some markers first')

        with open(filename, 'w') as f:
            log.info('Saving ini info of {} to file {}'.format(self, filename))
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
            filename = splitext(self.pnt_filename)[0] + '_samples.csv'
        log.info('Exporting samples of {} to {}'.format(self, filename))
        samples = self.samples
        if snowpack_only:
            samples = self.samples_within_snowpack()
        fmt = '%.{}f'.format(precision)
        samples.to_csv(filename, header=True, index=False, float_format=fmt)

    def export_meta(self, filename=None, include_pnt_header=False):
        if not filename:
            filename = splitext(self.pnt_filename)[0] + '_meta.csv'
        log.info('Exporting meta information of {} to {}'.format(self, filename))
        with open(filename, 'w') as f:
            writer = csv.writer(f)
            # CSV header
            writer.writerow(['key', 'value'])
            # Export important properties of profile
            writer.writerow(('name', self.name))
            writer.writerow(('pnt_file', self.pnt_filename))
            writer.writerow(('gps.coords.lat', self.latitude))
            writer.writerow(('gps.coords.long', self.longitude))
            writer.writerow(('gps.numsats', self.gps_numsats))
            writer.writerow(('gps.pdop', self.gps_pdop))
            writer.writerow(('smp.serial', self.smp_serial))
            writer.writerow(('smp.length', self.smp_length))
            # Export markers
            for k, v in self.markers:
                writer.writerow(('ini.marker.' + k, v))
            # Export pnt header entries
            if include_pnt_header:
                for pnt_id, (label, value, unit) in sorted(self.pnt_header.items()):
                    writer.writerow(['pnt.' + pnt_id, value])

    @property
    def max_force(self):
        """ Return the maximum force value of all samples of this profile. """
        return self.samples.force.max()

    def samples_within_distance(self, begin=None, end=None, relativize=False):
        """Return samples which within a range.

        :param begin: Start of distance of interest. When ``None``,
            start of Profile is used.
        :param end: End of distance of interest. When ``None``, end of
            the Profile is used.
        :param relativize: Default set to ``False``. When set
            to ``True``, the distance in the samples returned starts
            with 0.
        :return: Samples within the range.
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
        try:
            s = self.marker('surface')
            g = self.marker('ground')
            return self.samples_within_distance(s, g, relativize)
        except KeyError as e:
            raise KeyError('Required marker missing in {}. Error: {}'.format(self, str(e)))

    def detect_surface(self):
        surface = detect_surface(self.samples.values)
        self.set_marker('surface', surface)
        return surface

    def detect_ground(self):
        ground = detect_ground(self.samples.values, self.overload)
        self.set_marker('ground', ground)
        return ground

    def model_shotnoise(self, save_to_file=False, filename_suffix='shotnoise'):
        sn = model_shotnoise(self.samples)
        sn.to_csv(self.default_filename(suffix=filename_suffix), index=False)
        return sn

    def model_ssa(self, save_to_file=False, filename_suffix='ssa'):
        ssa = model_ssa_and_density(self.samples)
        ssa.to_csv(self.default_filename(filename_suffix), index=False)
        return ssa

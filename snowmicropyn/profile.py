import configparser
import csv
import logging
import pathlib
from datetime import datetime

import pandas as pd
import pytz
from pandas import np as np

from . import windowing
from . import __version__, githash
from . import detection
from . import loewe2012
from . import proksch2015
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

    def __init__(self, pnt_file, name=None):
        self._pnt_file = pathlib.Path(pnt_file)
        # Load pnt file, returns header (dict) and raw samples
        self._pnt_header, pnt_samples = Pnt.load(self._pnt_file)

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
        if abs(self._longitude) > 180:
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

        self._smp_serial = str(self.pnt_header_value(Pnt.Header.SMP_SERIAL))
        self._smp_firmware = str(self.pnt_header_value(Pnt.Header.SMP_FIRMWARE))
        self._smp_length = self.pnt_header_value(Pnt.Header.SMP_LENGTH)
        self._smp_tipdiameter = self.pnt_header_value(Pnt.Header.SMP_TIPDIAMETER)
        self._gps_pdop = self.pnt_header_value(Pnt.Header.GPS_PDOP)
        self._gps_numsats = self.pnt_header_value(Pnt.Header.GPS_NUMSATS)
        self._amplifier_range = self.pnt_header_value(Pnt.Header.AMPLIFIER_RANGE)
        self._amplifier_serial = self.pnt_header_value(Pnt.Header.AMPLIFIER_SERIAL)
        self._sensor_serial = self.pnt_header_value(Pnt.Header.SENSOR_SERIAL)
        self._sensor_sensivity = self.pnt_header_value(Pnt.Header.SENSOR_SENSITIVITIY)

        # Create a pandas dataframe with distance and force
        distance_arr = np.arange(0, self._samples_count) * self._spatial_resolution
        factor = self.pnt_header_value(Pnt.Header.SAMPLES_CONVFACTOR_FORCE)
        force_arr = np.asarray(pnt_samples) * factor
        stacked = np.column_stack([distance_arr, force_arr])
        self._samples = pd.DataFrame(stacked, columns=('distance', 'force'))

        self._ini = configparser.ConfigParser()

        # Look out for corresponding ini file

        self._ini_file = self._pnt_file.with_suffix('.ini')
        if self._ini_file.exists():
            log.info('Reading ini file {} for {}'.format(self._ini_file, self))
            self._ini.read(self._ini_file)

        # Ensure a section called 'markers' does exist
        if not self._ini.has_section('markers'):
            self._ini.add_section('markers')

        # Check for invalid values (non floats) in 'markers' section
        for k, v in self._ini.items('markers'):
            try:
                float(v)
                log.info('Marker: {}={}'.format(k, v))
            except ValueError:
                log.warning(
                    'Ignoring value {} for marker {}, not float value'.format(repr(v), repr(k)))
                self._ini.remove_option('markers', k)

    def __str__(self):
        length = self.recording_length
        return 'Profile(name={}, {:.3f} mm, {} samples)'.format(repr(self.name), length, len(self))

    def __len__(self):
        return len(self.samples.distance)

    @property
    def name(self):
        """ Name of this profile. Can be specified when profile is loaded or,
        by default, "filename" header entry of the pnt file is used. """
        return self._name

    @property
    def pnt_file(self):
        """ ``pathlib.Path`` instance of the pnt file this data was loaded from. """
        return self._pnt_file

    @property
    def ini_file(self):
        """ ``pathlib.Path`` instance of the ini file in which markers are saved.

        This file may does not exist.
        """
        return self._ini_file

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
    def sensor_serial(self):
        """ Returns the serial number of the force sensor of the SnowMicroPen
        used.
        """
        return self._sensor_serial

    @property
    def sensor_sensitivity(self):
        """ Returns the sensitivity of SnowMicroPen's force sensor. The unit of
        this value is µC/N.
        """
        return self._sensor_sensivity

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
        decimal format as a tuple (``(float, float)``) or ``None`` when
        coordinates are not available.

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

    @property
    def markers(self):
        """ Returns all markers on the profile (a dictionary).

        The dictionary keys are of type string, the values are floats. When no
        markers are set, the returned dictionary is empty.
        """
        return {k: float(v) for k, v in self._ini.items('markers')}

    # configparser._UNSET as default value for fallback is required to enable
    # None as a valid value to pass
    def marker(self, label, fallback=configparser._UNSET):
        """ Returns the value of a marker as a ``float``. In case a fallback
        value is provided and no marker is present, the fallback value is
        returned. It's recommended to pass a ``float`` fallback value. ``None``
        is a valid fallback value.

        :param label: Name of the marker requested.
        :param fallback: Fallback value returned in case no marker exists for
               the provided name.
        """
        try:
            # Always return floats
            return self._ini.getfloat('markers', label, fallback=fallback)
        except configparser.NoOptionError:
            raise KeyError('No marker named {} available'.format(label))

    def set_marker(self, label, value):
        """ Sets a marker.

        When passing ``None``as value, the marker is removed. Otherwise, the
        provided value is converted into a ``float``. The method raises
        :exc:`ValueError` in case this fails.

        :param label: Name of the marker.
        :param value: Value for the marker. Passing a ``float`` is recommended.
        """
        if value is None:
            try:
                float(self._ini.remove_option('markers', label))
            except configparser.NoOptionError:
                raise KeyError('No marker named {} available'.format(label))
        else:
            value = float(value)
            self._ini.set('markers', label, str(value))

    def remove_marker(self, label):
        """ Remove a marker.

        Equivalent to ``set_marker(label, None)``.
        """
        return self.set_marker(label, None)

    @property
    def recording_length(self):
        first = self.samples.distance.iloc[0]
        last = self.samples.distance.iloc[-1]
        return last - first

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
    def load(pnt_file, name=None):
        """ Loads a profile from a pnt file.

        This static method loads a pnt file and also its ini file in case its
        available. You can pass a name for the profile if you like. When omitted
        (passing ``None``), the content of the pnt header field
        (:const:`Pnt.Header.FILENAME`) is used.

        :param pnt_file: A `path-like object`_.
        :param name: Name of the profile.

        .. _path-like object: https://docs.python.org/3/glossary.html#term-path-like-object
        """
        return Profile(pnt_file, name)

    def save(self):
        """ Save markers of this profile to a ini file.

        .. warning::
           An already existing ini file is overwritten with no warning.

        When no markers are set on the profile, the resulting file will be
        empty.
        """
        with self._ini_file.open('w') as f:
            log.info('Saving ini info of {} to file {}'.format(self, self._ini_file))
            self._ini.write(f)

    def export_samples(self, file=None, precision=4, snowpack_only=False):
        """ Export the samples of this profile into a CSV file.

        When parameter ``file`` is not provided, the default name is used which
        is same as the pnt file from which the profile was loaded with a suffix
        `_samples` and the `csv` extension.

        :param file: A `path-like object`_.
        :param precision: Precision (number of digits after comma) of the
               values. Default value is 4.
        :param snowpack_only: In case set to true, only samples within the
               markers surface and ground are exported.

        .. _path-like object: https://docs.python.org/3/glossary.html#term-path-like-object
        """
        if file:
            file = pathlib.Path(file)
        else:
            file = self._pnt_file.with_name(self._pnt_file.stem + '_samples').with_suffix('.csv')

        log.info('Exporting samples of {} to {}'.format(self, file))
        samples = self.samples
        if snowpack_only:
            samples = self.samples_within_snowpack()
        fmt = '%.{}f'.format(precision)
        with file.open('w') as f:
            # Write version and git hash as comment for tracking
            crumbs = '# Exported by snowmicropyn {} (git hash {})\n'.format(__version__, githash())
            f.write(crumbs)
            with_units = {
                'distance': 'distance [mm]',
                'force': 'force [N]',
            }
            data = samples.rename(columns=with_units)
            data.to_csv(f, header=True, index=False, float_format=fmt)
        return file

    def export_meta(self, file=None, include_pnt_header=False):
        """ Export meta information of this profile into a CSV file.

        When parameter ``file`` is not provided, the default name is used which
        is same as the pnt file from which the profile was loaded with a suffix
        `_meta` and the `csv` extension.

        :param file: A `Path-like object<https://docs.python.org/3/glossary.html#term-path-like-object>`_.
        :param include_pnt_header: When ``True``, raw pnt header fields are
               included too.
        """
        if file:
            file = pathlib.Path(file)
        else:
            file = self._pnt_file.with_name(self._pnt_file.stem + '_meta').with_suffix('.csv')
        log.info('Exporting meta information of {} to {}'.format(self, file))
        with file.open('w') as f:
            writer = csv.writer(f)
            # Write version and git hash as comment for tracking
            crumbs = '# Exported by snowmicropyn {} (git hash {})\n'.format(__version__, githash())
            f.write(crumbs)
            # CSV header
            writer.writerow(['key', 'value'])
            # Export important properties of profile
            writer.writerow(('recording_name', self.name))
            writer.writerow(('recording_pntfile', str(self.pnt_file)))
            writer.writerow(('recording_timestamp', str(self.timestamp.isoformat() if self.timestamp else None)))
            writer.writerow(('recording_latitude', self._latitude))
            writer.writerow(('recording_longitude', self._longitude))
            writer.writerow(('recording_length', self.recording_length))
            writer.writerow(('recording_samplecount', len(self)))
            writer.writerow(('recording_spatialresolution', self.spatial_resolution))
            writer.writerow(('recording_overload', self.overload))
            writer.writerow(('recording_speed', self.speed))
            writer.writerow(('smp_serial', self.smp_serial))
            writer.writerow(('smp_firmware', self.smp_firmware))
            writer.writerow(('smp_maxlength', self.smp_length))
            writer.writerow(('smp_tipdiameter', self.smp_tipdiameter))
            writer.writerow(('smp_sensor_serial', self.sensor_serial))
            writer.writerow(('smp_sensor_sensitivity', self.sensor_sensitivity))
            writer.writerow(('smp_amplifier_serial', self.amplifier_serial))
            # Export markers
            for k, v in self.markers.items():
                writer.writerow(('marker_' + k, v))
            # Export pnt header entries
            if include_pnt_header:
                for header_id, (value, unit) in self._pnt_header.items():
                    writer.writerow(['pnt_' + header_id.name, str(value)])
        return file

    def export_derivatives(self, file=None, snowpack_only=True, window_size=windowing.DEFAULT_WINDOW, overlap_factor=windowing.DEFAULT_WINDOW_OVERLAP, precision=4):
        if file:
            file = pathlib.Path(file)
        else:
            file = self._pnt_file.with_name(self._pnt_file.stem + '_derivatives').with_suffix('.csv')

        samples = self.samples
        if snowpack_only:
            samples = self.samples_within_snowpack()

        log.info('Calculating derivatives by Löwe 2012')
        loewe2012_df = loewe2012.calc(samples, window_size, overlap_factor)

        log.info('Calculating derivatives by Proksch 2015')
        proksch_data = proksch2015.calc_from_loewe2012(loewe2012_df)

        derivatives = loewe2012_df.merge(proksch_data)

        # Add units in label for export
        with_units = {
            'distance': 'distance [mm]',
            'force_median': 'force_median [N]',
            'L2012_lambda': 'L2012_lambda [1/mm]',
            'L2012_f0': 'L2012_f0 [N]',
            'L2012_delta': 'L2012_delta [mm]',
            'L2012_L': 'L2012_L [mm]',
            'P2015_ssa': 'P2015_ssa [m^2/m^3]',
            'P2015_density': 'P2015_density [kg/m^3]'
        }
        derivatives = derivatives.rename(columns=with_units)

        fmt = '%.{}f'.format(precision)
        derivatives.to_csv(file, header=True, index=False, float_format=fmt)
        return file

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
        s = self.marker('surface', fallback=self.samples.distance.iloc[0])
        g = self.marker('ground', fallback=self.samples.distance.iloc[-1])
        return self.samples_within_distance(s, g, relativize)

    def detect_surface(self):
        """ Convenience method to detect the surface. This also sets the marker
        called "surface". """
        surface = detection.detect_surface(self)
        self.set_marker('surface', surface)
        return surface

    def detect_ground(self):
        """ Convenience method to detect the ground. This also sets the marker
        called "surface". """
        ground = detection.detect_ground(self)
        self.set_marker('ground', ground)
        return ground

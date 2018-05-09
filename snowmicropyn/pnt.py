import logging
import pathlib
import string
import struct
from collections import namedtuple
from enum import Enum

log = logging.getLogger(__name__)

pnt_header_entry = namedtuple('pnt_header_field', ['label', 'value', 'unit'])


# noinspection PyClassHasNoInit
class Pnt:
    """ Low level pnt loading functionality.

    An example::

        from snowmicropyn import Pnt

        header, raw_samples = Pnt.load('S31M0067.pnt')

        print(header[Pnt.Header.TIMESTAMP_YEAR].value)
        print(raw_samples[2000:2005])

    This may prints lines like ``2017`` and ``(40, 41, 42, 43, 42)``.
    """
    class Header(Enum):
        """ Identifiers for pnt header entries """

        #: Version of firmware of SnowMicroPen used
        FIRMWARE = 'smp.firmware'
        #: Number of samples
        SAMPLES_COUNT = 'samples.count'
        #: Spatial resolution of distance
        SAMPLES_SPATIALRES = 'samples.spatialres'
        #: Conversion factor of force
        SAMPLES_CONVFACTOR_FORCE = 'samples.conv.force'
        #: Conversion factor of pressure
        SAMPLES_CONVFACTOR_PRESSURE = 'samples.conv.pressure'
        #: Offset value for force values. **NOT IN USE**.
        SAMPLES_OFFSET_FORCE = 'samples.force.offset'
        #: Timestamp's year
        TIMESTAMP_YEAR = 'timestamp.year'
        #: Timestamp's month
        TIMESTAMP_MONTH = 'timestamp.month'
        #: Timestamp's day
        TIMESTAMP_DAY = 'timestamp.day'
        #: Timestamp's hour
        TIMESTAMP_HOUR = 'timestamp.hour'
        #: Timestamp's minute
        TIMESTAMP_MINUTE = 'timestamp.minute'
        #: Timestamp's second
        TIMESTAMP_SECOND = 'timestamp.second'
        #: CH1903 coordinate X. **NOT IN USE**.
        GPS_CH1903_X = 'gps.ch1903.x'
        #: CH1903 coordinate Y. **NOT IN USE**.
        GPS_CH1903_Y = 'gps.ch1903.y'
        #: CH1903 coordinate Z. **NOT IN USE**.
        GPS_CH1903_Z = 'gps.ch1903.z'
        #: Voltage of battery. **NOT IN USE**.
        BATTERY_VOLTAGE = 'battery.voltage'
        #: Penetration speed
        SAMPLES_SPEED = 'samples.speed'
        #: Loop size... **NOT IN USE**.
        LOOPSIZE = 'loopsize'
        #: Waypoints... **NOT IN USE**.
        WAYPOINTS = 'waypoints'
        #: cal start... **NOT IN USE**.
        CAL_START = 'cal.start'
        #: cal end... **NOT IN USE**.
        CAL_END = 'cal.end'
        #: Comment length. **NOT IN USE**.
        COMMENT_LENGTH = 'comment.length'
        #: Comment content. **NOT IN USE**.
        COMMENT_CONTENT = 'comment.content'
        #: Filename of recording
        FILENAME = 'filename'
        #: WGS 84 latitude
        GPS_WGS84_LATITUDE = 'gps.wgs84.latitude'
        #: WGS 84 longitude
        GPS_WGS84_LONGITUDE = 'gps.wgs84.longitude'
        #: WGS84 altitude. **NOT IN USE**.
        GPS_WGS84_HEIGHT = 'gps.wgs84.height'
        #: Positional DOP, geometric dilution of precision
        GPS_PDOP = 'gps.pdop'
        #: Part of WGS 84 coords: N for northern hemisphere, S for southern hemisphere
        GPS_WGS84_NORTH = 'gps.wgs84.north'
        #: Part of WGS 84 coords: E eastern, W for western.
        GPS_WGS84_EAST = 'gps.wgs84.east'
        #: Number of satellites when location was determined. **NOT IN USE**.
        GPS_NUMSATS = 'gps.numsats'
        #: GPS fixmode value
        GPS_FIXMODE = 'gps.fixmode'
        #: GPS state
        GPS_STATE = 'gps.state'
        #: Reserved space 1
        RESERVED1 = 'reserved.1'
        #: Local X... **NOT IN USE**.
        LOCAL_X = 'local.x'
        #: Local Y... **NOT IN USE**.
        LOCAL_Y = 'local.y'
        #: Local Z... **NOT IN USE**.
        LOCAL_Z = 'local.z'
        #: Local theta. **NOT IN USE**.
        LOCAL_THETA = 'local.theta'
        #: Reserved space 2
        RESERVED2 = 'reserved.2'
        #: Number of force samples
        SAMPLES_COUNT_FORCE = 'samples.force.count'
        #: Number of termperature samples. **NOT IN USE**.
        SAMPLES_COUNT_TEMP = 'samples.temp.count'
        #: Sensor range
        SENSOR_RANGE = 'sensor.range'
        #: Amplifier range
        AMPLIFIER_RANGE = 'amplifier.range'
        #: Sensor sensitivity value
        SENSOR_SENSITIVITIY = 'sensor.sensitivity'
        #: Sensor temperature offset value
        SENSOR_TEMPOFFSET = 'sensor.tempoffset'
        #: Hand operation. **NOT IN USE**.
        SENSOR_HANDOP = 'sensor.handop'
        #: Diameter of SnowMicroPen's tip
        TIP_DIAMETER = 'smp.diameter'
        #: Overload value
        SENSOR_OVERLOAD = 'sensor.overload'
        #: Sensor type value
        SENSOR_TYPE = 'sensor.type'
        #: Amplifier type value
        AMPLIFIER_TYPE = 'amplifier.type'
        #: SnowMicroPen's serial number
        SMP_SERIAL = 'smp.serial'
        #: SnowMicroPen's length
        SMP_LENGTH = 'smp.length'
        #: Reserved space 3
        RESERVED3 = 'reserved.3'
        #: Serial number of sensor
        SENSOR_SERIAL = 'sensor.serial'
        #: Serial number of amplifier
        AMPLIFIER_SERIAL = 'amplifier.serial'
        #: Reserved space 4
        RESERVED4 = 'reserved.4'

    _PNT_HEADER = [
        # Offset (from start of header), format for struct.unpack, id, label, unit
        (0, '>h', Header.FIRMWARE, 'Firmware Version', None),
        (2, '>i', Header.SAMPLES_COUNT, 'Total of Samples', None),
        (6, '>f', Header.SAMPLES_SPATIALRES, 'Distance', 'mm'),
        (10, '>f', Header.SAMPLES_CONVFACTOR_FORCE, 'Conversion Factor Force', 'N/mV'),
        (14, '>f', Header.SAMPLES_CONVFACTOR_PRESSURE, 'Conversion Factor Pressure ', 'N/bar'),
        (18, '>h', Header.SAMPLES_OFFSET_FORCE, 'Offset', 'N'),
        (20, '>h', Header.TIMESTAMP_YEAR, 'Year', None),
        (22, '>h', Header.TIMESTAMP_MONTH, 'Month', None),
        (24, '>h', Header.TIMESTAMP_DAY, 'Day', None),
        (26, '>h', Header.TIMESTAMP_HOUR, 'Hour', None),
        (28, '>h', Header.TIMESTAMP_MINUTE, 'Min', None),
        (30, '>h', Header.TIMESTAMP_SECOND, 'Sec', None),
        (32, '>d', Header.GPS_CH1903_X, 'Coordinate CH1903 X', 'deg'),
        (40, '>d', Header.GPS_CH1903_Y, 'Coordinate CH1903 Y', 'deg'),
        (48, '>d', Header.GPS_CH1903_Z, 'Coordinate CH1903 Z', 'm'),
        (56, '>d', Header.BATTERY_VOLTAGE, 'Battery Voltage', 'V'),
        (64, '>f', Header.SAMPLES_SPEED, 'Average Speed', 'mm/s'),
        (68, '>l', Header.LOOPSIZE, 'Loop Size', None),
        (72, '>10l', Header.WAYPOINTS, 'Waypoints', None),
        (112, '>10h', Header.CAL_START, 'Calstart', None),
        (132, '>10h', Header.CAL_END, 'Calend', None),
        (152, '>h', Header.COMMENT_LENGTH, 'Comment Length', None),
        (154, '102s', Header.COMMENT_CONTENT, 'Comment', None),
        (256, '8s', Header.FILENAME, 'Filename', None),
        (264, '>f', Header.GPS_WGS84_LATITUDE, 'Latitude', 'deg'),
        (268, '>f', Header.GPS_WGS84_LONGITUDE, 'Longitude', 'deg'),
        (272, '>f', Header.GPS_WGS84_HEIGHT, 'Height', 'cm'),
        (276, '>f', Header.GPS_PDOP, 'GPS PDOP', None),
        (280, '>c', Header.GPS_WGS84_NORTH, 'GPS North', None),
        (281, '>c', Header.GPS_WGS84_EAST, 'GPS East', None),
        (282, '>h', Header.GPS_NUMSATS, 'GPS N° Satellites', None),
        (284, '>h', Header.GPS_FIXMODE, 'GPS Fix Mode', None),
        (286, '>c', Header.GPS_STATE, 'GPS State', None),
        (287, 'B', Header.RESERVED1, 'reserved 1', None),
        (288, '>h', Header.LOCAL_X, 'Local X', 'deg'),
        (290, '>h', Header.LOCAL_Y, 'Local Y', 'deg'),
        (292, '>h', Header.LOCAL_Z, 'Local Z', 'm'),
        (294, '>h', Header.LOCAL_THETA, 'Local Theta', 'deg'),
        (296, '62B', Header.RESERVED2, 'Reserved 2', None),
        (358, '>l', Header.SAMPLES_COUNT_FORCE, 'N° Force Samples', None),
        (362, '>l', Header.SAMPLES_COUNT_TEMP, 'N° Temperature Samples', None),
        (366, '>h', Header.SENSOR_RANGE, 'Sensor Range', 'pC'),
        (368, '>h', Header.AMPLIFIER_RANGE, 'Amp Range', 'pC'),
        (370, '>h', Header.SENSOR_SENSITIVITIY, 'Sensitivity', 'pC/N'),
        (372, '>h', Header.SENSOR_TEMPOFFSET, 'Temp Offset', '°C'),
        (374, '>h', Header.SENSOR_HANDOP, 'Hand Operation', None),
        (376, '>l', Header.TIP_DIAMETER, 'Tip Diameter', 'µm'),
        (380, '>h', Header.SENSOR_OVERLOAD, 'Overload', 'N'),
        (382, '>c', Header.SENSOR_TYPE, 'Sensor Type', None),
        (383, '>c', Header.AMPLIFIER_TYPE, 'Amplifier Type', None),
        (384, '>h', Header.SMP_SERIAL, 'SMP Serial', None),
        (386, '>h', Header.SMP_LENGTH, 'SMP Length', 'mm'),
        (388, '4B', Header.RESERVED3, 'Reserved 3', None),
        (392, '20s', Header.SENSOR_SERIAL, 'Sensor Serial', None),
        (412, '20s', Header.AMPLIFIER_SERIAL, 'Amplifier Serial', None),
        (432, '80B', Header.RESERVED4, 'Reserved 4 ', None),
    ]

    @staticmethod
    def load(file):
        """ Loads the raw data of a pnt file

        This is the low level method used by class :class:`snowmicropyn.Profile`
        to load the content of a pnt file. The method returns a tuple: A header
        (dict) and the raw measurement values (tuple). The header dictionary
        contains the header entries. Each entry has a label (``.label``), a
        unit (``.unit``) and a actual value (``.value``). Each entry can be
        ``None``. Mostly this is the case for unit.

        :param file: Path-like object
        """
        file = pathlib.Path(file)
        log.info('Reading pnt file {}'.format(file))
        with file.open('rb') as f:
            raw = f.read()

        header = {}
        try:
            for offset, fmt, pnt_id, label, unit in Pnt._PNT_HEADER:
                value = struct.unpack_from(fmt, raw, offset)
                if len(value) == 1:
                    value = value[0]
                if 's' in fmt or 'c' in fmt:
                    value = value.decode('utf-8', errors='ignore')
                    # Drop non printable chars
                    value = ''.join([x if x in string.printable else '' for x in value])
                log.debug('Read header entry {} = {}{}'.format(
                    pnt_id, repr(value), ' ' + unit if unit else '')
                )
                header[pnt_id] = pnt_header_entry(label, value, unit)

            count = header[Pnt.Header.SAMPLES_COUNT_FORCE].value
            raw_samples = struct.unpack_from('>{}h'.format(count), raw, offset=512)
            log.info('Read {} raw samples from file {}'.format(len(raw_samples), file))
        except struct.error as e:
            raise ValueError('Failed to load pnt file. Message: ' + str(e))

        return header, raw_samples

import logging
import pathlib
import string
import struct
from collections import namedtuple
from enum import Enum

log = logging.getLogger(__name__)

pnt_header_entry = namedtuple('pnt_header_field', ['value', 'unit'])


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
        SMP_FIRMWARE = 'smp.firmware'
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
        #: Way points... **NOT IN USE**.
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
        #: Part of WGS 84 coordinates: N for northern hemisphere, S for southern hemisphere
        GPS_WGS84_NORTH = 'gps.wgs84.north'
        #: Part of WGS 84 coordinates: E eastern, W for western.
        GPS_WGS84_EAST = 'gps.wgs84.east'
        #: Number of satellites when location was determined. **NOT IN USE**.
        GPS_NUMSATS = 'gps.numsats'
        #: GPS fix mode value
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
        #: Number of temperature samples. **NOT IN USE**.
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
        SMP_TIPDIAMETER = 'smp.diameter'
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
        # Offset (from start of header), format for struct.unpack, id, unit
        (0, '>h', Header.SMP_FIRMWARE, None),
        (2, '>i', Header.SAMPLES_COUNT, None),
        (6, '>f', Header.SAMPLES_SPATIALRES, 'mm'),
        (10, '>f', Header.SAMPLES_CONVFACTOR_FORCE, 'N/mV'),
        (14, '>f', Header.SAMPLES_CONVFACTOR_PRESSURE, 'N/bar'),
        (18, '>h', Header.SAMPLES_OFFSET_FORCE, 'N'),
        (20, '>h', Header.TIMESTAMP_YEAR, None),
        (22, '>h', Header.TIMESTAMP_MONTH, None),
        (24, '>h', Header.TIMESTAMP_DAY, None),
        (26, '>h', Header.TIMESTAMP_HOUR, None),
        (28, '>h', Header.TIMESTAMP_MINUTE, None),
        (30, '>h', Header.TIMESTAMP_SECOND, None),
        (32, '>d', Header.GPS_CH1903_X, None),
        (40, '>d', Header.GPS_CH1903_Y, None),
        (48, '>d', Header.GPS_CH1903_Z, 'm'),
        (56, '>d', Header.BATTERY_VOLTAGE, 'V'),
        (64, '>f', Header.SAMPLES_SPEED, 'mm/s'),
        (68, '>l', Header.LOOPSIZE, None),
        (72, '>10l', Header.WAYPOINTS, None),
        (112, '>10h', Header.CAL_START, None),
        (132, '>10h', Header.CAL_END, None),
        (152, '>h', Header.COMMENT_LENGTH, None),
        (154, '102s', Header.COMMENT_CONTENT, None),
        (256, '8s', Header.FILENAME, None),
        (264, '>f', Header.GPS_WGS84_LATITUDE, 'deg'),
        (268, '>f', Header.GPS_WGS84_LONGITUDE, 'deg'),
        (272, '>f', Header.GPS_WGS84_HEIGHT, 'cm'),
        (276, '>f', Header.GPS_PDOP, None),
        (280, '>c', Header.GPS_WGS84_NORTH, None),
        (281, '>c', Header.GPS_WGS84_EAST, None),
        (282, '>h', Header.GPS_NUMSATS, None),
        (284, '>h', Header.GPS_FIXMODE, None),
        (286, '>c', Header.GPS_STATE, None),
        (287, 'B', Header.RESERVED1, None),
        (288, '>h', Header.LOCAL_X, 'deg'),
        (290, '>h', Header.LOCAL_Y, 'deg'),
        (292, '>h', Header.LOCAL_Z, 'm'),
        (294, '>h', Header.LOCAL_THETA, 'deg'),
        (296, '62B', Header.RESERVED2, None),
        (358, '>l', Header.SAMPLES_COUNT_FORCE, None),
        (362, '>l', Header.SAMPLES_COUNT_TEMP, None),
        (366, '>h', Header.SENSOR_RANGE, 'pC'),
        (368, '>h', Header.AMPLIFIER_RANGE, 'pC'),
        (370, '>h', Header.SENSOR_SENSITIVITIY, 'pC/N'),
        (372, '>h', Header.SENSOR_TEMPOFFSET, '°C'),
        (374, '>h', Header.SENSOR_HANDOP, None),
        (376, '>l', Header.SMP_TIPDIAMETER, 'µm'),
        (380, '>h', Header.SENSOR_OVERLOAD, 'N'),
        (382, '>c', Header.SENSOR_TYPE, None),
        (383, '>c', Header.AMPLIFIER_TYPE, None),
        (384, '>h', Header.SMP_SERIAL, None),
        (386, '>h', Header.SMP_LENGTH, 'mm'),
        (388, '4B', Header.RESERVED3, None),
        (392, '20s', Header.SENSOR_SERIAL, None),
        (412, '20s', Header.AMPLIFIER_SERIAL, None),
        (432, '80B', Header.RESERVED4, None),
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
            for offset, fmt, pnt_id, unit in Pnt._PNT_HEADER:
                value = struct.unpack_from(fmt, raw, offset)
                if len(value) == 1:
                    value = value[0]
                if 's' in fmt or 'c' in fmt:
                    value = value.decode('utf-8', errors='ignore')
                    # Drop non-printable chars
                    value = ''.join([x if x in string.printable else '' for x in value])
                unit_label = ' ' + unit if unit else ''
                log.info('Read header entry {} = {}{}'.format(pnt_id, repr(value), unit_label))
                header[pnt_id] = pnt_header_entry(value, unit)

            count = header[Pnt.Header.SAMPLES_COUNT_FORCE].value
            raw_samples = struct.unpack_from('>{}h'.format(count), raw, offset=512)
            log.info('Read {} raw samples from file {}'.format(len(raw_samples), file))
        except struct.error as e:
            log.exception(e)
            raise ValueError('Failed to load pnt file. Message: ' + str(e))

        return header, raw_samples

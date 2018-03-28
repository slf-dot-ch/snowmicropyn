# -*- coding: utf-8 -*-

import logging
import string
import struct
from collections import namedtuple

import numpy as np

log = logging.getLogger(__name__)

pnt_header_field = namedtuple('pnt_header_field', ['label', 'value', 'unit'])


# noinspection PyClassHasNoInit
class Pnt:
    VERSION = 'version'
    SAMPLES_COUNT = 'samples.count'
    SAMPLES_SPATIALRES = 'samples.spatialres'
    SAMPLES_CONVFACTOR_FORCE = 'samples.conv.force'
    SAMPLES_CONVFACTOR_PRESSURE = 'samples.conv.pressure'
    SAMPLES_OFFSET_FORCE = 'samples.force.offset'
    TIMESTAMP_YEAR = 'timestamp.year'
    TIMESTAMP_MONTH = 'timestamp.month'
    TIMESTAMP_DAY = 'timestamp.day'
    TIMESTAMP_HOUR = 'timestamp.hour'
    TIMESTAMP_MINUTE = 'timestamp.minute'
    TIMESTAMP_SECOND = 'timestamp.second'
    GPS_CH1903_X = 'gps.ch1903.x'
    GPS_CH1903_Y = 'gps.ch1903.y'
    GPS_CH1903_Z = 'gps.ch1903.z'
    BATTERY_VOLTAGE = 'battery.voltage'
    SAMPLES_SPEED = 'samples.speed'
    LOOPSIZE = 'loopsize'
    WAYPOINTS = 'waypoints'
    CAL_START = 'cal.start'
    CAL_END = 'cal.end'
    COMMENT_LENGTH = 'comment.length'
    COMMENT_CONTENT = 'comment.content'
    FILENAME = 'filename'
    GPS_WGS84_LATITUDE = 'gps.wgs84.latitude'
    GPS_WGS84_LONGITUDE = 'gps.wgs84.longitude'
    GPS_WGS84_HEIGHT = 'gps.wgs84.height'
    GPS_PDOP = 'gps.pdop'
    GPS_WGS84_NORTH = 'gps.wgs84.north'
    GPS_WGS84_EAST = 'gps.wgs84.east'
    GPS_NUMSATS = 'gps.numsats'
    GPS_FIXMODE = 'gps.fixmode'
    GPS_STATE = 'gps.state'
    # RESERVED1 = 'reserved.1'
    LOCAL_X = 'local.x'
    LOCAL_Y = 'local.y'
    LOCAL_Z = 'local.z'
    LOCAL_THETA = 'local.theta'
    # RESERVED2 = 'reserved.2'
    SAMPLES_COUNT_FORCE = 'samples.force.count'
    SAMPLES_COUNT_TEMP = 'samples.temp.count'
    SENSOR_RANGE = 'sensor.range'
    AMPLIFIER_RANGE = 'amplifier.range'
    SENSOR_SENSITIVITIY = 'sensor.sensitivity'
    SENSOR_TEMPOFFSET = 'sensor.tempoffset'
    SENSOR_HANDOP = 'sensor.handop'
    SENSOR_DIAMETER = 'sensor.diameter'
    SENSOR_OVERLOAD = 'sensor.overload'
    SENSOR_TYPE = 'sensor.type'
    AMPLIFIER_TYPE = 'amplifier.type'
    SMP_SERIAL = 'smp.serial'
    SMP_MAXLENGTH = 'smp.maxlength'
    # RESERVED3 = 'reserved.3'
    SENSOR_SERIAL = 'sensor.serial'
    AMPLIFIER_SERIAL = 'amplifier.serial'
    # RESERVED4 = 'reserved.4'

    _PNT_HEADER = [
        # offset (from start of header), format (struct.unpack), id, label, unit
        (0, '>h', VERSION, 'Firmware Version', None),
        (2, '>i', SAMPLES_COUNT, 'Total of Samples', None),
        (6, '>f', SAMPLES_SPATIALRES, 'Distance', 'mm'),
        (10, '>f', SAMPLES_CONVFACTOR_FORCE, 'Conversion Factor Force', 'N/mV'),
        (14, '>f', SAMPLES_CONVFACTOR_PRESSURE, 'Conversion Factor Pressure ', 'N/bar'),
        (18, '>h', SAMPLES_OFFSET_FORCE, 'Offset', 'N'),
        (20, '>h', TIMESTAMP_YEAR, 'Year', None),
        (22, '>h', TIMESTAMP_MONTH, 'Month', None),
        (24, '>h', TIMESTAMP_DAY, 'Day', None),
        (26, '>h', TIMESTAMP_HOUR, 'Hour', None),
        (28, '>h', TIMESTAMP_MINUTE, 'Min', None),
        (30, '>h', TIMESTAMP_SECOND, 'Sec', None),
        (32, '>d', GPS_CH1903_X, 'Coordinate CH1903 X', 'deg'),
        (40, '>d', GPS_CH1903_Y, 'Coordinate CH1903 Y', 'deg'),
        (48, '>d', GPS_CH1903_Z, 'Coordinate CH1903 Z', 'm'),
        (56, '>d', BATTERY_VOLTAGE, 'Battery Voltage', 'V'),
        (64, '>f', SAMPLES_SPEED, 'Average Speed', 'mm/s'),
        (68, '>l', LOOPSIZE, 'Loop Size', None),
        (72, '>10l', WAYPOINTS, 'Waypoints', None),
        (112, '>10h', CAL_START, 'Calstart', None),
        (132, '>10h', CAL_END, 'Calend', None),
        (152, '>h', COMMENT_LENGTH, 'Comment Length', None),
        (154, '102s', COMMENT_CONTENT, 'Comment', None),
        (256, '8s', FILENAME, 'Filename', None),
        (264, '>f', GPS_WGS84_LATITUDE, 'Latitude', 'deg'),
        (268, '>f', GPS_WGS84_LONGITUDE, 'Longitude', 'deg'),
        (272, '>f', GPS_WGS84_HEIGHT, 'Height', 'cm'),
        (276, '>f', GPS_PDOP, 'GPS PDOP', None),
        (280, '>c', GPS_WGS84_NORTH, 'GPS North', None),
        (281, '>c', GPS_WGS84_EAST, 'GPS East', None),
        (282, '>h', GPS_NUMSATS, 'GPS N° Satellites', None),
        (284, '>h', GPS_FIXMODE, 'GPS Fix Mode', None),
        (286, '>c', GPS_STATE, 'GPS State', None),
        # (287, 'B', RESERVED1, 'reserved 1', None),
        (288, '>h', LOCAL_X, 'Local X', 'deg'),
        (290, '>h', LOCAL_Y, 'Local Y', 'deg'),
        (292, '>h', LOCAL_Z, 'Local Z', 'm'),
        (294, '>h', LOCAL_THETA, 'Local Theta', 'deg'),
        # (296, '62B', RESERVED2, 'Reserved 2', None),
        (358, '>l', SAMPLES_COUNT_FORCE, 'N° Force Samples', None),
        (362, '>l', SAMPLES_COUNT_TEMP, 'N° Temperature Samples', None),
        (366, '>h', SENSOR_RANGE, 'Sensor Range', 'pC'),
        (368, '>h', AMPLIFIER_RANGE, 'Amp Range', 'pC'),
        (370, '>h', SENSOR_SENSITIVITIY, 'Sensitivity', 'pC/N'),
        (372, '>h', SENSOR_TEMPOFFSET, 'Temp Offset', '°C'),
        (374, '>h', SENSOR_HANDOP, 'Hand Operation', None),
        (376, '>l', SENSOR_DIAMETER, 'Diameter', 'µm'),
        (380, '>h', SENSOR_OVERLOAD, 'Overload', 'N'),
        (382, '>c', SENSOR_TYPE, 'Sensor Type', None),
        (383, '>c', AMPLIFIER_TYPE, 'Amplifier Type', None),
        (384, '>h', SMP_SERIAL, 'SMP Serial', None),
        (386, '>h', SMP_MAXLENGTH, 'SMP Length', 'mm'),
        # (388, '4B', RESERVED3, 'Reserved 3', None),
        (392, '20s', SENSOR_SERIAL, 'Sensor Serial', None),
        (412, '20s', AMPLIFIER_SERIAL, 'Amplifier Serial', None),
        # (432, '80B', RESERVED4, 'Reserved 4 ', None),
    ]

    @staticmethod
    def load_pnt(filename):
        """Load the content of a binary pnt file

        The method loads a binary pnt file written by a SnowMicroPen.
        A pnt file consists of a header and samples. The header
        contains multiple fields storing meta information.

        The samples are the actual measurement values. The samples
        are returned as a ``numpy.mdarray`` with a shape of (<sample
        count>, 2).

        The content of the header is returned as a dictionary. It
        contains the header entries. Each entry has a label (``<entry
        instance>``.label), a unit (``<entry instance>``.unit) and a
        actual value (``<entry instance>``.value). Each property can
        be ``None``. Mostly this is true for the unit property.

        :param filename: File path of file name

        :return: A tuple containing the samples (``numpy.mdarray``)
        and a header ( ``dict``)
        """

        log.info('Reading pnt file {}'.format(filename))
        with open(filename, 'rb') as f:
            raw = f.read()

        header = {}
        try:
            for offset, fmt, pnt_id, label, unit in Pnt._PNT_HEADER:
                value = struct.unpack_from(fmt, raw, offset)
                if len(value) == 1:
                    value = value[0]
                # Drop non printable chars in string values
                if 's' in fmt or 'c' in fmt:
                    value = filter(lambda x: x in string.printable, value)
                log.debug('Read header entry {} = {}{}'.format(
                    pnt_id, repr(value), ' ' + unit if unit else '')
                )
                header[pnt_id] = pnt_header_field(label, value, unit)

            count = header[Pnt.SAMPLES_COUNT_FORCE].value
            samples = struct.unpack_from('>{}h'.format(count), raw, offset=512)
            log.info('Read {} samples from file {}'.format(len(samples), filename))
        except struct.error as e:
            raise ValueError('Failed to load pnt file. Message: ' + str(e))

        spatial_res = header[Pnt.SAMPLES_SPATIALRES].value
        conv_factor = header[Pnt.SAMPLES_CONVFACTOR_FORCE].value

        distances = np.arange(0, count) * spatial_res
        forces = np.asarray(samples) * conv_factor
        samples = np.column_stack([distances, forces])

        return samples, header

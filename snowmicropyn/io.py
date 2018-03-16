import matplotlib.pyplot as plt
import numpy
import struct


##########################################################
# Author:	Sascha Grimm
# Company:	SLF, Institute for Snow and Avalanche Research
##########################################################
# this file contents functions to create an object PNT that stores file name,raw data, header infos
# and meaurement data from a binary .pnt file. Run as script, the main function opens a file dialog
# where you can choose one or multiple files to be converted from binary to a readable .txt file
###########################################################

class Pnt(object):
    def __init__(self, filename):
        """Object Pnt contains raw data (binary), header infos (dict) and measurement data (array)"""
        self.filename = filename
        self.raw = self.getRaw()
        self.infos = None
        self.header, self.units = self.getHeader()
        self.data = self.getData()
        self.surface = 0.0
        self.ground = self.data[-1, 0]
        self.shotnoise_data = []

    def printHeader(self):
        """Show Header infos"""
        print 'Header:'
        for key, value in sorted(self.header.items()):
            print '    ', key.ljust(15), value

    def printData(self):
        """Print Data"""
        print 'x: ', self.data[:, 0]
        print 'y: ', self.data[:, 1]

    def writeFile(self, show=False):
        """"write pnt Object Header to text file"""
        filename = self.filename.replace('.pnt', '.txt')
        file = open(filename, 'w')
        file.write('#Automatic written Header from SnowMicroPen .pnt binary\n'
                   '#SLF Institute for Snow and Avalanche Research\n#\n'
                   '##################################\nHeader:\n##################################\n')
        message = ''
        for entry, value in sorted(self.header.items()):
            line = '%s %s\n' % (entry.ljust(15), str(value))
            file.write(line)
            message += line
        print 'Converted Header of %s to %s' % (self.filename, filename)
        file.close()
        if show:
            gui.infoScroll(message, self.filename + " Header")
        return filename

    ###########################################################
    def getData(self):
        """Read Force Data from .pnt file x=way, y=force"""
        try:
            data = self.raw
            start = 512
            end = self.header['Force Samples'] * 2 + start
            frmt = '>' + str(self.header['Force Samples']) + 'h'
            data = struct.unpack(frmt, data[start:end])
        except:
            print 'Error while reading data points'
            return None
        else:
            dx = self.header['Samples Dist [mm]']
            data_x = numpy.arange(0, len(data)) * dx
            data_y = numpy.asarray(data) * self.header['CNV Force [N/mV]']
            data = numpy.column_stack([data_x, data_y])

            print 'Read %d data points in %s' % (len(data_y), self.filename)
            return data

    def getRaw(self):
        """Get raw data from binary"""
        try:
            raw = open(self.filename, "rb").read()
        except:
            print 'Error: Could not open file %s' % self.filename
        else:
            print 'Read %d bytes in %s' % (len(raw), self.filename)

        return raw

    def getHeader(self):
        """Read Header from raw data"""

        # header construction name, type, start, length, unit
        construct = [
            ['Version', 'H', 0, 2, "-"],
            ['Tot Samples', 'i', 2, 4, "-"],
            ['Samples Dist [mm]', 'f', 6, 4, "mm"],
            ['CNV Force [N/mV]', 'f', 10, 4, "N/mV"],
            ['CNV Pressure [N/bar]', 'f', 14, 4, "N/bar"],
            ['Offset [N]', 'H', 18, 2, "N"],
            ['Year', 'H', 20, 2, "y"],
            ['Month', 'H', 22, 2, "m"],
            ['Day', 'H', 24, 2, "d"],
            ['Hour', 'H', 26, 2, "h"],
            ['Min', 'H', 28, 2, "min"],
            ['Sec', 'H', 30, 2, "s"],
            ['X Coord', 'd', 32, 8, "deg"],
            ['Y Coord', 'd', 40, 8, "deg"],
            ['Z Coord', 'd', 48, 8, "deg"],
            ['Battery [V]', 'd', 56, 8, "V"],
            ['Speed [mm/s]', 'f', 64, 4, "mm/s"],
            ['Loopsize', 'l', 68, 4, "-"],
            ['Waypoints', '10l', 72, 40, "-"],
            ['Calstart', '10H', 112, 20, "-"],
            ['Calend', '10H', 132, 20, "-"],
            ['Length Comment', 'H', 152, 2, "-"],
            ['Comment', '102s', 154, 102, "-"],
            ['File Name', '8s', 256, 8, "-"],
            ['Latitude', 'f', 264, 4, "deg"],
            ['Longitude', 'f', 268, 4, "deg"],
            ['Altitude [cm]', 'f', 272, 4, "cm"],
            ['PDOP', 'f', 276, 4, "-"],
            ['Northing', 'c', 280, 1, "-"],
            ['Easting', 'c', 281, 1, "-"],
            ['Num Sats', 'H', 282, 2, "-"],
            ['Fix Mode', 'H', 284, 2, "-"],
            ['GPS State', 'c', 286, 1, "-"],
            ['reserved 1', 'x', 187, 1, "-"],
            ['X local', 'H', 288, 2, "deg"],
            ['Y local', 'H', 290, 2, "deg"],
            ['Z local', 'H', 292, 2, "m"],
            ['Theta local', 'H', 294, 2, "deg"],
            ['reserved 2', '62x', 296, 62, "-"],
            ['Force Samples', 'l', 358, 4, "-"],
            ['Temperature Samples', 'l', 362, 4, "-"],
            ['Kistler Range [pC]', 'H', 366, 2, "pC"],
            ['Amp Range [pC]', 'H', 368, 2, "pC"],
            ['Sensitivity [pC/N]', 'H', 370, 2, "pC/N"],
            ['Temp Offset [N]', 'h', 372, 2, "Celsius"],
            ['Hand Op', 'H', 374, 2, "-"],
            ['Diameter [um]', 'l', 376, 4, "um"],
            ['Overload [N]', 'H', 380, 2, "N"],
            ['Sensor Type', 'c', 382, 1, "-"],
            ['Amp Type', 'c', 383, 1, "-"],
            ['SMP Serial', 'H', 384, 2, "-"],
            ['Length [mm]', 'H', 386, 2, "mm"],
            ['reserved 3', '4x', 388, 4, "-"],
            ['Sensor Serial', '20s', 392, 20, "-"],
            ['Amp Serial', '20s', 412, 20, "-"],
            ['reserved 4 ', '80x', 432, 80, "-"]
        ]

        # read header values
        values = []
        for f in range(len(construct)):
            frmt = '>' + construct[f][1]
            start = construct[f][2]
            end = start + construct[f][3]
            try:
                value = struct.unpack(frmt, self.raw[start:end])[0]
            except:
                value = ""
                pass
            values.append(value)

        # get header names
        names = [row[0] for row in construct]

        # create dict of names and values
        header = dict(zip(names, values))

        # cut strings
        if header['Length Comment'] == 0:
            header['Comment'] = ""
        else:
            header['Comment'] = header['Comment'].split("\x00")[0]

        header['File Name'] = header['File Name'].split("\x00")[0]
        header['Amp Serial'] = header['Amp Serial'].split("\x00")[0]
        header['Sensor Serial'] = header['Sensor Serial'].split("\x00")[0]
        header['Northing'] = header['Northing'].split("\x00")[0]
        header['Easting'] = header['Easting'].split("\x00")[0]
        header['GPS State'] = header['GPS State'].split("\x00")[0]

        # add sign to coordinates if required
        if header["Northing"] == "S":
            header["Latitude"] = - header["Latitude"]
        if header["Easting"] == "W":
            header["Longitude"] = - header["Longitude"]

        units = [row[4] for row in construct]

        return header, units


def plotData(self):
    """plot force against penetration depth"""
    plt.figure('Snow Micro Pen')
    plt.ylabel('Force [N]')
    plt.xlabel('Depth [mm]')
    plt.title(self.filename)
    plt.plot(self.data[:, 0], self.data[:, 1])
    plt.show()


#import snowmicropyn.gui.menus as gui

# def main():
#     """Convert selected .pnt binaries to readable .txt files"""
#     show = gui.ask('Show Measurement Graph?')
#     files = gui.openFile()
#     converted = []
#     for path in files:
#         pnt = Pnt(path)
#         if show:
#             plotData(pnt)
#         pnt.printHeader()
#         pnt.printData()
#         converted.append(pnt.writeFile(False))
#     list = '\n'.join(converted)
#     gui.infoScroll('Converted %d file(s):\n %s' % (len(converted), list))
#
#
# if __name__ == '__main__':
#     main()

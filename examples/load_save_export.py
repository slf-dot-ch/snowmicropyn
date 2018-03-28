# SnowMicroPyn Example: load_save_export.py
#
# This examples demonstrates load, saving and exporting a SMP
# profile. First, the profile is loaded from a binary pnt file. Some
# information is printed.
#
# Finally, the samples and meta data are exported to a file
# in CSV format.

import logging
import sys

from snowmicropyn.profile import Profile

# Enable logging to stdout to see what's going on under the hood
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

p = Profile.load('/Users/marcel/Dropbox/SMP/pnt_examples/S31M0067.pnt')
print('Timestamp: {}'.format(p.timestamp))
print('SMP Serial Number: {}'.format(p.smp_serial))
print('Coordinates: {}'.format(p.coordinates))

p.set_marker('surface', 100)
p.set_marker('ground', 400)
print('Markers: {}'.format(p.markers))

# Export measurements samples (depth, force) into a CSV. Pass a
# filename in case your got special needs for naming your file.
# Default naming convention: x.pnt --> x_samples.csv
p.export_samples()

# Export meta information (pnt header, markers) into a CSV. Pass a
# filename in case your got special needs for naming your file.
# Default naming convention: x.pnt --> x_meta.csv
p.export_meta(full_pnt_header=True)

# Save profile. This call writes an ini file containing parameters
# not stored in the binary pnt file like the markers for example.
# When a profile is loaded using Profile.load, it search for a
# matching ini file and loads its content in case its found. Default
# naming convention: x.pnt --> x.ini
p.save()

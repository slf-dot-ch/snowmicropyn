import logging
import sys

# Enable logging to stdout to see what's going on under the hood
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

from snowmicropyn import Profile

p = Profile.load('./some_directory/S31M0067.pnt')

print('Timestamp: {}'.format(p.timestamp))
print('SMP Serial Number: {}'.format(p.smp_serial))
print('Coordinates: {}'.format(p.coordinates))

p.set_marker('surface', 100)
p.set_marker('ground', 400)
print('Markers: {}'.format(p.markers))

# We don't want to loose our markers. Call save to write it to an ini
# file named like the pnt file.
p.save()

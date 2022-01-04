import logging
import sys

import snowmicropyn

# Enable logging to stdout to see what's going on under the hood
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

print(snowmicropyn.__version__)
print(snowmicropyn.githash())

p = snowmicropyn.Profile.load('profiles/S37M0876.pnt')

print('Timestamp: {}'.format(p.timestamp))
print('SMP Serial Number: {}'.format(p.smp_serial))
print('Coordinates: {}'.format(p.coordinates))

p.set_marker('surface', 100)
p.set_marker('ground', 400)
print('Markers: {}'.format(p.markers))

# We don't want to lose our markers. Call save to write it to an ini
# file named like the pnt file.
p.save()

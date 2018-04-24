import logging
import sys

# Enable logging to stdout to see what's going on under the hood
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

from snowmicropyn import Profile
from snowmicropyn.detection import detect_ground, detect_surface

p = Profile.load('./some_directory/S31M0067.pnt')

# Explicit...
ground = detect_ground(p.samples.values, p.overload)
surface = detect_surface(p.samples.values)

# ... implicit, this also set the markers 'ground' and 'surface'
# on the profile
g = p.detect_ground()
s = p.detect_surface()

print('Surface: {} mm'.format(surface))
print('Ground: {} mm'.format(ground))

import logging
import sys

from snowmicropyn.profile import Profile
from snowmicropyn.analysis import detect_surface, detect_ground

# Enable logging to stdout to see what's going on under the hood
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

p = Profile.load('/Users/marcel/Dropbox/SMP/pnt_examples/S31M0067.pnt')

# Explicit
ground = detect_ground(p.samples.values, p.overload)
surface = detect_surface(p.samples.values)

# Implicit, this also set markers 'ground' and 'surface' on the profile
g = p.detect_ground()
s = p.detect_surface()

print(p)
print('Surface: {} mm'.format(surface))
print('Ground: {} mm'.format(ground))

p.set_marker('ground', ground)
p.set_marker('surface', surface)
p.save()

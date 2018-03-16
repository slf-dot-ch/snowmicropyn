from matplotlib import pyplot as plt

from snowmicropyn.io import Pnt
import snowmicropyn.analysis.mathematics as smpcalc
from snowmicropyn.analysis.ssa import calculate_density_and_ssa_proksch as ssa

# Load profile. This also loads S31M0067_marks.csv, if available in same directory
p = Pnt.fromfile('/Users/marcel/Dropbox/SMP/pnt_examples/S31M0067.pnt')

# Access to measurements and other data
p.measurements

# Access markers like surface, ground, etc.
surface = p.marks.surface
ground = p.marks.ground

# Some calculations
surface = smpcalc.detect_ground(p)
ground = smpcalc.detect_surface(p)

ssa = ssa()

p.save()
from snowmicropyn.profile import Profile, SSA
import logging
import sys

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

p = Profile.load('/Users/marcel/Dropbox/SMP/pnt_examples/S31M0067.pnt')

p.set_marker('surface', 100)
p.set_marker('ground', 400)

ssa = SSA()
print(ssa.author())
print(ssa.compute(p))

p.save()

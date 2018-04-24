import numpy as np

from snowmicropyn.loewe2011 import model_shotnoise
from snowmicropyn.profile import Profile


np.set_printoptions(precision=4, suppress=True)

p = Profile.load('/Users/marcel/Dropbox/SMP/pnt_examples/S31M0067.pnt')

shotnoise = model_shotnoise(p.samples)
print(shotnoise)

# Saving model result
shotnoise.to_excel()

# Using convenient method on profile
shotnoise = p.model_shotnoise()
print(shotnoise)

import numpy as np

from snowmicropyn.models import model_shotnoise
from snowmicropyn.profile import Profile

np.set_printoptions(precision=4, suppress=True)

p = Profile.load('/Users/marcel/Dropbox/SMP/pnt_examples/S31M0067.pnt')

shotnoise_values = model_shotnoise(p.samples)
print(shotnoise_values)

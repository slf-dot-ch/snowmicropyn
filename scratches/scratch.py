import numpy as np

from snowmicropyn.loewe2011 import model_shotnoise
from snowmicropyn.profile import Profile

np.set_printoptions(precision=4, suppress=True)
p = Profile.load('/Users/marcel/Dropbox/SMP/pnt_examples/S31M0067.pnt')

print(p.samples.shape)

precision = 4
fmt = '%.{}f'.format(precision)
header = 'distance,lambda,f0,delta,L'
np.savetxt('shot_noise.csv', model_shotnoise(p.samples), delimiter=',', fmt=fmt, header=header, comments='')

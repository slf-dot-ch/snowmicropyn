from snowmicropyn import Profile
from snowmicropyn import proksch2015

p = Profile.load('profiles/S37M0876.pnt')
p2015 = proksch2015.model_ssa_and_density(p.samples)

crust_start = p.marker('crust_start')
crust_end = p.marker('crust_end')

crust = p2015[p2015.distance.between(crust_start, crust_end)]

# Calculate mean SSA within crust
print('Mean SSA within crust: {:.1f} m^2/m^3'.format(crust.P2015_ssa.mean()))

# How much weight lies above the hoar layer?
surface = p.marker('surface')
hoar_start = p.marker('depthhoar_start')
above_hoar = p2015[p2015.distance.between(surface, hoar_start)]
weight_above_hoar = above_hoar.P2015_density.mean() * (hoar_start - surface) / 1000
print('Weight above hoar layer: {:.0f} kg/m^2'.format(weight_above_hoar))

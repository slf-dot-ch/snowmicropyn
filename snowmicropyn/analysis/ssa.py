import numpy as np


# Mock-up!
def ssa(profile, l, impl='Proksch_2015'):
    impls = {
        'Proksch_2015': calculate_density_and_ssa_proksch
    }
    if impl not in impls:
        raise ValueError('Invalid value for parameter impl. Valid values: ' + ','.join(impls))

    # ... and execute
    return impls[impl]()


def calculate_density_and_ssa_proksch(median_force, l):
    # Parametrization of density and SSA as presented in
    # Proksch 2015, JGR (Journal of Geophysical Research)
    a = 420.47
    b = 102.47
    c = -121.15
    d = -169.96
    rho = a + b * np.log(median_force) + c * np.log(median_force) * l + d * l
    e = 0.1312
    f = 0.3548
    g = 0.0291
    lc = e + f * l + g * np.log(median_force)
    ssa = (4. * (1. - (rho / 917.)) / lc) / 917. * 1000.
    return [rho, ssa]

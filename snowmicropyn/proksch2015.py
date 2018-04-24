"""Calculation of density and ssa.

This module implements the methods to derive density and specific surface area
(SSA) from SnowMicroPen's signal as described in publication
`Density, specific surface area, and correlation length of snow measured by
high‐resolution penetrometry <https://doi.org/10.1002/2014JF003266>`_ by Martin
Proksch, Henning Löwe and Martin Schneebeli, publicised in `Journal of
Geophysical Research: Earth Surface
<https://agupubs.onlinelibrary.wiley.com/journal/21699011>`_, Volume 120,
Issue 2, February 2015.
"""

import pandas as pd

from snowmicropyn.loewe2011 import model_shotnoise
from snowmicropyn.windowing import DEFAULT_WINDOW, DEFAULT_WINDOW_OVERLAP

DENSITY_ICE = 917.


def calc_density_ssa(median_force, element_size):
    """Calculation of density and ssa

    :param median_force: median of force
    :param element_size: element size
    :return: Tuple containing density and ssa
    """

    l = element_size
    fm = median_force
    rho_ice = DENSITY_ICE

    # Equation 9 in publication
    a1 = 420.47
    a2 = 102.47
    a3 = -121.15
    a4 = -169.96
    rho = a1 + a2 * pd.np.log(fm) + a3 * pd.np.log(fm) * l + a4 * l

    # Equation 11 in publication
    c1 = 0.131
    c2 = 0.355
    c3 = 0.0291
    lc = c1 + c2 * l + c3 * pd.np.log(fm)

    # Equation 12 in publication
    ssa = 4 * (1 - (rho / rho_ice)) / lc

    return rho, ssa


def model_ssa_and_density(samples, window=DEFAULT_WINDOW, overlap_factor=DEFAULT_WINDOW_OVERLAP):
    # Base: shot noise model
    shotnoise = model_shotnoise(samples, window, overlap_factor)
    result = []
    for index, row in shotnoise.iterrows():
        rho, ssa = calc_density_ssa(row.f0, row.L)
        result.append((row.distance, rho, ssa))
    return pd.DataFrame(result, columns=['distance', 'rho', 'ssa'])

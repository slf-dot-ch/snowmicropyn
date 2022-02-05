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

from .. import derivatives
import numpy as np

class Proksch2015(derivatives.Derivatives):
    def __init__(self):
        self.name = 'Proksch 2015' # used in menus etc.
        self.shortname = 'P2015' # used in data frames etc.

    def density(self, F_m, LL):
        """Calculation of density from median of force and element size.

        :param F_m: Median of force in N.
        :param LL: Element size in mm.
        :return: density in kg/m^3.
        """
        # Equation 9 in publication
        aa = [420.47, 102.47, -121.15, -169.96]
        return aa[0] + aa[1] * np.log(F_m) + aa[2] * np.log(F_m) * LL + aa[3] * LL

    def ssa(self, density, F_m, LL):
        """Calculation of SSA from density, median of force and element size.

        :param density: Density in kg/m^3
        :param F_m: Median of force in N.
        :param LL: Element size in mm.
        :return: SSA value in m^2/kg.
        """
        DENSITY_ICE = 917.
        # Equation 11 in publication
        cc = [0.131, 0.355, 0.0291]
        lc = cc[0] + cc[1] * LL + cc[2] * np.log(F_m)
        # Equation 12 in publication
        ssa = 4 * (1 - (density / DENSITY_ICE)) / lc
        # Last line yields ssa in 1/mm, conversion to m^2/kg as per convention
        ssa = ssa * 1000 / DENSITY_ICE
        return ssa

derivatives.parameterizations.register('proksch2015', Proksch2015())

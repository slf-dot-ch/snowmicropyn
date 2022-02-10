"""Calculation of density and ssa.

This module implements the methods to derive density and specific surface area
(SSA) from SnowMicroPen's signal as described in publication
`Local-scale variability of snow density on Arctic sea ice
<https://doi.org/10.5194/tc-14-4323-2020>`_ by King, J., Howell, S.,
Brady, M., Toose, P., Derksen, C., Haas, C., and Beckers, J., publicised in
`The Cryosphere, 14
<https://tc.copernicus.org/articles/14/4323/2020/>`_, 4323–4339, 2020.
"""

from .. import derivatives
import numpy as np

class King2020a(derivatives.Derivatives):
    def __init__(self):
        """Properties of the parameterization.

        name: Descriptive long name (used in menus etc.)
        shortname: Shortcut name (used in file output etc.)
        window_size: Size of the moving window in mm
        overlap: Overlap factor in %
        """
        self.name = 'King 2020a'
        self.shortname = 'K2020a'
        self.window_size = 5
        self.overlap = 50

    def density(self, F_m, LL, lamb, f0, delta):
        """Calculation of density from median of force and element size.

        :param F_m: Median of force in N.
        :param LL: Element size in mm.
        :param lamb: Intensity of point process in mm^-1 (unused in King).
        :param f0: Mean rupture force in N (unused in King).
        :param delta: Deflection at rupture in mm (unused in King).
        :return: SSA value in m^2/kg.
        """
        # Table 2 in publication
        aa = [315.61, 46.94, -43.94, -88.15]
        return aa[0] + aa[1] * np.log(F_m) + aa[2] * np.log(F_m) * LL + aa[3] * LL

class King2020b(derivatives.Derivatives):
    def __init__(self):
        """Properties of the parameterization."""
        self.name = 'King 2020b'
        self.shortname = 'K2020b'
        self.window_size = 5
        self.overlap = 50

    def density(self, F_m, LL, lamb, f0, delta):
        """Calculation of density from median of force and element size."""
        # Table 2 in publication
        aa = [312.54, 50.27, -50.26, -85.35]
        return aa[0] + aa[1] * np.log(F_m) + aa[2] * np.log(F_m) * LL + aa[3] * LL

derivatives.parameterizations.register(King2020a()) # create instances for all of SMPyn
derivatives.parameterizations.register(King2020b())

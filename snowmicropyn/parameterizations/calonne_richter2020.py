"""Calculation of density and ssa.

This module implements the methods to derive density and specific surface area
(SSA) from SnowMicroPen's signal as described in publication
`The RHOSSA campaign: multi-resolution monitoring of the seasonal evolution of the
seasonal evolution of the structure and mechanical stability of an alpine snowpack
<https://doi.org/10.5194/tc-14-1829-2020>`_ by Neige Calonne, Bettina Richter, Henning Löwe,
Cecilia Cetti, Judith ter Schure, Alec Van Herwijnen, Charles Fierz, Matthias Jaggi, and
Martin Schneebeli publicised in `The Cryosphere
<https://tc.copernicus.org/articles/14/1829/2020/tc-14-1829-2020.html>`_, Volume 14, 2020.
"""

from .. import derivatives
import numpy as np

class CalonneRichter2020(derivatives.Derivatives):
    def __init__(self):
        """Properties of the parameterization.

        name: Descriptive long name (used in menus etc.)
        shortname: Shortcut name (used in file output etc.)
        window_size: Size of the moving window in mm
        overlap: Overlap factor in %
        """
        self.name = 'Calonne and Richter 2020'
        self.shortname = 'CR2020'
        self.window_size = 1
        self.overlap = 50

    def density(self, F_m, LL, lamb, f0, delta):
        """Calculation of density from median of force and element size.

        :param F_m: Median of force in N.
        :param LL: Element size in mm.
        :param lamb: Intensity of point process in mm^-1 (unused in Calonne/Richter).
        :param f0: Mean rupture force in N (unused in Calonne/Richter).
        :param delta: Deflection at rupture in mm (unused in Calonne/Richter).
        :return: density in kg/m^3.
        """
        # Equation (1) in publication
        aa = [295.8, 65.1, -43.2, 47.1]
        return aa[0] + aa[1] * np.log(F_m) + aa[2] * np.log(F_m) * LL + aa[3] * LL

    def ssa(self, density, F_m, LL, lamb, f0, delta):
        """Calculation of SSA from density, median of force and element size.

        :param density: Density in kg/m^3
        :param F_m: Median of force in N.
        :param LL: Element size in mm.
        :param lamb: Intensity of point process in mm^-1 (unused in Calonne/Richter).
        :param f0: Mean rupture force in N (unused in Calonne/Richter).
        :param delta: Deflection at rupture in mm (unused in Calonne/Richter).
        :return: SSA value in m^2/kg.
        """
        # Equation (2) in publication
        bb = [0.57, -18.56, -3.66]
        return bb[0] + bb[1] * np.log(LL) + bb[2] * np.log(F_m)

derivatives.parameterizations.register(CalonneRichter2020()) # create instance for all of SMPyn

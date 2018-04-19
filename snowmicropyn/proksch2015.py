from datetime import date

import pandas as pd

from .models import model_shotnoise
from .tools import Publication

AUTHORS = 'Martin Proksch, Henning Löwe, Martin Schneebeli'
TITLE = 'Density, specific surface area, and correlation length of snow measured by high-resolution penetrometry'
JOURNAL = 'Journal of Geophysical Research: Earth Surface, Volume 120, Issue 2'
PUBLISHED = date(year=2015, month=1, day=16)
URL = 'https://agupubs.onlinelibrary.wiley.com/doi/epdf/10.1002/2014JF003266'

DENSITY_ICE = 917.


def calc_density_ssa(median_force, element_size):
    """Calculation of density and ssa

    This function calculates density and ssa (specific surface area)
    according to publication Proksch, 2015, Journal of Geophysical
    Research.

    https://agupubs.onlinelibrary.wiley.com/doi/epdf/10.1002/2014JF003266

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


# noinspection PyClassHasNoInit
class Proksch2015:
    pubinfo = Publication(TITLE, AUTHORS, JOURNAL, PUBLISHED, URL)

    @staticmethod
    def apply(profile):
        # First we need to get the shot noise params
        shotnoise = model_shotnoise(profile.samples, 2.5, 1.4)
        result = []
        for index, row in shotnoise.iterrows():
            rho, ssa = calc_density_ssa(row.f0, row.L)
            result.append((rho, ssa))
        return pd.DataFrame(result, columns=['rho', 'ssa'])

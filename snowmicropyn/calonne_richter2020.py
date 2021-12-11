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

import pandas as pd
import numpy as np

import snowmicropyn.loewe2012
import snowmicropyn.windowing

def calc_step(median_force, element_size):
    """Calculation of density and ssa from median of force and element size.

    This is the actual math described in the publication.

    :param median_force: Median of force.
    :param element_size: Element size.
    :return: Tuple containing density and ssa value.
    """
    LL = element_size
    F_m = median_force

    # Equation (1) in publication
    a1 = 295.8
    a2 = 65.1
    a3 = -43.2
    a4 = 47.1
    density = a1 + a2 * np.log(F_m) + a3 * np.log(F_m) * LL + a4 * LL

    # Equation (2) in publication
    b1 = 0.57
    b2 = -18.56
    b3 = -3.66
    ssa = b1 + b2 * np.log(LL) + b3 * np.log(F_m)

    return density, ssa

def calc_from_loewe2012(shotnoise_dataframe):
    """Calculate ssa and density from a pandas dataframe containing shot noise
    model values.

    :param shotnoise_dataframe: A pandas dataframe containing shot noise model values.
    :return: A pandas dataframe with the columns 'distance', 'CR2020_density' and 'CR2020_ssa'.
    """
    result = []
    for index, row in shotnoise_dataframe.iterrows():
        density, ssa = calc_step(row.force_median, row.L2012_L)
        result.append((row.distance, density, ssa))
    return pd.DataFrame(result, columns=['distance', 'CR2020_density', 'CR2020_ssa'])

def calc(samples, window=snowmicropyn.windowing.DEFAULT_WINDOW, overlap=snowmicropyn.windowing.DEFAULT_WINDOW_OVERLAP):
    """Calculate ssa and density from a pandas dataframe containing the samples
    of a SnowMicroPen recording.

    :param samples: A pandas dataframe containing the columns 'distance' and 'force'.
    :param window: Size of window in millimeters.
    :param overlap: Overlap factor in percent.
    :return: A pandas dataframe with the columns 'distance', 'CR2020_density' and 'CR2020_ssa'.
    """
    sn = snowmicropyn.loewe2012.calc(samples, window, overlap)
    result = []
    for index, row in sn.iterrows():
        density, ssa = calc_step(row.force_median, row.L2012_L)
        result.append((row.distance, density, ssa))
    return pd.DataFrame(result, columns=['distance', 'CR2020_density', 'CR2020_ssa'])

"""Calculation of density and ssa.

This module implements the methods to derive density and specific surface area
(SSA) from SnowMicroPen's signal as described in
Calonne et al, in preparation (2021)
"""

from pandas import np as np
import pandas as pd

import snowmicropyn.loewe2012
import snowmicropyn.windowing

DENSITY_ICE = 917.


def calc_step(elementSize, medianForce):
    """Calculation of density and ssa from median of force and element size.

    This is the actual math described in the publication.

    :param median_force: Median of force.
    :param element_size: Element size.
    :return: Tuple containing density and ssa value.

       calculate density as derived in Calonne et al, in preparation (2021)
       input:
           elementSize in mm
           median Force in N
       returns:
           density in kg/m^3
           ssa in m^2/kg
       DISCLAIMER: unpublished (but likely better than proksch density)
       """

    a = 295.7538
    b = 65.1200
    c = -43.2137
    d = 47.1206
    density = a + b * np.log(medianForce) + c * np.log(medianForce) * elementSize + d * elementSize


    c1 = 0.57
    c2 = -18.56
    c3 = -3.66
    ssa = c1 + c2 * np.log(elementSize) + c3 * np.log(medianForce)

    return density, ssa


def calc_from_loewe2012(shotnoise_dataframe):
    """Calculate ssa and density from a pandas dataframe containing shot noise
    model values.

    :param shotnoise_dataframe: A pandas dataframe containing shot noise model values.
    :return: A pandas dataframe with the columns 'distance', 'P2015_density' and 'P2015_ssa'.
    """
    result = []
    for index, row in shotnoise_dataframe.iterrows():
        density, ssa = calc_step(row.force_median, row.L2012_L)
        result.append((row.distance, density, ssa))
    return pd.DataFrame(result, columns=['distance', 'C2018_density', 'C2018_ssa'])


def calc(samples, window=snowmicropyn.windowing.DEFAULT_WINDOW, overlap=snowmicropyn.windowing.DEFAULT_WINDOW_OVERLAP):
    """Calculate ssa and density from a pandas dataframe containing the samples
    of a SnowMicroPen recording.

    :param samples: A pandas dataframe containing the columns 'distance' and 'force'.
    :param window: Size of window in millimeters.
    :param overlap: Overlap factor in percent.
    :return: A pandas dataframe with the columns 'distance', 'P2015_density' and 'P2015_ssa'.
    """
    sn = snowmicropyn.loewe2012.calc(samples, window, overlap)
    result = []
    for index, row in sn.iterrows():
        density, ssa = calc_step(row.force_median, row.L2012_L)
        result.append((row.distance, density, ssa))
    return pd.DataFrame(result, columns=['distance', 'C2018_density', 'C2018_ssa'])

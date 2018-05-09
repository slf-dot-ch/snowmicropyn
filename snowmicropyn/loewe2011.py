""" Implementation of poisson shot noise model

This module implements the shot noise model according to publication `A Poisson
shot noise model for micro-penetration of snow
<https://doi.org/10.1016/j.coldregions.2011.09.001>`_ by Henning Löwe and Alec
van Herwijnen, publicised in `Cold Regions Science and Technology
<https://www.sciencedirect.com/journal/cold-regions-science-and-technology>`_,
Volume 70, January 2012.
"""

import math

import pandas as pd
from pandas import np as np

from .windowing import chunkup, DEFAULT_WINDOW, DEFAULT_WINDOW_OVERLAP

#: Default value for SnowMicroPen's cone diameter im mm.
SMP_CONE_DIAMETER = 5  # [mm]
#: Default value for SnowMicroPen's projected cone area, depends on :const:`SMP_CONE_DIAMETER`.
SMP_CONE_AREA = (SMP_CONE_DIAMETER / 2.) ** 2 * math.pi  # [mm^2]


def shotnoise_chunk(spatial_res, forces, cone_area=SMP_CONE_AREA):
    n = forces.size

    # Mean and variance of force signal
    k1 = np.mean(forces)
    k2 = np.var(forces)

    # Covariance/Autocorrelation
    c_f = np.correlate(forces, forces, mode='full')  # eq. 8 in LvH 2012

    # Equation 11 in publication
    delta = -(3. / 2) * c_f[n - 1] / (c_f[n] - c_f[n - 1]) * spatial_res

    # Equations 12 in publication
    lambda_ = (4. / 3) * (k1 ** 2) / k2 / delta  # Intensity
    f0 = (3. / 2) * k2 / k1

    # According to equation 2 in publication
    L = (cone_area / lambda_) ** (1. / 3)

    return lambda_, f0, delta, L


def shotnoise(samples, window=DEFAULT_WINDOW, overlap_factor=DEFAULT_WINDOW_OVERLAP):
    # Calculate spatial resolution of the distance samples as median of all
    # step sizes.
    spatial_res = np.median(np.diff(samples.distance.values))

    # Split dataframe into chunks
    chunks = chunkup(samples, window, overlap_factor)
    result = []
    for center, chunk in chunks:
        f_median = np.median(chunk.force)
        sn = shotnoise_chunk(spatial_res, chunk.force)
        result.append((center, f_median) + sn)
    return pd.DataFrame(result, columns=['distance', 'f_median', 'lambda', 'f0', 'delta', 'L'])

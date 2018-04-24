""" Implementation of poisson shot noise model

This module implements the shot noise model according to publication `A Poisson
shot noise model for micro-penetration of snow
<https://doi.org/10.1016/j.coldregions.2011.09.001>`_ by Henning Löwe and Alex
van Herwijnen, publicised in `Cold Regions Science and Technology
<https://www.sciencedirect.com/journal/cold-regions-science-and-technology>`_,
Volume 70, January 2012.
"""

import math

import pandas as pd
import scipy.signal
from pandas import np as np

from .windowing import chunkup, DEFAULT_WINDOW, DEFAULT_WINDOW_OVERLAP

#: Default value for SnowMicroPen's cone diameter im mm.
SMP_CONE_DIAMETER = 5  # [mm]
#: Default value for SnowMicroPen's projected cone area, depends on :const:`SMP_CONE_DIAMETER`.
SMP_CONE_AREA = (SMP_CONE_DIAMETER / 2.) ** 2 * math.pi  # [mm^2]


def shotnoise_from_evalSMP(spatial_res, forces, cone_area=SMP_CONE_AREA):
    # this version is taken from evalSMP and returns 5 parameters (instead of 4): lambda, f0, delta, L and median(F)
    """Returns the parameters lambda, f0, delta, L of the (uniform
    strength) shot noise model according to Loewe, van Herwijnen CRST
    70, 62-70 (2012)
    dz: spatial resolution
    f_z: force array
    a_cone: projected SMP tip area (mm^2)
    """

    n = forces.size

    # Mean and variance of the signal
    k1 = np.mean(forces)
    k2 = np.var(forces)

    # Detrend signal, note that the detrending is not foreseen in LvH (!!) but recommended by Martin Proksch
    forces = scipy.signal.detrend(forces - k1, type='linear')

    # Covariance/auto-correlation
    c_f = np.correlate(forces, forces, mode='full')  # eq. 8 in LvH 2012

    # Equation 11 in publication
    delta = -(3. / 2) * c_f[n - 1] / (c_f[n] - c_f[n - 1]) * spatial_res

    # Equations 12 in publication
    # lambda_ = Intensity
    lambda_ = (4. / 3) * (k1 ** 2) / k2 / delta
    f0 = (3. / 2) * k2 / k1

    # According to equation 2 in publication
    L = (cone_area / lambda_) ** (1. / 3)

    return lambda_, f0, delta, L


def model_shotnoise(samples, window=DEFAULT_WINDOW, overlap_factor=DEFAULT_WINDOW_OVERLAP):
    spatial_res = np.median(np.diff(samples.distance.values))
    chunks = chunkup(samples, window, overlap_factor)
    result = []
    for center, chunk in chunks:
        force_chunk = chunk.force
        shotnoise = shotnoise_from_evalSMP(spatial_res, force_chunk)
        r = (center,) + shotnoise
        result.append(r)
    return pd.DataFrame(result, columns=['distance', 'lambda', 'f0', 'delta', 'L'])

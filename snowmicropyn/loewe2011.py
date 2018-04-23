import math

import pandas as pd
from pandas import np as np
from scipy.signal import detrend

from .windowing import chunkup, DEFAULT_WINDOW, DEFAULT_WINDOW_OVERLAP

SMP_CONE_DIAMETER = 5
SMP_CONE_AREA = (SMP_CONE_DIAMETER / 2.) ** 2 * math.pi


def shotnoise_from_evalSMP(spatial_res, force_arr, area_cone=SMP_CONE_AREA):
    # this version is taken from evalSMP and returns 5 parameters (instead of 4): lambda, f0, delta, L and median(F)
    """Returns the parameters lambda, f0, delta, L of the (uniform
    strength) shot noise model according to Loewe, van Herwijnen CRST
    70, 62-70 (2012)
    dz: spatial resolution
    f_z: force array
    a_cone: projected SMP tip area (mm^2)
    """

    # Auxiliary parameters
    n = force_arr.size

    # Mean and variance of the signal
    k1 = np.mean(force_arr)
    k2 = np.var(force_arr)

    # Detrend signal, note that the detrending is not foreseen in LvH (!!) but recommended by Martin Proksch
    force_arr = detrend(force_arr - k1, type='linear')

    # Covariance/auto-correlation
    c_f = np.correlate(force_arr, force_arr, mode='full')  # eq. 8 in LvH 2012

    # Equation 11 in publication
    delta = -(3. / 2) * c_f[n - 1] / (c_f[n] - c_f[n - 1]) * spatial_res

    # Equations 12 in publication
    # lambda_ = Intensity
    lambda_ = (4. / 3) * (k1 ** 2) / k2 / delta
    f0 = (3. / 2) * k2 / k1

    # According to equation 2 in publication
    L = (area_cone / lambda_) ** (1. / 3)

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

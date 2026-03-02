"""Implementation of poisson shot noise model

This module implements the shot noise model according to publication
`A Poisson shot noise model for micro-penetration of snow
<https://doi.org/10.1016/j.coldregions.2011.09.001>`_ by Henning Löwe
and Alec van Herwijnen, publicised in `Cold Regions Science and
Technology
<https://www.sciencedirect.com/journal/cold-regions-science-and-technology>`_,
Volume 70, January 2012, with one addition: As suggested in Proksch,
Henning Löwe and Martin Schneebeli, publicised in `Journal of
Geophysical Research: Earth Surface
<https://agupubs.onlinelibrary.wiley.com/journal/21699011>`_, Volume
120, Issue 2, February 2015, the force signals are detrended before
the force correlation function is computed.

"""

import math
import pandas as pd
import numpy as np
from scipy import signal
import logging

from .windowing import chunkup, chunkup_numpy

log = logging.getLogger('snowmicropyn')

#: Default value for SnowMicroPen's cone diameter im mm.
SMP_CONE_DIAMETER = 5  # [mm]
#: Default value for SnowMicroPen's projected cone area, depends on :const:`SMP_CONE_DIAMETER`.
SMP_CONE_AREA = (SMP_CONE_DIAMETER / 2.) ** 2 * math.pi  # [mm^2]

def calc_step(spatial_res, forces, cone_area=SMP_CONE_AREA):
    """Calculate shot noise parameters for a segment of a profile.

    This is the actual implementation of the algorithm described in the
    publication and calculates the derived parameters for a single segment of
    the profile.

    :param spatial_res: Spatial resolution of profile.
    :param forces: Numpy array containing the force values.
    :param cone_area: Projected area of cone (tip) of SnowMicroPen in square
           millimeters.
    :return: A tuple containing lambda, f0, delta and L.
    """
    forces = np.asarray(forces)
    n = len(forces)

    # Mean and variance of force signal
    k1 = forces.mean()
    k2 = forces.var()

    # use a tolerance to detect where the signal deviates from the background
    # level and treat this as surface
    tol = 0.001
    if k1 < tol:
        return 0, 0, 0, np.inf  # Constant signal

    is_surface = False
    k1_ = forces[:n // 2].mean()
    if k1_ < tol:
        is_surface = True

    # signal detrending as suggested by Proksch 2015
    force_detrended = signal.detrend(forces - k1, type='linear')

    # Covariance/Autocorrelation (Equation 8 in publication)
    # We only need lag-0 and lag-1 values, so use O(n) dot products
    # instead of the full O(n²) np.correlate.
    c0 = np.dot(force_detrended, force_detrended)          # lag 0
    c1 = np.dot(force_detrended[:-1], force_detrended[1:])  # lag 1

    # Equation 11 in publication
    delta = -(3. / 2) * c0 / (c1 - c0) * spatial_res

    # Equation 12 in publication
    try: # Try/catch for speed
        lambda_ = (4. / 3) * (k1 ** 2) / k2 / delta  # Intensity
    except FloatingPointError:
        lambda_ = np.inf # A warning will be shown later
    f0 = (3. / 2) * k2 / k1

    # According to equation 2 in publication
    if is_surface:
        # Treat surface slightly different as density lambda_ is underestimated
        L = (cone_area / (4 * lambda_)) ** (1. / 3)
    else:
        L = (cone_area / lambda_) ** (1. / 3)

    return lambda_, f0, delta, L


def calc(samples, window, overlap):
    """Calculation of shot noise model parameters.

    :param samples: A pandas dataframe with columns called 'distance' and 'force'.
    :param window: Size of moving window.
    :param overlap: Overlap factor in percent.
    :return: Pandas dataframe with the columns 'distance', 'force_median',
             'L2012_lambda', 'L2012_f0', 'L2012_delta', 'L2012_L'.
             force_median: Median of force in N.
             lambda: Intensity of point process in mm^-1.
             f0: Mean rupture force in N.
             delta: Deflection at rupture in mm.
             L: Element size in mm.
    """

    # Extract numpy arrays once – avoids pandas overhead per chunk.
    dist_arr = samples.distance.values
    force_arr = samples.force.values

    # Calculate spatial resolution of the distance samples as median of all
    # step sizes.
    spatial_res = np.median(np.diff(dist_arr))

    # Split into chunks using fast numpy index ranges
    chunks = chunkup_numpy(dist_arr, force_arr, window, overlap)

    # Pre-allocate result arrays
    n_chunks = len(chunks)
    out_dist = np.empty(n_chunks)
    out_fmed = np.empty(n_chunks)
    out_lamb = np.empty(n_chunks)
    out_f0   = np.empty(n_chunks)
    out_delt = np.empty(n_chunks)
    out_L    = np.empty(n_chunks)

    with np.errstate(divide='raise'): # Allow for our own handling with all np configurations
        for i, (center, i0, i1) in enumerate(chunks):
            chunk_force = force_arr[i0:i1]
            out_dist[i] = center
            out_fmed[i] = np.median(chunk_force)
            lam, f0, dlt, L = calc_step(spatial_res, chunk_force)
            out_lamb[i] = lam
            out_f0[i]   = f0
            out_delt[i] = dlt
            out_L[i]    = L

    result = pd.DataFrame({
        'distance': out_dist,
        'force_median': out_fmed,
        'L2012_lambda': out_lamb,
        'L2012_f0': out_f0,
        'L2012_delta': out_delt,
        'L2012_L': out_L,
    })

    if np.isinf(out_lamb).any():
        log.warning('Constant signal - could not compute intensity of Poisson process')
        if len(log.handlers) > 1: # we are in the GUI
            log.handlers[1].toTop()
    return result

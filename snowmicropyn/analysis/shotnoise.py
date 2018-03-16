import numpy
from scipy.signal import detrend

from snowmicropyn.analysis.ssa import calculate_density_and_ssa_proksch
from snowmicropyn.analysis.corr import xcorr


def shotnoise_from_evalSMP(dz, f_z, a_cone=19.6):
    # this version is taken from evalSMP and returns 5 parameters (instead of 4): lambda, f_0, delta, L and median(F)
    """Returns the parameters lambda, f_0, delta, L of the (uniform
    strength) shot noise model according to Loewe, van Herwijnen CRST
    70, 62-70 (2012)
    dz: spatial resolution
    f_z: force array
    A_cone: projected SMP tip area (mm^2)
    """

    # auxiliary parameters
    n = f_z.size

    # mean and variance of the signal
    c1 = numpy.mean(f_z)
    c2 = numpy.var(f_z)

    # detrend signal, note that the detrending is not foreseen in LvH
    # (!!) but recommended by Martin Proksch
    detrended_f_z = detrend(f_z - c1, type='linear')

    # covariance/auto-correlation
    C_f = numpy.correlate(detrended_f_z, detrended_f_z, mode='full')  # eq. 8 in LvH 2012

    # retrieve shot noise parameters
    delta = -3.0 / 2 * C_f[n - 1] / (C_f[n] - C_f[n - 1]) * dz  # eq. 11 in LvH 2012
    lambd = 4.0 / 3 * c1 ** 2 / c2 / delta  # eq. 12 in LvH 2012
    f_0 = 3.0 / 2 * c2 / c1  # eq. 12 in LvH 2012
    L = (a_cone / lambd) ** (1.0 / 3)  # eq. 2 in  LvH 2012

    f_median = numpy.median(f_z)
    [density, ssa] = calculate_density_and_ssa_proksch(f_median, L)

    # return values
    return [lambd, f_0, delta, L, f_median, density, ssa]


def getSNParams(file, window=2.5, overlap=50):
    """get shot noise theory parameters, see function shotnoise()
    for details.
    x: distance array in mm
    y: force array in N
    windows: analysis windows in mm
    overlap: overlap of windows in %
    """
    distance = file.data[:, 0]
    force = file.data[:, 1]

    overlap = window * overlap / 100.
    dz = (distance[-1] - distance[0]) / len(distance)
    start = numpy.where(distance >= file.surface)[0][0]
    end = numpy.where(distance >= file.ground)[0][0]
    distance = distance[start:end]
    force = force[start:end]

    x0 = distance[0]
    dx = window - overlap
    data = []
    while x0 + window <= distance[-1]:
        start = numpy.where(distance >= x0)[0][0]
        end = numpy.where(distance >= x0 + window)[0][0]
        shotnoise_data = shotnoise_from_evalSMP(dz, force[start:end])
        shotnoise_data.append(float(x0))
        data.append(shotnoise_data)
        x0 += dx

    return data


def shotnoise(dz, f_z, A_cone=19.6):
    """This functions calculates the shot noise parameters from the
    SMP penetration force correlation function according to:
    Loewe and van Herwijnen, 2012: A Poisson shot noise model for
    micro-penetration of snow, CRST.
    d_z:
    f_z: array with force values
    A-cone: projected cone area [mm^2]"""

    n = len(f_z)

    # estimate shot noise parameters:
    c1 = numpy.mean(f_z)  # mean
    c2 = numpy.var(f_z, ddof=1)  # variance

    c_f, d = xcorr(detrend(f_z - c1), detrend(f_z - c1), norm="unbiased")  # eq. 8 in Loewe and van Herwijnen, 2012

    # shot noise parameters
    delta = -3. / 2 * c_f[n - 1] / ((c_f[n]) - c_f[n - 1]) * dz  # eq. 11 in Loewe and van Herwijnen, 2012
    lambd = 4. / 3 * (c1 ** 2) / c2 / delta  # eq. 12 in Loewe and van Herwijnen, 2012
    f_0 = 3. / 2 * c2 / c1  # eq. 12 in Loewe and van Herwijnen, 2012
    l = (A_cone / lambd) ** 1 / 3

    return lambd, f_0, delta, l

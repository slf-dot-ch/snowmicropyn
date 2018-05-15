import logging

from pandas import np as np

from .tools import downsample, smooth

log = logging.getLogger(__name__)


def detect_ground(profile):
    """Automatic detection of ground (end of snowpack).

    :param snowmicropyn.Profile profile: The profile to detect ground in.
    :return: Distance where ground was detected.
    :rtype: float
    """

    force = profile.samples.force
    distance = profile.samples.distance

    ground = distance.iloc[-1]

    if force.max() >= profile.overload:
        i_ol = force.argmax()
        i_threshhold = np.where(distance.values >= distance.values[i_ol] - 20)[0][0]
        f_mean = np.mean(force.iloc[0:i_threshhold])
        f_std = np.std(force.iloc[0:i_threshhold])
        threshhold = f_mean + 5 * f_std

        while force.iloc[i_ol] > threshhold:
            i_ol -= 10

        ground = distance.iloc[i_ol]

    log.info('Detected ground at {:.3f} mm in profile {}'.format(ground, profile))
    return ground


def detect_surface(profile):
    """Automatic detection of surface (begin of snowpack).

    :param profile: The profile to detect surface in.
    :return: Distance where surface was detected.
    :rtype: float
    """

    # Cut off ca. 1 mm
    distance = profile.samples.distance.values[250:]
    force = profile.samples.force.values[250:]

    force = downsample(force, 20)
    distance = downsample(distance, 20)

    force = smooth(force, 242)

    y_grad = np.gradient(force)
    y_grad = downsample(y_grad, 3)
    x_grad = downsample(distance, 3)

    max_force = np.amax(force)

    try:
        for i in np.arange(100, x_grad.size):
            std = np.std(y_grad[:i - 1])
            mean = np.mean(y_grad[:i - 1])
            if y_grad[i] >= 5 * std + mean:
                surface = x_grad[i]
                break

        if i == x_grad.size - 1:
            surface = max_force

        log.info('Detected surface at {:.3f} mm in profile {}'.format(surface, profile))
        return surface

    except ValueError:
        log.warning('Failed to detect surface')
        return max_force

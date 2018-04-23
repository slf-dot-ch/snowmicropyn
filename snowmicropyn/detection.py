import logging

from pandas import np as np

from .tools import downsample, smooth

log = logging.getLogger(__name__)


def detect_ground(samples, overload):
    force_arr = samples[:, 0]
    distance_arr = samples[:, 1]

    ground = force_arr[-1]

    if np.max(distance_arr) >= overload:
        i_ol = np.argmax(distance_arr)
        i_threshold = np.where(force_arr >= force_arr[i_ol] - 20)[0][0]
        f_mean = np.mean(distance_arr[0:i_threshold])
        f_std = np.std(distance_arr[0:i_threshold])
        threshold = f_mean + 5 * f_std

        while distance_arr[i_ol] > threshold:
            i_ol -= 10

        ground = force_arr[i_ol]

    log.info('Detected ground at {:.3f} mm'.format(ground))
    return ground


def detect_surface(samples):
    max_value = np.amax(samples[:, 0])

    # Cut off ca. 1 mm
    forces = samples[250:, 0]
    distances = samples[250:, 1]

    distances = downsample(distances, 20)
    forces = downsample(forces, 20)

    distances = smooth(distances, 242)

    y_grad = np.gradient(distances)
    y_grad = downsample(y_grad, 3)
    x_grad = downsample(forces, 3)

    try:
        for i in np.arange(100, x_grad.size):

            std = np.std(y_grad[:i - 1])
            mean = np.mean(y_grad[:i - 1])
            if y_grad[i] >= 5 * std + mean:
                surface = x_grad[i]
                break

        if i == x_grad.size - 1:
            surface = max_value

        log.info('Detected surface at {:.3f} mm'.format(surface))
        return surface

    except ValueError:
        log.warning('Failed to detect surface')
        return max_value

import collections

from matplotlib import pyplot as plt
from pandas import np as np

pub_fields = ['title', 'authors', 'journal', 'url', 'pubdate']
Publication = collections.namedtuple('Publication', pub_fields)


def merge_profiles(profiles):
    """
    :param profiles:
    :return: A single
    """
    raise NotImplementedError('merge_profiles not implemented yet')


def subtract_median(x, y, window=200):
    """Subtract median of frame from original signal y"""
    start = 0
    end = len(y) - 1
    y_out = []

    while start <= end:
        median = np.median(y[start:start + window])
        y_out[start:start + window] = y[start:start + window] - median
        start += window

    x_out = x[:len(y_out)]
    return x_out, y_out


def rsme(x_ref, x_sub, norm=False):
    """Root-mean-square error calculation """

    result = ((x_ref - x_sub) ** 2).mean()
    if norm:
        result = result / np.max(x_ref) * 100
    return result


def downsample(x, n=2):
    if n < 1:
        raise ValueError('n must be bigger or equal 1')

    i = np.mod(len(x), n)
    x = x[:len(x) - i].reshape(-1, n).mean(axis=1)
    return x


def smooth(x, window_len=11, window='hanning'):
    """Smooth the data using a window with requested size"""

    if x.ndim != 1:
        raise ValueError('Function only accepts 1 dimension arrays.')
    if x.size < window_len:
        raise ValueError('Input vector needs to be bigger than window size.')
    if window_len < 3:
        return x
    valid = ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']
    if window not in valid:
        raise ValueError('Invalid value for parameter window. Valid values: ' + ','.join(valid))

    s = np.r_[x[window_len - 1:0:-1], x, x[-1:-window_len:-1]]

    if window == 'flat':
        # moving average
        w = np.ones(window_len, 'd')
    else:
        w = eval('np.' + window + '(window_len)')

    y = np.convolve(w / w.sum(), s, mode='valid')
    return y


# This function is used to calculate offset, drift and noise.
def lin_fit(x, y, surface=None):

    x = x[10:]
    y = y[10:]

    i = np.where(x >= surface)[0][0]
    x = x[:i]
    y = y[:i]

    m, c = np.polyfit(x, y, 1)
    y_fit = x * m + c
    std = np.std(y - y_fit)

    return x, y_fit, m, c, std


def force_drops(x, y, max_dx=0.02, min_dy=0.05, dx_bins=0.02):
    dy = -min_dy
    start = 0
    end = 1
    down = []
    i_max = len(y)

    while end < i_max:

        delta = y[start] - y[end]

        if x[end] - x[start] > max_dx:
            start += 1
            end = start + 1
            continue

        elif delta > dy:
            end += 1
            continue

        down.append(delta)

        start = end
        end = start + 1

    down = np.abs(down)
    bin_down = (max(down) - min(down)) / dx_bins

    plt.hist(down, normed=True, stacked=False, bins=bin_down)
    plt.show()

    return down

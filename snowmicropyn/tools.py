from pandas import np as np


def merge_profiles(profiles):
    raise NotImplementedError('merge_profiles not implemented yet')


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
def lin_fit(x, y):
    m, c = np.polyfit(x, y, 1)
    y_fit = x * m + c
    std = np.std(y - y_fit)

    return x, y_fit, m, c, std

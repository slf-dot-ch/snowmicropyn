import logging

import matplotlib.pyplot as plt
import numpy as np
import scipy.fftpack
from scipy import interpolate
from scipy.signal import butter, filtfilt

log = logging.getLogger(__name__)


def downsample(x, n=2):
    if n < 1:
        raise ValueError('n must be bigger or equal 1')

    i = np.mod(len(x), n)
    x = x[:len(x) - i].reshape(-1, n).mean(axis=1)
    return x


def smooth(x, window_len=11, window='hanning'):
    """smooth the data using a window with requested size"""

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


def detect_ground(pnt):
    x = pnt.data[:, 0]
    y = pnt.data[:, 1]
    ol = pnt.header["Overload [N]"]
    ground = x[-1]

    if np.max(y) >= ol:
        i_ol = np.argmax(y)
        i_threshold = np.where(x >= x[i_ol] - 20)[0][0]
        f_mean = np.mean(y[0:i_threshold])
        f_std = np.std(y[0:i_threshold])
        threshold = f_mean + 5 * f_std

        while y[i_ol] > threshold:
            i_ol -= 10

        ground = x[i_ol]

    log.info('ground :%0.2f mm'.format(ground))
    return ground


def detect_surface(x_orig, y_orig):
    """find surface of file[index]"""

    x = x_orig[250:]  # cut off ca 1mm
    y = y_orig[250:]

    y = downsample(y, 20)
    x = downsample(x, 20)

    y = smooth(y, 242)
    # x,y = butterworth(x,y,c=1))

    y_grad = np.gradient(y)
    y_grad = downsample(y_grad, 3)
    x_grad = downsample(x, 3)

    try:
        for i in np.arange(100, x_grad.size):

            std = np.std(y_grad[:i - 1])
            mean = np.mean(y_grad[:i - 1])
            if y_grad[i] >= 5 * std + mean:
                surface = x_grad[i]
                break

        if i == x_grad.size - 1:
            surface = np.amax(x_orig)
    except ValueError:
        print "couldn't get surface"
        surface = np.amax(x_orig)
        pass

    print "surface: %0.2f mm" % surface
    return surface


def linFit(x, y, surface=None):
    x = x[10:]
    y = y[10:]

    i = np.where(x >= surface)[0][0]
    x = x[:i]
    y = y[:i]

    m, c = np.polyfit(x, y, 1)
    y_fit = x * m + c
    std = np.std(y - y_fit)

    return x, y_fit, m, c, std


def butterworth(x, y, freq=242, c=5, o=2, show=False):
    """Filter signal y(x) with sampling frequency f using a o-order butterworth filter
       and cutoff frequency c"""

    # Butterworth filter
    b, a = butter(o, (c / (freq / 2)), btype='low')
    y2 = filtfilt(b, a, y)  # filter with phase shift correction
    # plot
    """    fig, ax1 = plt.subplots(1,1)
    ax1.plot(x,  y, 'r.-', linewidth=1, label = 'raw data')
    ax1.plot(x, y2, 'g.-', linewidth=1, label = 'filtfilt')
    ax1.legend(frameon=False, fontsize=14)
    ax1.set_xlabel("Dist [mm]"); ax1.set_ylabel("Force [N]");

    plt.show()"""

    if show:
        # 2nd derivative of the data
        ydd = np.diff(y, 2) * freq * freq  # raw data
        y2dd = np.diff(y2, 2) * freq * freq  # filtered data
        # frequency content 
        yfft = np.abs(scipy.fftpack.fft(y)) / (y.size / 2)  # raw data
        y2fft = np.abs(scipy.fftpack.fft(y2)) / (y.size / 2)  # filtered data
        freqs = scipy.fftpack.fftfreq(y.size, 1. / freq)
        yddfft = np.abs(scipy.fftpack.fft(ydd)) / (ydd.size / 2)
        y2ddfft = np.abs(scipy.fftpack.fft(y2dd)) / (ydd.size / 2)
        freqs2 = scipy.fftpack.fftfreq(ydd.size, 1. / freq)

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)

        ax1.set_title('Temporal domain', fontsize=14)
        ax1.plot(x, y, 'r', linewidth=1, label='raw data')
        ax1.plot(x, y2, 'b', linewidth=1, label='filtered @ %.2f per mm' % c)
        ax1.set_ylabel('f')
        ax1.legend(frameon=False, fontsize=12)

        ax2.set_title('Frequency domain', fontsize=14)
        ax2.plot(freqs[:yfft.size / 2], yfft[:yfft.size / 2], 'r', linewidth=1, label='raw data')
        ax2.plot(freqs[:yfft.size / 2], y2fft[:yfft.size / 2], 'b--', linewidth=1, label='filtered @ %.2f per mm' % c)
        ax2.set_ylabel('FFT(f)')
        ax2.legend(frameon=False, fontsize=12)

        ax3.plot(x[:-2], ydd, 'r', linewidth=1, label='raw')
        ax3.plot(x[:-2], y2dd, 'b', linewidth=1, label='filtered @ %.2f Hz' % c)
        ax3.set_xlabel('Depth [mm]')
        ax3.set_ylabel("f ''")

        ax4.plot(freqs[:yddfft.size / 2], yddfft[:yddfft.size / 2], 'r', linewidth=1, label='raw')
        ax4.plot(freqs[:yddfft.size / 2], y2ddfft[:yddfft.size / 2], 'b--', linewidth=1,
                 label='filtered @ %.2f per mm' % c)
        ax4.set_xlabel('Frequency [$mm^{-1}$]')
        ax4.set_ylabel("FFT(f '')")

        plt.show()

    return x, y


# root-mean-square error calculation
def rsme(x_ref, x_sub, norm=False):
    rsme = ((x_ref - x_sub) ** 2).mean()
    if norm:
        rsme = rsme / np.max(x_ref) * 100
    return rsme


def subtractMedian(x, y, window=200):
    """subtract median of frame from original signal y """
    start = 0
    end = len(y) - 1
    y_out = []

    while start <= end:
        median = np.median(y[start:start + window])
        y_out[start:start + window] = y[start:start + window] - median
        start += window

    x_out = x[:len(y_out)]
    return x_out, y_out


def transsectGetValues(x, y, window=2.5, overlap=50):
    """this function prepares 2d transect data.
    x = distance array
    y = force array f(x)
    window [mm] = alaysation window for log(median(f))
    overlap [%] = overlap of analyzation windows"""

    x_out = []
    y_out = []
    while x[0] + window <= x[-1]:
        i_end = np.where(x >= x[0] + window)[0][0]
        median = np.median(y[:i_end])
        i_start = np.where(x >= x[0] + window * overlap / 100.)[0][0]
        x_out.append(x[0])
        y_out.append(np.log(median))
        x = x[i_start:]
        y = y[i_start:]

    return x_out, y_out


def transsectFromFile(Files):
    """Create 2d transsect from pnt Files"""
    X = []
    F = []
    y = []
    # appen x,y, and force data to 3 arrays
    for file in Files:
        x, f = transsectGetValues(file.data[:, 0], file.data[:, 1])
        surface = np.where(x >= file.surface)[0][0]
        ground = np.where(x >= file.ground)[0][0]

        X.append(x[surface:ground])
        F.append(f[surface:ground])
        y.append(len(y))

    # Set up a regular grid of interpolation points
    xi, yi = np.linspace(X.min(), X.max(), len(X) / len(Files)), np.linspace(y.min(), y.max(),
                                                                             len(X) / len(Files))
    xi, yi = np.meshgrid(xi, yi)

    # Interpolate
    rbf = interpolate.Rbf(X, y, F, function='linear')
    zi = rbf(xi, yi)

    plt.imshow(zi, vmin=F.min(), vmax=F.max(), origin='lower',
               extent=[X.min(), X.max(), y.min(), y.max()])
    plt.scatter(X, y, c=F)
    plt.colorbar()
    plt.show()


def forceDrops(x, y, max_dx=0.020, min_dy=0.050, dx_bins=0.02):
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

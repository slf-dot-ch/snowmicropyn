import numpy as np
from matplotlib import pyplot as plt
from scipy import signal

from snowmicropyn.helpers import lin_fit
from snowmicropyn.profile import Profile

p = Profile.load('/Users/marcel/Dropbox/SMP/pnt_examples/S31M0064.pnt')
surface = p.detect_surface()
print('Surface')
print(surface)

x = p.distance_arr
y = p.force_arr

x, y_fit, drift, offset, noise = lin_fit(x, y, p.marker('surface'))
print('lin_fit:')
print(drift, offset, noise)


def running_mean(x, n):
    cumsum = np.cumsum(np.insert(x, 0, 0))
    return (cumsum[n:] - cumsum[:-n]) / n


imin = 10
imax = 30000

x = p.distance_arr[imin:imax]
y = p.force_arr[imin:imax]

y_rm = running_mean(y, 242)

y_savgol_1 = signal.savgol_filter(y, window_length=242*10 + 1, polyorder=1)
y_smoothed = signal.savgol_filter(y_savgol_1, window_length=242*4+1, polyorder=1, deriv=1) * 10000


i_surface = np.where(x > surface)[0][0]
print(i_surface)

plt.axvline(i_surface, label='Original', color='y')
plt.plot(y, color='blue', label='SMP signal')
plt.plot(y_savgol_1, color='red', label='savgol_1')
plt.plot(y_smoothed, color='green', label='savgol_deriv')

#plt.plot(signal.savgol_filter(np.gradient(y_smoothed,3), 243, 2)*1000, color='pink', label='gradient savgol')
plt.legend()

plt.show()




# SnowMicroPyn Example: plot.py
#
# Plotting the signal of a SMP profile using the library matploblib.
# An interactive plot is shown, you can pan, zoom, export by using
# the toolbar buttons. Happy examining!

from matplotlib import pyplot as plt

from snowmicropyn.profile import Profile

p = Profile.load('/Users/marcel/Dropbox/SMP/pnt_examples/S31M0067.pnt')
x, y = p.distance_arr, p.force_arr

plt.plot(x, y)

plt.title(p.name)
plt.ylabel('Force [N]')
plt.xlabel('Depth [mm]')

plt.show()

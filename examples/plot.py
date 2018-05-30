from matplotlib import pyplot as plt

from snowmicropyn import Profile

p = Profile.load('profiles/S37M0876.pnt')

# Plot distance on x and samples on y axis
plt.plot(p.samples.distance, p.samples.force)

# Prettify our plot a bit
plt.title(p.name)
plt.ylabel('Force [N]')
plt.xlabel('Depth [mm]')

# Show interactive plot with zoom, export and other features
plt.show()

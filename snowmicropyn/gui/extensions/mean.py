import matplotlib.pyplot as plt
import numpy as np


class Drift(object):
    def __init__(self, x, y):
        self.dataX = x
        self.dataY = y
        self.xpoint = self.dataX[0]
        self.ypoint = self.dataY[0]

        self.fig, (self.ax, self.ax2) = plt.subplots(2, 1)
        self.fig.canvas.set_window_title('SMP Mean Value, Drift and Noise Analysis Tool')

        self.fig.subplots_adjust(hspace=0.4)

        self.selected, = self.ax.plot(
            [self.dataX[0]],
            [self.dataY[0]],
            'o',
            ms=12,
            alpha=0.2,
            color='red',
            visible=False
        )

        self.v1 = self.ax.axvline(x=x[0], color="red", visible=False)
        self.v2 = self.ax.axvline(x=x[-1], color="red", visible=False)

        self.ax.set_title('Original Data')
        self.ax.set_xlabel("Depth [mm]")
        self.ax.set_ylabel("Force [N]")
        self.ax2.set_title("Selected Range")
        self.ax2.set_ylabel("Force [N]")
        self.ax2.set_xlabel("Depth [mm]")
        self.line, = self.ax.plot(self.dataX, self.dataY, picker=5)  # 5 points tolerance

        self.fig.canvas.mpl_connect('pick_event', self.onpick)

        plt.show()

    def onpick(self, event):
        x = event.mouseevent.xdata
        y = event.mouseevent.ydata

        distances = np.hypot(x - self.dataX[event.ind], y - self.dataY[event.ind])
        indmin = distances.argmin()
        self.index = event.ind[indmin]
        self.update()

    def update(self):
        if self.index is None: return
        self.selected.set_visible(True)
        self.v1.set_visible(True)
        self.v2.set_visible(True)

        self.xpoint = np.append(self.selected.get_xdata(), self.dataX[self.index])
        self.ypoint = np.append(self.selected.get_ydata(), self.dataY[self.index])
        self.xpoint = self.xpoint[-2:]
        self.ypoint = self.ypoint[-2:]

        self.selected.set_data(self.xpoint, self.ypoint)
        length = [0, 10]
        v1 = ([self.xpoint[0], self.xpoint[0]], length)
        v2 = ([self.xpoint[1], self.xpoint[1]], length)
        self.v1.set_data(v1)
        self.v2.set_data(v2)

        self.ax2.set_title("Selected Range")
        self.ax2.set_ylabel("Force [N]")
        self.ax2.set_xlabel("Depth [mm]")
        self.ax2.clear()

        min = np.where(self.dataX == np.amin(self.xpoint))[0]
        max = np.where(self.dataX == np.amax(self.xpoint))[0]

        x = self.dataX[min:max]
        y = self.dataY[min:max]

        self.ax2.plot(x, y)
        self.ax2.set_xlim((np.amin(x), np.amax(x)))
        self.ax2.set_title("Selected Range")
        self.ax2.set_ylim((np.amin(y), 2 * np.amax(y)))

        self.linFit(x, y)

        self.fig.canvas.draw()

    def linFit(self, x, y):
        mean = np.mean(y)
        dev = np.std(y)
        m, c = np.polyfit(x, y, 1)
        y_fit = x * m + c
        std = np.sqrt(np.mean((y - y_fit) ** 2))
        self.ax2.plot(x, y_fit, "r--", x, y_fit + std, "b:", x, y_fit - std, "b:")
        self.ax2.text(0.05, 0.9, 'Mean: (%.2e +- %.2e) N\nSlope: %.2e N/m\nStd: %.2e N' % (mean, dev, m * 1000, std),
                      transform=self.ax2.transAxes, va='top')


if __name__ == "__main__":
    test = Drift(np.arange(0, 1000), np.random.normal(0, 1, 1000))

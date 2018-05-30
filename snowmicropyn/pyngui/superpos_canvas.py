import logging

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

log = logging.getLogger(__name__)


class SuperposCanvas(FigureCanvas):

    COLOR_ACTIVE = 'C0'
    COLOR_INACTIVE = 'C7'

    def __init__(self, main_window):
        self.main_window = main_window
        self.figure = Figure()
        super(SuperposCanvas, self).__init__(self.figure)

        self._lines = dict()

        self.axes = self.figure.add_axes([0.1, 0.1, 0.85, 0.80])
        self.axes.set_title('Superposition')
        self.axes.xaxis.set_label_text('Snow Depth [mm]')
        self.axes.yaxis.set_label_text('Force [N]')

        self.active_doc = None

    def add_doc(self, doc):
        p = doc.profile
        lines = self.axes.plot(p.samples.distance, p.samples.force)
        self._lines[p.name] = lines
        self.set_active_doc(doc)

    def set_active_doc(self, doc):
        if self.active_doc:
            lines = self._lines[self.active_doc.profile.name]
            for l in lines:
                l.set_color(self.COLOR_INACTIVE)
                l.set_zorder(1)
        if doc:
            lines = self._lines[doc.profile.name]
            for l in lines:
                l.set_color(self.COLOR_ACTIVE)
                l.set_zorder(2)
        self.active_doc = doc
        self.draw()

    def remove_doc(self, doc):
        p = doc.profile
        lines = self._lines.pop(p.name)
        for l in lines:
            l.remove()
        self.draw()
        if doc is self.active_doc:
            self.active_doc = None

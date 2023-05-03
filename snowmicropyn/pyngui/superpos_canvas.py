import logging

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

log = logging.getLogger('snowmicropyn')


class SuperposCanvas(FigureCanvas):

    COLOR_ACTIVE = 'C0'
    COLOR_INACTIVE = 'C7'

    def __init__(self, main_window):
        self.main_window = main_window
        self.figure = Figure()
        super(SuperposCanvas, self).__init__(self.figure)

        self._lines = dict()
        self._airgap_lines = dict()

        self.axes = self.figure.add_axes([0.1, 0.1, 0.85, 0.80])
        self.axes.set_title('Superposition')
        self.axes.xaxis.set_label_text('Snow Depth [mm]')
        self.axes.yaxis.set_label_text('Force [N]')
        self.airgap_axes = self.figure.add_axes([0.1, 0.1, 0.85, 0.80])
        self.airgap_axes.set_title('Superposition with air gap hidden')
        self.airgap_axes.xaxis.set_label_text('Snow Depth [mm]')
        self.airgap_axes.yaxis.set_label_text('Force [N]')
        self.airgap_axes.autoscale(enable=True, axis='x', tight=True)

        self.active_doc = None

    def add_doc(self, doc):
        pro = doc.profile

        lines = self.axes.plot(pro.samples.distance, pro.samples.force)
        self._lines[pro.name] = lines

        samples_sp = doc.profile.samples_within_snowpack()
        airgap_lines = self.airgap_axes.plot(samples_sp.distance, samples_sp.force)
        self._airgap_lines[pro.name] = airgap_lines

        self.airgap_axes.relim()
        self.set_active_doc(doc)

    def set_active_doc(self, doc):
        if self.active_doc:
            lines = self._lines[self.active_doc.profile.name]
            for l in lines:
                l.set_color(self.COLOR_INACTIVE)
                l.set_zorder(1)
            airgap_lines = self._airgap_lines[self.active_doc.profile.name]
            for l in airgap_lines:
                l.set_color(self.COLOR_INACTIVE)
                l.set_zorder(1)
        if doc:
            lines = self._lines[doc.profile.name]
            for l in lines:
                l.set_color(self.COLOR_ACTIVE)
                l.set_zorder(2)
            airgap_lines = self._airgap_lines[doc.profile.name]
            for l in airgap_lines:
                l.set_color(self.COLOR_ACTIVE)
                l.set_zorder(2)
        self.active_doc = doc
        self.draw()

    def remove_doc(self, doc):
        p = doc.profile
        lines = self._lines.pop(p.name)
        for l in lines:
            l.remove()
        airgap_lines = self._airgap_lines.pop(p.name)
        for l in airgap_lines:
            l.remove()
        self.draw()
        if doc is self.active_doc:
            self.active_doc = None

    def _switch_airgap(self, hide_airgap: bool):
        for pro in self._lines:
            for l in self._lines[pro]:
                l.set_visible(not hide_airgap)
            for l in self._airgap_lines[pro]:
                l.set_visible(hide_airgap)
        self.axes.set_visible(not hide_airgap)
        self.airgap_axes.set_visible(hide_airgap)
        self.airgap_axes.relim()
        self.draw()

    def _update_on_marker(self, doc):
        self.remove_doc(doc)
        self.add_doc(doc)


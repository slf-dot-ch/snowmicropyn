import logging
import math
from pandas import np as np

from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QAction, QMenu
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

log = logging.getLogger(__name__)


class PlotCanvas(FigureCanvas):

    def __init__(self, main_window):
        self.main_window = main_window
        self.figure = Figure()
        super(PlotCanvas, self).__init__(self.figure)

        # When a context click is done, a menu pops up to select a
        # which marker to set. The value where the click was performed
        # is stored in this field.
        self._clicked_distance = None

        self._markers = dict()
        self._signals_axes = dict()
        self._drift_axes = None

        self.mpl_connect('button_press_event', self.mouse_button_pressed)

        def set_marker(name):
            main_window.set_marker(name, self.clicked_distance())

        def add_marker():
            main_window.add_marker(default_value=self.clicked_distance())

        set_surface_action = QAction('Set Surface to here', self)
        set_surface_action.triggered.connect(lambda checked: set_marker('surface'))

        set_ground_action = QAction('Set Ground to here', self)
        set_ground_action.triggered.connect(lambda checked: set_marker('ground'))

        add_marker_action = QAction("Add Marker...", self)
        add_marker_action.triggered.connect(lambda checked: add_marker())

        set_drift_begin_action = QAction('Set Drift Begin to here', self)
        set_drift_begin_action.triggered.connect(lambda checked: set_marker('drift_begin'))

        set_drift_end_action = QAction('Set Drift End to here', self)
        set_drift_end_action.triggered.connect(lambda checked: set_marker('drift_end'))

        # Context Menu, shown on right click in canvas
        menu = QMenu()
        menu.addAction(set_surface_action)
        menu.addAction(set_ground_action)
        menu.addSeparator()
        menu.addAction(set_drift_begin_action)
        menu.addAction(set_drift_end_action)
        menu.addSeparator()
        menu.addAction(add_marker_action)

        self.context_menu = menu

    def clicked_distance(self):
        return self._clicked_distance

    def color_for_marker(self, label):
        if label == 'surface':
            return 'C3'
        if label == 'ground':
            return 'C4'
        if label.startswith('drift_'):
            return 'C6'
        return 'C5'

    def set_document(self, doc):
        self.figure.clear()
        self._markers.clear()
        self._signals_axes.clear()
        if doc is None:
            return

        main_axes = self.figure.add_axes([0.1, 0.1, 0.72, 0.85])
        main_axes.xaxis.set_label_text('Distance [mm]')
        main_axes.yaxis.set_visible(False)

        FORCE_COLOR = 'C0'
        SSA_COLOR = 'C1'
        DENSITY_COLOR = 'C2'
        DRIFT_COLOR = 'C6'

        for label, value in doc.profile.markers:
            self.set_marker(label, value)

        # Force signal
        force_axes = main_axes.twinx()
        force_axes.yaxis.set_label_text('Force [N]')
        force_axes.yaxis.label.set_color(FORCE_COLOR)
        force_axes.plot(doc.profile.samples.distance, doc.profile.samples.force, FORCE_COLOR)
        self._signals_axes['smp'] = force_axes

        # Drift signal and text
        drift_axes = main_axes.twinx()
        drift_axes.set_axis_off()
        drift_axes.set_ylim(force_axes.get_ylim())
        drift_axes.plot(doc._fit_x, doc._fit_y, DRIFT_COLOR)
        x = doc._fit_x.iloc[-1]
        y = doc._fit_y.iloc[-1]
        dx = doc._fit_x.iloc[-1] - doc._fit_x.iloc[0]
        dy = doc._fit_y.iloc[-1] - doc._fit_y.iloc[0]
        angle = math.atan(dy/dx) * (180/math.pi)
        loc = np.array((x, y))
        trans_angle = self.figure.gca().transData.transform_angles(np.array((angle,)), loc.reshape((1, 2)))[0]
        drift_axes.text(x, y, 'drift', color=DRIFT_COLOR, rotation=trans_angle, rotation_mode='anchor', verticalalignment='top', horizontalalignment='right')
        self._drift_axes = drift_axes

        # SSA Proksch 2015
        ssa_axes = main_axes.twinx()
        ssa_axes.yaxis.label.set_text('SSA [$m^2/m^3$]')
        ssa_axes.yaxis.label.set_color(SSA_COLOR)
        ssa_axes.plot(doc.derivatives.distance, doc.derivatives.P2015_ssa, SSA_COLOR)
        self._signals_axes['P2015_ssa'] = ssa_axes

        # Density Proksch 2015
        density_axes = main_axes.twinx()
        density_axes.yaxis.set_label_text('Density [$kg/m^3$]')
        density_axes.yaxis.label.set_color(DENSITY_COLOR)
        density_axes.plot(doc.derivatives.distance, doc.derivatives.P2015_density, DENSITY_COLOR)
        self._signals_axes['P2015_density'] = density_axes

    def draw(self):
        plot_smpsignal = self.main_window.plot_smpsignal_action.isChecked()
        plot_surface = self.main_window.plot_surface_action.isChecked()
        plot_ground = self.main_window.plot_ground_action.isChecked()
        plot_markers = self.main_window.plot_markers_action.isChecked()
        plot_drift = self.main_window.plot_drift_action.isChecked()
        plot_ssa_proksch2015 = self.main_window.plot_ssa_proksch2015_action.isChecked()
        plot_density_proksch2015 = self.main_window.plot_density_proksch2015_action.isChecked()

        prefs = self.main_window.preferences
        distance_axis_limits = (prefs.distance_axis_from, prefs.distance_axis_to) if prefs.distance_axis_fix else None
        force_axis_limits = (prefs.force_axis_from, prefs.force_axis_to) if prefs.force_axis_fix else None
        density_axis_limits = (prefs.density_axis_from, prefs.density_axis_to) if prefs.density_axis_fix else None
        ssa_axis_limits = (prefs.ssa_axis_from, prefs.ssa_axis_to) if prefs.ssa_axis_fix else None

        for k, (line, text) in self._markers.items():
            visibility = plot_markers
            if k == 'surface':
                visibility = plot_surface
            elif k == 'ground':
                visibility = plot_ground
            elif k.startswith('drift_'):
                visibility = plot_drift
            line.set_visible(visibility)
            text.set_visible(visibility)

        outward_pos = 0
        for k, axes in self._signals_axes.items():
            visibility = None
            if k == 'smp':
                visibility = plot_smpsignal
                axes.yaxis.tick_left()
                axes.yaxis.set_label_position('left')
                if distance_axis_limits:
                    axes.set_xlim(*distance_axis_limits)
                if force_axis_limits:
                    axes.set_ylim(*force_axis_limits)

            if k == 'P2015_ssa':
                visibility = plot_ssa_proksch2015
                axes.yaxis.tick_right()
                axes.yaxis.set_label_position('right')
                if ssa_axis_limits:
                    axes.set_ylim(*ssa_axis_limits)

                # Place y-axis outside plot if axis on right is already in use
                if visibility:
                    axes.spines['right'].set_position(('outward', outward_pos))
                    outward_pos += 60

            if k == 'P2015_density':
                visibility = plot_density_proksch2015
                axes.yaxis.tick_right()
                axes.yaxis.set_label_position('right')
                if density_axis_limits:
                    axes.set_ylim(*density_axis_limits)

                # Place y-axis outside plot if axis on right is already in use
                if visibility:
                    axes.spines['right'].set_position(('outward', outward_pos))
                    outward_pos += 60

            axes.set_visible(visibility)

        if self._drift_axes:
            self._drift_axes.set_visible(plot_drift)

        super(PlotCanvas, self).draw()

    def set_marker(self, label, value):
        if label in self._markers:
            line, text = self._markers.pop(label)
            line.remove()
            text.remove()
        if value is not None:
            axes = self.figure.gca()
            color = self.color_for_marker(label)
            line = axes.axvline(value, color=color)
            text = axes.annotate(label, xy=(value, 1), xycoords=('data', 'axes fraction'), rotation=90, verticalalignment='top', color=color)
            self._markers[label] = line, text

    def mouse_button_pressed(self, event):
        log.debug('context click. x={}'.format(event))
        if event.button == 3:
            # Save distance value where the click was
            self._clicked_distance = event.xdata
            cursor = QCursor()
            self.context_menu.popup(cursor.pos())

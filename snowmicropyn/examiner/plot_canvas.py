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

    def set_document(self, doc):
        self.figure.clear()
        if doc is None:
            return

        axes = self.figure.add_axes([0.1, 0.1, 0.7, 0.85])
        axes.xaxis.set_label_text('Distance [mm]')

        FORCE_COLOR = 'C0'
        SSA_COLOR = 'C1'
        DENSITY_COLOR = 'C2'
        SURFACE_COLOR = 'C3'
        GROUND_COLOR = 'C4'
        MARKERS_COLOR = 'C5'
        DRIFT_COLOR = 'C6'

        prefs = self.main_window.preferences
        distance_axis_limits = (prefs.distance_axis_from, prefs.distance_axis_to) if prefs.distance_axis_fix else None
        force_axis_limits = (prefs.force_axis_from, prefs.force_axis_to) if prefs.force_axis_fix else None
        density_axis_limits = (prefs.density_axis_from, prefs.density_axis_to) if prefs.density_axis_fix else None
        ssa_axis_limits = (prefs.ssa_axis_from, prefs.ssa_axis_to) if prefs.ssa_axis_fix else None

        plot_markers = self.main_window.plot_markers_action.isChecked()
        plot_surface = self.main_window.plot_surface_action.isChecked()
        plot_ground = self.main_window.plot_ground_action.isChecked()
        plot_smpsignal = self.main_window.plot_smpsignal_action.isChecked()
        plot_drift = self.main_window.plot_drift_action.isChecked()

        plot_ssa_proksch2015 = self.main_window.plot_ssa_proksch2015_action.isChecked()
        plot_density_proksch2015 = self.main_window.plot_density_proksch2015_action.isChecked()

        if plot_markers:
            for label, value in doc.profile.markers:
                if label in ['surface', 'ground', 'drift_begin', 'drift_end']:
                    continue

                axes.axvline(value, color=MARKERS_COLOR)
                axes.annotate(label, xy=(value, 1), xycoords=('data', 'axes fraction'),
                              rotation=90, verticalalignment='top', color=MARKERS_COLOR)

        if plot_drift:
            try:
                drift_begin = doc.profile.marker('drift_begin')
                axes.axvline(drift_begin, color=DRIFT_COLOR)
                axes.annotate('drift_begin', xy=(drift_begin, 1), xycoords=('data', 'axes fraction'),
                              rotation=90, verticalalignment='top', color=DRIFT_COLOR)
            except KeyError:
                pass
            try:
                drift_begin = doc.profile.marker('drift_end')
                axes.axvline(drift_begin, color=DRIFT_COLOR)
                axes.annotate('drift_end', xy=(drift_begin, 1), xycoords=('data', 'axes fraction'),
                              rotation=90, verticalalignment='top', color=DRIFT_COLOR)
            except KeyError:
                pass

        if plot_surface:
            try:
                surface = doc.profile.surface
                axes.axvline(surface, color=SURFACE_COLOR)
                axes.annotate('surface', xy=(surface, 1), xycoords=('data', 'axes fraction'),
                              rotation=90, verticalalignment='top', color=SURFACE_COLOR)
            except KeyError:
                pass

        if plot_ground:
            try:
                ground = doc.profile.ground
                axes.axvline(ground, color=GROUND_COLOR)
                axes.annotate('ground', xy=(ground, 1), xycoords=('data', 'axes fraction'),
                              rotation=90, verticalalignment='top', color=GROUND_COLOR)
            except KeyError:
                pass

        if plot_smpsignal:
            axes.yaxis.set_label_text('Force [N]')
            axes.plot(doc.profile.samples.distance, doc.profile.samples.force, FORCE_COLOR)
            axes.yaxis.label.set_color(FORCE_COLOR)
            if distance_axis_limits:
                axes.set_xlim(*distance_axis_limits)
            if force_axis_limits:
                axes.set_ylim(*force_axis_limits)

        if plot_drift:
            axes.plot(doc._fit_x, doc._fit_y, DRIFT_COLOR)

            x = doc._fit_x.iloc[-1]
            y = doc._fit_y.iloc[-1]

            dx = doc._fit_x.iloc[-1] - doc._fit_x.iloc[0]
            dy = doc._fit_y.iloc[-1] - doc._fit_y.iloc[0]
            angle = math.atan(dy/dx) * (180/math.pi)

            loc = np.array((x, y))

            trans_angle = self.figure.gca().transData.transform_angles(np.array((angle,)), loc.reshape((1, 2)))[0]

            axes.text(x, y, 'drift', color=DRIFT_COLOR,
                      rotation=trans_angle, rotation_mode='anchor', verticalalignment='top', horizontalalignment='right')

        if plot_ssa_proksch2015 and doc.model_df is not None:
            ssa = axes.twinx()
            ssa.yaxis.label.set_text('SSA [$m^2/m^3$]')
            ssa.yaxis.label.set_color(SSA_COLOR)
            ssa.plot(doc.model_df.distance, doc.model_df.ssa, SSA_COLOR)
            if ssa_axis_limits:
                ssa.set_ylim(*ssa_axis_limits)

        if plot_density_proksch2015 and doc.model_df is not None:
            density = axes.twinx()
            density.yaxis.set_label_text('Density [$kg/m^3$]')
            density.yaxis.label.set_color(DENSITY_COLOR)
            density.plot(doc.model_df.distance, doc.model_df.density, DENSITY_COLOR)
            if density_axis_limits:
                density.set_ylim(*density_axis_limits)
            # Place y-axis outside in case ssa axis is also present
            if plot_ssa_proksch2015:
                density.spines['right'].set_position(('outward', 60))

    def mouse_button_pressed(self, event):
        log.debug('context click. x={}'.format(event))
        if event.button == 3:
            # Save distance value where the click was
            self._clicked_distance = event.xdata
            cursor = QCursor()
            self.context_menu.popup(cursor.pos())

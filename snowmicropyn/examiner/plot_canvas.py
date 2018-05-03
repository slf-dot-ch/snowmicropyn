import logging
from functools import partial

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

        def set_surface(checked):
            main_window.set_marker('surface', self.clicked_distance())
        set_surface_action = QAction('Set Surface to here', self)
        set_surface_action.triggered.connect(set_surface)

        def set_ground(checked):
            main_window.set_marker('ground', self.clicked_distance())
        set_ground_action = QAction('Set Ground to here', self)
        set_ground_action.triggered.connect(set_ground)

        def add_marker(checked):
            main_window.add_marker(default_value=self.clicked_distance())
        add_marker_action = QAction("Add Marker...", self)
        add_marker_action.triggered.connect(add_marker)

        set_drift_start_action = QAction('Set Drift Start to here', self)
        set_drift_end_action = QAction('Set Drift End to here', self)

        # Context Menu, shown on right click in canvas
        menu = QMenu()
        menu.addAction(set_surface_action)
        menu.addAction(set_ground_action)
        menu.addAction(add_marker_action)
        menu.addSeparator()
        menu.addAction(set_drift_start_action)
        menu.addAction(set_drift_end_action)

        self.context_menu = menu

    def clicked_distance(self):
        return self._clicked_distance

    def set_document(self, doc):
        self.figure.clear()
        if doc is None:
            return

        axes = self.figure.add_axes([0.1, 0.1, 0.7, 0.8])

        FORCE_COLOR = 'C0'
        SSA_COLOR = 'C1'
        DENSITY_COLOR = 'C2'
        SURFACE_COLOR = 'C3'
        GROUND_COLOR = 'C4'

        axes.set_title(doc.profile.pnt_filename, y=1.04)

        axes.xaxis.set_label_text('Distance [mm]')
        axes.yaxis.set_label_text('Force [N]')
        axes.plot(doc.profile.samples.distance, doc.profile.samples.force, FORCE_COLOR)
        axes.yaxis.label.set_color(FORCE_COLOR)

        plot_surface = self.main_window.plot_surface_action.isChecked()
        plot_ground = self.main_window.plot_ground_action.isChecked()
        plot_ssa_proksch2015 = self.main_window.plot_ssa_proksch2015_action.isChecked()
        plot_density_proksch2015 = self.main_window.plot_density_proksch2015_action.isChecked()

        middle = doc.profile.max_force()

        if plot_surface:
            try:
                surface = doc.profile.surface
                axes.axvline(surface, color=SURFACE_COLOR)
                axes.text(x=surface, y=middle, s='surface',
                          rotation=90,
                          verticalalignment='top',
                          color=SURFACE_COLOR)
            except KeyError:
                pass

        if plot_ground:
            try:
                ground = doc.profile.ground
                axes.axvline(ground, color=GROUND_COLOR)
                axes.text(x=ground, y=middle, s='ground',
                          rotation=90,
                          verticalalignment='top',
                          color=GROUND_COLOR)
            except KeyError:
                pass

        if plot_ssa_proksch2015 and doc.ssa_density_df is not None:
            ssa = axes.twinx()
            ssa.yaxis.label.set_text('SSA [$m^2/m^3$]')
            ssa.yaxis.label.set_color(SSA_COLOR)
            ssa.plot(doc.ssa_density_df.distance, doc.ssa_density_df.ssa, SSA_COLOR)

        if plot_density_proksch2015 and doc.ssa_density_df is not None:
            density = axes.twinx()
            density.yaxis.set_label_text('Density [$kg/m^3$]')
            density.yaxis.label.set_color(DENSITY_COLOR)
            density.plot(doc.ssa_density_df.distance, doc.ssa_density_df.density, DENSITY_COLOR)
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

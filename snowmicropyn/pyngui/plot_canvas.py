import logging
from collections import defaultdict, OrderedDict
from functools import partial

from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QAction, QMenu
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

log = logging.getLogger('snowmicropyn')

class PlotCanvas(FigureCanvas):
    COLOR_BLUE = 'C0'
    COLOR_ORANGE = 'C1'
    COLOR_GREEN = 'C2'
    COLOR_RED = 'C3'
    COLOR_VIOLET = 'C4'
    COLOR_BROWN = 'C5'
    COLOR_PINK = 'C6'
    COLOR_GREY = 'C7'
    COLOR_YELLOW = 'C8'
    COLOR_CYAN = 'C9'

    COLORS = {
        'label_force': COLOR_BLUE,
        'label_ssa': COLOR_GREEN,
        'label_density': COLOR_VIOLET,
        'label_drift': COLOR_CYAN,
        'plot_force': COLOR_BLUE,
        'plot_drift': COLOR_CYAN,
        'marker_surface': COLOR_RED,
        'marker_ground': COLOR_RED,
        'marker_others': COLOR_GREY,
        'marker_drift_begin': COLOR_CYAN,
        'marker_drift_end': COLOR_CYAN
    }

    COLORS = defaultdict(lambda: 'C0', COLORS)

    LABEL_FONT_SIZE = 14
    TICKS_FONT_SIZE = 12

    def __init__(self, main_window):
        self.main_window = main_window

        for key, par in self.main_window.params.items():
            self.COLORS['plot_density_' + key] = par._density_color
            self.COLORS['plot_ssa_' + key] = par._ssa_color

        self.figure = Figure()
        super(PlotCanvas, self).__init__(self.figure)

        # When a context click is done, a menu pops up to select
        # which marker to set. The value where the click was performed
        # is stored in this field.
        self._clicked_distance = None

        self._axes = dict()
        self._plots = dict()
        self._markers = dict()  # Contains tuples: line, text
        self._drift_label = None

        self.mpl_connect('button_press_event', self.mouse_button_pressed)

    def build_menu(self):
        def set_marker(name):
            self.main_window.set_marker(name, self.clicked_distance())

        def add_marker():
            self.main_window.new_marker(default_value=self.clicked_distance())

        labels = set(self.main_window.all_marker_labels())
        labels.discard('surface')
        labels.discard('ground')
        labels.discard('drift_begin')
        labels.discard('drift_end')

        menu = QMenu()

        action = QAction('Set surface', self)
        action.triggered.connect(lambda: set_marker('surface'))
        menu.addAction(action)

        action = QAction('Set ground', self)
        action.triggered.connect(lambda: set_marker('ground'))
        menu.addAction(action)

        menu.addSeparator()

        action = QAction('Set drift_begin', self)
        action.triggered.connect(lambda: set_marker('drift_begin'))
        menu.addAction(action)

        action = QAction('Set drift_end', self)
        action.triggered.connect(lambda: set_marker('drift_end'))
        menu.addAction(action)

        menu.addSeparator()

        for label in sorted(labels):
            action = QAction('Set ' + label, self)
            action.triggered.connect(partial(lambda l: set_marker(l), label))
            menu.addAction(action)

        menu.addSeparator()

        action = QAction("New Marker...", self)
        action.triggered.connect(lambda checked: add_marker())
        menu.addAction(action)

        return menu

    def clicked_distance(self):
        return self._clicked_distance

    def set_document(self, doc, remove_air_gap=False):
        self.figure.clear()

        self._axes.clear()
        self._plots.clear()
        self._markers.clear()
        self._drift_label = None

        name = 'force'
        axes = self.figure.add_axes([0.1, 0.1, 0.72, 0.85])
        axes.xaxis.set_label_text('Snow Depth [mm]')
        axes.xaxis.label.set_size(self.LABEL_FONT_SIZE)
        axes.xaxis.set_tick_params(labelsize=self.TICKS_FONT_SIZE)
        axes.yaxis.label.set_text('Force [N]')
        axes.yaxis.label.set_color(self.COLORS['label_' + name])
        axes.yaxis.label.set_size(self.LABEL_FONT_SIZE)
        axes.yaxis.set_tick_params(labelsize=self.TICKS_FONT_SIZE)
        self._axes[name] = axes

        name = 'ssa'
        axes = self._axes['force'].twinx()
        axes.yaxis.label.set_text('SSA [$m^2/kg$]')
        axes.yaxis.label.set_color(self.COLORS['label_' + name])
        axes.yaxis.tick_right()
        axes.yaxis.set_label_position('right')
        axes.yaxis.label.set_size(self.LABEL_FONT_SIZE)
        axes.yaxis.set_tick_params(labelsize=self.TICKS_FONT_SIZE)
        self._axes[name] = axes

        name = 'density'
        axes = self._axes['force'].twinx()
        axes.yaxis.label.set_text('Density [$kg/m^3$]')
        axes.yaxis.label.set_color(self.COLORS['label_' + name])
        axes.yaxis.tick_right()
        axes.yaxis.set_label_position('right')
        axes.yaxis.label.set_size(self.LABEL_FONT_SIZE)
        axes.yaxis.set_tick_params(labelsize=self.TICKS_FONT_SIZE)
        self._axes[name] = axes

        if doc is None:
            return

        samples = doc.profile.samples
        surface_offset = 0
        if remove_air_gap:
            surface_offset = doc.profile.marker('surface', fallback=0) * -1
            samples = doc.profile.samples_within_snowpack()
        values = (samples.distance, samples.force)
        self.set_plot('force', 'force', values)

        for key, param in self.main_window.params.items():  # run through all available parameterizations
            derivs = doc.derivatives[key] # these were already calculated with the creation of doc
            values = (derivs['distance'] + surface_offset, derivs[param.shortname + '_density'])
            self.set_plot('density', 'density_' + key, values)
            if hasattr(param, 'ssa'):
                values = (derivs['distance'] + surface_offset, derivs[param.shortname + '_ssa'])
                self.set_plot('ssa', 'ssa_' + key, values)

        val_x = doc._fit_x + surface_offset
        val_y = doc._fit_y
        val_y = val_y.where(val_x >= 0)
        val_x = val_x.where(val_x >= 0)

        if not val_x.isnull().all():
            self.set_plot('force', 'drift', (val_x, val_y))

        for label, value in doc.profile.markers.items():
            if value + surface_offset >= 0:
                 self.set_marker(label, value + surface_offset)

        self.set_limits()

    def set_plot(self, axes_id, plot_id, values):
        if plot_id in self._plots:
            lines = self._plots.pop(plot_id)
            for l in lines:
                l.remove()
            if plot_id == 'drift' and self._drift_label:
                self._drift_label.remove()
                self._drift_label = None
        if values:
            color = self.COLORS['plot_' + plot_id]
            x, y = values
            axes = self._axes[axes_id]
            lines = axes.plot(x, y, color)
            self._plots[plot_id] = lines

            if plot_id == 'drift':
                label_x = x.iloc[-1]
                label_y = y.iloc[-1]
                self._drift_label = self._axes['force'].text(label_x, label_y, 'drift', color=color, verticalalignment='center')

    def set_marker(self, label, value):
        if label in self._markers:
            line, text = self._markers.pop(label)
            line.remove()
            text.remove()
        if value is not None:
            axes = self._axes['force']
            color = self.COLORS['marker_others']
            if 'marker_' + label in self.COLORS:
                color = self.COLORS['marker_' + label]
            line = axes.axvline(value, color=color)
            text = axes.annotate(label, xy=(value, 1), xycoords=('data', 'axes fraction'), rotation=90, verticalalignment='top', color=color)
            self._markers[label] = line, text

    def draw(self):

        visibility = {
            'plot_force': self.main_window.plot_smpsignal_action.isChecked(),
            'plot_drift': self.main_window.plot_drift_action.isChecked(),
            'marker_surface': self.main_window.plot_surface_and_ground_action.isChecked(),
            'marker_ground': self.main_window.plot_surface_and_ground_action.isChecked(),
            'marker_drift_begin': self.main_window.plot_drift_action.isChecked(),
            'marker_drift_end': self.main_window.plot_drift_action.isChecked(),
            'marker_others': self.main_window.plot_markers_action.isChecked(),
            'plot_density': False,
            'plot_ssa': False
        }
        for key, action in self.main_window.plot_density_actions.items():
            visibility['plot_density_' + key] = action.isChecked()
            visibility['plot_density'] = visibility['plot_density'] or action.isChecked()
        for key, action in self.main_window.plot_ssa_actions.items():
            visibility['plot_ssa_' + key] = action.isChecked()
            visibility['plot_ssa'] = visibility['plot_ssa'] or action.isChecked()
        self._axes['force'].yaxis.set_visible(visibility['plot_force'])
        self._axes['ssa'].yaxis.set_visible(visibility['plot_ssa'])
        self._axes['density'].yaxis.set_visible(visibility['plot_density'])

        outward = 60 if visibility['plot_ssa'] and visibility['plot_density'] else 0
        self._axes['density'].spines['right'].set_position(('outward', outward))

        for label, lines in self._plots.items():
            vis = visibility['plot_' + label]
            for ll in lines:
                ll.set_visible(vis)
            if label == 'drift' and self._drift_label:
                self._drift_label.set_visible(vis)

        for label, (line, text) in self._markers.items():
            vis = visibility['marker_others']
            if 'marker_' + label in visibility:
                vis = visibility['marker_' + label]
            line.set_visible(vis)
            text.set_visible(vis)

        super(PlotCanvas, self).draw()

    def set_limits(self):
        prefs = self.main_window.preferences
        distance_axis_limits = (prefs.distance_axis_from, prefs.distance_axis_to) if prefs.distance_axis_fix else None
        force_axis_limits = (prefs.force_axis_from, prefs.force_axis_to) if prefs.force_axis_fix else None
        ssa_axis_limits = (prefs.ssa_axis_from, prefs.ssa_axis_to) if prefs.ssa_axis_fix else None
        density_axis_limits = (prefs.density_axis_from, prefs.density_axis_to) if prefs.density_axis_fix else None

        if distance_axis_limits:
            self._axes['force'].set_xlim(*distance_axis_limits)
        else:
            self._axes['force'].autoscale(axis='x')

        if force_axis_limits:
            self._axes['force'].set_ylim(*force_axis_limits)
        else:
            self._axes['force'].autoscale(axis='y')

        if ssa_axis_limits:
            self._axes['ssa'].set_ylim(*ssa_axis_limits)
        else:
            self._axes['ssa'].autoscale(axis='y')

        if density_axis_limits:
            self._axes['density'].set_ylim(*density_axis_limits)
        else:
            self._axes['density'].autoscale(axis='y')

    def mouse_button_pressed(self, event):
        log.debug('context click. x={}'.format(event))
        if event.button == 3:
            # Save distance value where the click was
            self._clicked_distance = event.xdata
            cursor = QCursor()
            self.menu = self.build_menu()
            self.menu.popup(cursor.pos())

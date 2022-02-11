import logging
from os.path import expanduser, dirname, abspath, join
from string import Template

from PyQt5.QtCore import QRect, Qt, QSettings, QSize
from PyQt5.QtGui import QIcon, QDoubleValidator, QValidator
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar

import snowmicropyn
import snowmicropyn.pyngui.icons
import snowmicropyn.pyngui.kml
import snowmicropyn.tools
from snowmicropyn.pyngui.document import Document
from snowmicropyn.pyngui.globals import APP_NAME, VERSION, GITHASH
from snowmicropyn.pyngui.plot_canvas import PlotCanvas
from snowmicropyn.pyngui.preferences import Preferences, PreferencesDialog
from snowmicropyn.pyngui.export_window import ExportSettings, ExportDialog
from snowmicropyn.pyngui.sidebar import SidebarWidget
from snowmicropyn.pyngui.superpos_canvas import SuperposCanvas
from snowmicropyn.derivatives import parameterizations

log = logging.getLogger('pyngui')

class MainWindow(QMainWindow):
    SETTING_LAST_DIRECTORY = 'MainFrame/last_directory'
    SETTING_GEOMETRY = 'MainFrame/geometry'
    SETTING_PLOT_SMPSIGNAL = 'MainFrame/plot/smpsignal'
    SETTING_PLOT_SURFACE_AND_GROUND = 'MainFrame/plot/surface+ground'
    SETTING_PLOT_MARKERS = 'MainFrame/plot/markers'
    SETTING_PLOT_DRIFT = 'MainFrame/plot/drift'
    SETTING_PLOT_DENSITY_ROOT = 'MainFrame/plot/density_'
    SETTING_PLOT_SSA_ROOT = 'MainFrame/plot/ssa_'

    DEFAULT_GEOMETRY = QRect(100, 100, 800, 600)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle(APP_NAME)

        self.notify_dialog = NotificationDialog()
        self.marker_dialog = MarkerDialog(self)
        self.prefs_dialog = PreferencesDialog(parameterizations)
        self.export_dialog = ExportDialog()

        self.documents = []
        self.preferences = Preferences.load()
        self.params = snowmicropyn.params

        homedir = expanduser('~')
        self._last_directory = QSettings().value(self.SETTING_LAST_DIRECTORY, defaultValue=homedir)

        self.plot_canvas = PlotCanvas(main_window=self)
        self.superpos_canvas = SuperposCanvas(self)

        self.plot_toolbar = NavigationToolbar(self.plot_canvas, self)
        self.plot_toolbar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.superpos_toolbar = NavigationToolbar(self.superpos_canvas, self)
        self.superpos_toolbar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.superpos_toolbar.setVisible(False)

        self.addToolBar(Qt.BottomToolBarArea, self.plot_toolbar)
        self.addToolBar(Qt.BottomToolBarArea, self.superpos_toolbar)

        self.sidebar = SidebarWidget(self)

        self.plot_stacked_widget = QStackedWidget(self)
        self.plot_stacked_widget.addWidget(self.plot_canvas)
        self.plot_stacked_widget.addWidget(self.superpos_canvas)

        splitter = QSplitter()
        splitter.addWidget(self.plot_stacked_widget)
        splitter.addWidget(self.sidebar)

        self.stacked_widget = QStackedWidget(self)
        self.stacked_widget.addWidget(NoDocWidget())
        self.stacked_widget.addWidget(splitter)

        self.setCentralWidget(self.stacked_widget)

        self.plot_density_actions = {}
        self.plot_ssa_actions = {}
        for key, par in self.params.items():
            self.plot_density_actions[key] = QAction(par.name, self)
            if hasattr(par, 'ssa'): # Some parameterizations are only for the density
                self.plot_ssa_actions[key] = QAction(par.name, self)

        self.about_action = QAction('About', self)
        self.quit_action = QAction('Quit', self)
        self.preferences_action = QAction('Preferences', self)
        self.open_action = QAction('&Open', self)
        self.save_action = QAction('&Save', self)
        self.saveall_action = QAction('Save &All', self)
        self.drop_action = QAction('&Drop', self)
        self.exportall_action = QAction('&Export &All', self)
        self.export_niviz_action = QAction('Export for niViz...', self)
        self.next_action = QAction('Next Profile', self)
        self.previous_action = QAction('Previous Profile', self)
        self.plot_smpsignal_action = QAction('Plot SMP Signal', self)
        self.plot_surface_and_ground_action = QAction('Plot Surface && Ground', self)
        self.plot_markers_action = QAction('Plot other Markers', self)
        self.plot_drift_action = QAction('Plot Drift', self)
        self.detect_surface_action = QAction('Auto Detect Surface', self)
        self.detect_ground_action = QAction('Auto Detect Ground', self)
        self.add_marker_action = QAction('New Marker', self)
        self.kml_action = QAction('Export to KML', self)
        self.show_log_action = QAction('Show Log', self)
        self.superpos_action = QAction('Superposition', self)

        self.profile_combobox = QComboBox(self)
        self.profile_combobox.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self._init_ui()
        self.switch_document()

    def _init_ui(self):
        geometry = QSettings().value('MainFrame/geometry', defaultValue=MainWindow.DEFAULT_GEOMETRY)
        self.setGeometry(geometry)

        self.profile_combobox.currentIndexChanged.connect(self.switch_document)

        action = self.about_action
        action.setStatusTip('About ' + APP_NAME)
        action.triggered.connect(self._about_triggered)

        action = self.quit_action
        action.setIcon(QIcon(':/icons/shutdown.png'))
        action.setShortcut('Ctrl+Q')
        action.setStatusTip('Quit application')
        # Call MainFrame.close when user wants to quit the application,
        # causing a call of MainFrame.closeEvent where we close all
        # other windows too (like LogWindow for example), which quits
        # the application itself
        action.triggered.connect(self.close)

        action = self.preferences_action
        action.setIcon(QIcon(':/icons/settings.png'))
        action.setShortcut('Ctrl+;')
        action.setStatusTip('Preferences')
        action.triggered.connect(self._preferences_triggered)

        action = self.open_action
        action.setIcon(QIcon(':/icons/open.png'))
        action.setShortcut('Ctrl+O')
        action.setStatusTip('Open')
        action.triggered.connect(self._open_triggered)

        action = self.save_action
        action.setIcon(QIcon(':/icons/save.png'))
        action.setShortcut('Ctrl+S')
        action.setStatusTip('Save')
        action.triggered.connect(self._save_triggered)

        action = self.saveall_action
        action.setIcon(QIcon(':/icons/saveall.png'))
        action.setShortcut('Ctrl+Alt+S')
        action.setStatusTip('Save All Profiles')
        action.triggered.connect(self._saveall_triggered)

        action = self.drop_action
        action.setIcon(QIcon(':/icons/drop.png'))
        action.setShortcut('Ctrl+X')
        action.setStatusTip('Drop Profile')
        action.triggered.connect(self._drop_triggered)

        action = self.exportall_action
        action.setIcon(QIcon(':/icons/csv.png'))
        action.setShortcut('Ctrl+E')
        action.setStatusTip('Export All Profiles to CSV')
        action.triggered.connect(self._exportall_triggered)

        action = self.export_niviz_action
        action.setIcon(QIcon(':/icons/csv.png'))
#        action.setShortcut('Ctrl+E')
        action.setStatusTip('Export Profile to CSV readable by niViz')
        action.triggered.connect(self._export_niviz_triggered)

        action = self.next_action
        action.setIcon(QIcon(':/icons/next.png'))
        action.setShortcut('Ctrl+N')
        action.setStatusTip('Next Profile')
        action.triggered.connect(self._next_triggered)

        action = self.previous_action
        action.setIcon(QIcon(':/icons/previous.png'))
        action.setShortcut('Ctrl+P')
        action.setStatusTip('Previous Profile')
        action.triggered.connect(self._previous_triggered)

        action = self.detect_surface_action
        action.setIcon(QIcon(':/icons/detect_surface.png'))
        action.setShortcut('Ctrl+T')
        action.setStatusTip('Auto Detection of Surface')
        action.triggered.connect(self._detect_surface_triggered)

        action = self.detect_ground_action
        action.setIcon(QIcon(':/icons/detect_ground.png'))
        action.setShortcut('Ctrl+G')
        action.setStatusTip('Auto Detection of Ground')
        action.triggered.connect(self._detect_ground_triggered)

        def force_plot():
            self.update()

        action = self.plot_smpsignal_action
        action.setShortcut('Alt+P')
        action.setStatusTip('Plot SMP Signal')
        action.setCheckable(True)
        action.triggered.connect(force_plot)
        setting = MainWindow.SETTING_PLOT_SMPSIGNAL
        enabled = QSettings().value(setting, defaultValue=True, type=bool)
        action.setChecked(enabled)

        action = self.plot_surface_and_ground_action
        action.setShortcut('Alt+G')
        action.setStatusTip('Plot Surface + Ground')
        action.setCheckable(True)
        action.triggered.connect(force_plot)
        setting = MainWindow.SETTING_PLOT_SURFACE_AND_GROUND
        enabled = QSettings().value(setting, defaultValue=True, type=bool)
        action.setChecked(enabled)

        action = self.plot_markers_action
        action.setShortcut('Alt+M')
        action.setStatusTip('Plot Markers')
        action.setCheckable(True)
        action.triggered.connect(force_plot)
        setting = MainWindow.SETTING_PLOT_MARKERS
        enabled = QSettings().value(setting, defaultValue=True, type=bool)
        action.setChecked(enabled)

        action = self.plot_drift_action
        action.setShortcut('Alt+R')
        action.setStatusTip('Plot Drift')
        action.setCheckable(True)
        action.triggered.connect(force_plot)
        setting = MainWindow.SETTING_PLOT_DRIFT
        enabled = QSettings().value(setting, defaultValue=False, type=bool)
        action.setChecked(enabled)

        action = self.add_marker_action
        action.setShortcut('Ctrl+M')
        action.setIcon(QIcon(':/icons/marker_add.png'))
        action.setStatusTip('Add New Marker...')
        action.triggered.connect(lambda checked: self.new_marker(default_value=0))

        action = self.kml_action
        action.setIcon(QIcon(':/icons/kml.png'))
        action.setShortcut('Ctrl+K')
        action.setStatusTip('Export to KML')
        action.triggered.connect(self._kml_triggered)

        action = self.show_log_action
        action.setIcon(QIcon(':/icons/logs.png'))
        action.setShortcut('Ctrl+L')
        action.setStatusTip('Show Log Window')
        action.triggered.connect(self._showlog_triggered)

        action = self.superpos_action
        action.setIcon(QIcon(':/icons/superpos.png'))
        action.setStatusTip('Show Superposition')
        action.triggered.connect(self._show_superpos)
        action.setCheckable(True)

        menubar = self.menuBar()

        menu = menubar.addMenu('&File')
        menu.addAction(self.about_action)
        menu.addAction(self.quit_action)
        menu.addAction(self.open_action)
        menu.addAction(self.save_action)
        menu.addAction(self.saveall_action)
        menu.addSeparator()
        menu.addAction(self.exportall_action)
        menu.addAction(self.export_niviz_action)
        menu.addSeparator()
        menu.addAction(self.drop_action)
        menu.addSeparator()
        menu.addAction(self.preferences_action)

        menu = menubar.addMenu('&View')
        menu.addAction(self.plot_smpsignal_action)

        density_menu = menu.addMenu('Plot &Density')
        for key, par in self.params.items():
            #action.setShortcut('Alt+D,P')
            action = self.plot_density_actions[key]
            action.setStatusTip('Show Density according to ' + par.name)
            action.setCheckable(True)
            action.triggered.connect(force_plot)
            setting = MainWindow.SETTING_PLOT_DENSITY_ROOT + key
            enabled = QSettings().value(setting, defaultValue=False, type=bool)
            action.setChecked(enabled)
            density_menu.addAction(action)

        ssa_menu = menu.addMenu('Plot &SSA')
        for key, par in self.params.items():
            if not hasattr(par, 'ssa'):
                continue
            #action.setShortcut('Alt+A,P')
            action = self.plot_ssa_actions[key]
            action.setStatusTip('Show SSA according to ' + par.name)
            action.setCheckable(True)
            action.triggered.connect(force_plot)
            setting = MainWindow.SETTING_PLOT_SSA_ROOT + key
            enabled = QSettings().value(setting, defaultValue=False, type=bool)
            action.setChecked(enabled)
            ssa_menu.addAction(action)

        menu.addSeparator()
        menu.addAction(self.plot_surface_and_ground_action)
        menu.addSeparator()
        menu.addAction(self.plot_markers_action)
        menu.addSeparator()
        menu.addAction(self.plot_drift_action)
        menu.addSeparator()
        menu.addAction(self.next_action)
        menu.addAction(self.previous_action)
        menu.addSeparator()
        menu.addAction(self.show_log_action)

        menu = menubar.addMenu('&Profile')
        menu.addAction(self.detect_surface_action)
        menu.addAction(self.detect_ground_action)
        menu.addAction(self.add_marker_action)

        toolbar = self.addToolBar('Exit')
        toolbar.addAction(self.quit_action)
        toolbar.addAction(self.preferences_action)
        toolbar.addSeparator()
        toolbar.addAction(self.open_action)
        toolbar.addAction(self.drop_action)
        toolbar.addAction(self.save_action)
        toolbar.addAction(self.exportall_action)
        toolbar.addSeparator()
        toolbar.addAction(self.detect_surface_action)
        toolbar.addAction(self.detect_ground_action)
        toolbar.addAction(self.add_marker_action)
        toolbar.addSeparator()
        toolbar.addAction(self.previous_action)
        toolbar.addWidget(self.profile_combobox)
        toolbar.addAction(self.next_action)
        toolbar.addSeparator()
        toolbar.addAction(self.kml_action)
        toolbar.addAction(self.saveall_action)
        toolbar.addAction(self.superpos_action)
        toolbar.setContextMenuPolicy(Qt.PreventContextMenu)

    def closeEvent(self, event):
        log.info('Saving settings of MainWindow')
        QSettings().setValue(MainWindow.SETTING_GEOMETRY, self.geometry())
        QSettings().setValue(MainWindow.SETTING_LAST_DIRECTORY, self._last_directory)
        QSettings().setValue(MainWindow.SETTING_PLOT_SMPSIGNAL, self.plot_smpsignal_action.isChecked())
        QSettings().setValue(MainWindow.SETTING_PLOT_SURFACE_AND_GROUND, self.plot_surface_and_ground_action.isChecked())
        QSettings().setValue(MainWindow.SETTING_PLOT_MARKERS, self.plot_markers_action.isChecked())
        QSettings().setValue(MainWindow.SETTING_PLOT_DRIFT, self.plot_drift_action.isChecked())
        for key, par in self.params.items():
            QSettings().setValue(MainWindow.SETTING_PLOT_DENSITY_ROOT + key, self.plot_density_actions[key].isChecked())
            if hasattr(par, 'ssa'):
                QSettings().setValue(MainWindow.SETTING_PLOT_SSA_ROOT + key, self.plot_ssa_actions[key].isChecked())
        QSettings().sync()
        # This is the main window. In case it's closed, we close all
        # other windows too which results in quitting the application
        log.removeHandler(log.handlers[1]) # detach LogWindow to not attempt to close it twice
        QApplication.instance().closeAllWindows()

    def _open_triggered(self):
        cap = "Open Profile(s)"
        filtr = "pnt Files (*.pnt)"
        opts = QFileDialog.ReadOnly
        startdir = self._last_directory
        files, _ = QFileDialog.getOpenFileNames(self, cap, startdir, filtr, options=opts)
        if files:
            self.open_pnts(files)

        # Save directory where we were to open at same place next time
        # for user's convenience
        if self.current_document:
            self._last_directory = dirname(self.current_document.profile.pnt_file)

    def open_pnts(self, files):
        new_docs = []
        for f in files:
            p = snowmicropyn.Profile.load(f)
            doc = Document(p)
            doc.recalc_derivatives()
            new_docs.append(doc)
            self.superpos_canvas.add_doc(doc)
        self.documents.extend(new_docs)
        first_new_index = self.profile_combobox.count()
        self.profile_combobox.addItems([d.profile.name for d in new_docs])

        # Set active to first of newly loaded profiles, this causes
        # also a call of method switch_document triggered by the combobox.
        self.profile_combobox.setCurrentIndex(first_new_index)

    def _save_triggered(self):
        self.current_document.profile.save()
        f = self.current_document.profile.ini_file
        self.notify_dialog.notifyFilesWritten([f],
            'These files contain only meta data and do not alter the dataset whatsoever.')

    def _saveall_triggered(self):
        for doc in self.documents:
            doc.profile.save()
        f = [doc.profile.ini_file for doc in self.documents]
        self.notify_dialog.notifyFilesWritten(f,
            'These files contain only meta data and do not alter the dataset whatsoever.')

    def _exportall_triggered(self):
        files=[]
        for doc in self.documents:
            p = doc.profile

            if self.preferences.export_samples:
                samples_file = p.export_samples()
                files.append(samples_file)
            meta_file = p.export_meta(include_pnt_header=True)
            files.append(meta_file)
            derivatives_file = p.export_derivatives(parameterization=self.preferences.export_parameterization)
            files.append(derivatives_file)
            par = parameterizations[self.preferences.export_parameterization]
        self.notify_dialog.notifyFilesWritten(files,
            'Only the parameterization chosen in your user settings (' + par.name +
            ') was exported to avoid mixed resolutions (here: window_size=' +
            str(par.window_size) + ', overlap=' + str(par.overlap) + ').')

    def _export_niviz_triggered(self):
        export_settings = ExportSettings.load()
        perform_export = self.export_dialog.exportForNiviz(export_settings)
        if perform_export:
            log.info('Exporting CSV for niViz (angle=' + str(export_settings.export_slope_angle) + \
                ', thinning=' + str(export_settings.export_data_thinning) + ', stretch=' + \
                str(export_settings.export_stretch_factor) + ')')
            p = self.current_document.profile
            export_settings.save()
            samples_file = p.export_samples_niviz(export_settings)
            self.notify_dialog.notifyFilesWritten([samples_file],
                'Do not forget to enable the SMP measurement in the niViz settings (Settings · Simple Profile · Configure additional parameters · + · "smp")')

    @property
    def current_document(self):
        i = self.profile_combobox.currentIndex()
        return self.documents[i] if i != -1 else None

    def _drop_triggered(self):
        doc = self.current_document
        self.superpos_canvas.remove_doc(doc)
        i = self.profile_combobox.currentIndex()
        del self.documents[i]
        # We just remove the item from the combobox, which causes
        # a call of method ``switch_profile``. The work is done there.
        self.profile_combobox.removeItem(i)

    def _next_triggered(self):
        # Fix for https://github.com/slf-dot-ch/snowmicropyn/issues/7
        # In case the lineedit widget to edit a markers value in the sidebar
        # has the focus, we clear that focus first, otherwise the marker would
        # set on the new profile instead.
        w = QApplication.focusWidget()
        if w:
            w.clearFocus()
        QApplication.processEvents()

        i = self.profile_combobox.currentIndex() + 1
        size = self.profile_combobox.count()
        if i > size - 1:
            i = 0
        # We just set a new index on the combobox, which causes a call
        # of method ``switch_profile``. The work is done there.
        self.profile_combobox.setCurrentIndex(i)

    def _previous_triggered(self):
        log.debug('method previous_profile called')

        # Fix for https://github.com/slf-dot-ch/snowmicropyn/issues/7
        # In case the lineedit widget to edit a markers value in the sidebar
        # has the focus, we clear that focus first, otherwise the marker would
        # set on the new profile instead.
        w = QApplication.focusWidget()
        if w:
            w.clearFocus()
        QApplication.processEvents()

        i = self.profile_combobox.currentIndex() - 1
        size = self.profile_combobox.count()
        if i < 0:
            i = size - 1
        # We just set a new index on the combobox, which causes a call
        # of method ``switch_profile``. The work is done there.
        self.profile_combobox.setCurrentIndex(i)

    def _detect_ground_triggered(self):
        doc = self.current_document
        doc.profile.detect_ground()
        self.set_marker('ground', doc.profile.ground)
        self.update()

    def _detect_surface_triggered(self):
        doc = self.current_document
        doc.profile.detect_surface()
        self.set_marker('surface', doc.profile.surface)
        self.update()

    @staticmethod
    def _about_triggered():
        # Read the content of the file about.html located in the same directory
        # as this file, read its content and use string.Template to replace
        # some content
        here = dirname(abspath(__file__))
        with open(join(here, 'about.html'), encoding='utf-8') as f:
            content = f.read()
        githash = GITHASH if GITHASH else 'None'
        tmpl = Template(content)
        content = tmpl.substitute(app_name=APP_NAME, version=VERSION, hash=githash)

        label = QLabel(content)
        label.setOpenExternalLinks(True)

        layout = QVBoxLayout()
        layout.addWidget(label)

        # noinspection PyArgumentList
        dialog = QDialog()
        dialog.setWindowTitle('About')
        dialog.setLayout(layout)
        dialog.exec_()

    def _showlog_triggered(self):
        # We must not keep a reference to LogWindow (crashes), so
        # we find this reference here:
        log.handlers[1].toTop()

    def _kml_triggered(self):
        profile = self.current_document.profile
        f = join(dirname(profile.pnt_file), 'snowmicropyn_profiles.kml')
        snowmicropyn.pyngui.kml.export2kml(f, self.documents)
        self.notify_dialog.notifyFilesWritten(f)

    def _preferences_triggered(self):
        modified = self.prefs_dialog.modifyPreferences(self.preferences)
        if modified:
            self.preferences.save()
            self.plot_canvas.set_limits()
            self.plot_canvas.draw()
            self.plot_toolbar.update()

    def switch_document(self):
        # Fix for https://github.com/slf-dot-ch/snowmicropyn/issues/7
        # In case the lineedit widget to edit a markers value in the sidebar
        # has the focus, we clear that focus first, otherwise the marker would
        # set on the new profile instead.
        w = QApplication.focusWidget()
        if w:
            w.clearFocus()
        QApplication.processEvents()

        doc = self.current_document
        log.debug('Switching to document: {}'.format(doc.profile if doc else None))

        at_least_one = len(self.documents) > 0
        multiple = len(self.documents) >= 2
        self.profile_combobox.setEnabled(at_least_one)
        self.previous_action.setEnabled(multiple)
        self.next_action.setEnabled(multiple)
        self.drop_action.setEnabled(at_least_one)
        self.save_action.setEnabled(at_least_one)
        self.saveall_action.setEnabled(at_least_one)
        self.exportall_action.setEnabled(at_least_one)
        self.export_niviz_action.setEnabled(at_least_one)
        self.detect_surface_action.setEnabled(at_least_one)
        self.detect_ground_action.setEnabled(at_least_one)
        self.add_marker_action.setEnabled(at_least_one)
        self.kml_action.setEnabled(at_least_one)

        self.stacked_widget.setCurrentIndex(1 if at_least_one else 0)

        self.sidebar.set_document(doc)

        if doc is not None:
            self.calc_drift()

        self.plot_canvas.set_document(doc)
        self.plot_canvas.draw()
        # Reset toolbar history
        self.plot_toolbar.update()

        self.superpos_canvas.set_active_doc(doc)

    # This method is called by PlotCanvas and Sidebar when a marker is set to
    # a new value. This method then causes the required update of visualization
    def set_marker(self, label, value):
        doc = self.current_document
        p = doc.profile
        if value is not None:
            value = float(value)
        log.info('Setting marker {} of profile {} to {}'.format(repr(label), p.name, value))
        p.set_marker(label, value)

        self.sidebar.set_marker(label, value)
        self.plot_canvas.set_marker(label, value)

        if label in ('surface', 'drift_begin', 'drift_end'):
            self.calc_drift()
            self.plot_canvas.set_plot('force', 'drift', (doc._fit_x, doc._fit_y))

        if label in ('surface', 'ground'):
            doc.recalc_derivatives()
            for key, par in snowmicropyn.params.items():
                self.plot_canvas.set_plot('density', 'density_' + key,
                    (doc.derivatives[key]['distance'], doc.derivatives[key][par.shortname + '_density']))
                if hasattr(par, 'ssa'):
                    self.plot_canvas.set_plot('ssa', 'ssa_' + key,
                        (doc.derivatives[key]['distance'], doc.derivatives[key][par.shortname + '_ssa']))

        self.plot_canvas.draw()

    def new_marker(self, default_value=0):
        name, value = self.marker_dialog.getMarker(default_value=default_value)
        if name is not None:
            self.set_marker(name, value)

    def calc_drift(self):
        p = self.current_document.profile

        try:
            begin = p.marker('drift_begin')
            begin_label = 'Marker drift_begin'
        except KeyError:
            # Skip the first few values of profile fo drift calculation
            begin = p.samples.distance.iloc[10]
            begin_label = 'Begin of Profile'

        try:
            end = p.marker('drift_end')
            end_label = 'Marker drift_end'
        except KeyError:
            try:
                end = p.marker('surface')
                end_label = 'Marker surface'
            except KeyError:
                end = p.samples.distance.iloc[-1]
                end_label = 'End of Profile'

        log.debug('Calculating drift from {} to {}'.format(begin, end))

        # Flip begin and end to make sure begin is always smaller then end
        if end < begin:
            begin, end = end, begin

        drift_range = p.samples[p.samples.distance.between(begin, end)]

        x_fit, y_fit, drift, offset, noise = snowmicropyn.tools.lin_fit(drift_range.distance,
                                                                        drift_range.force)
        self.current_document._fit_x = x_fit
        self.current_document._fit_y = y_fit
        self.current_document._dirft = drift
        self.current_document._offset = offset
        self.current_document._noise = noise

        self.sidebar.set_drift(begin_label, end_label, drift, offset, noise)

    def update(self):
        self.plot_canvas.draw()

    def _show_superpos(self, checked):
        log.info('Show superposition view: {}'.format(checked))
        self.plot_stacked_widget.setCurrentIndex(1 if checked else 0)

        self.superpos_toolbar.setVisible(checked)
        self.plot_toolbar.setVisible(not checked)

    def all_marker_labels(self):
        labels = set()
        for d in self.documents:
            labels.update(d.profile.markers.keys())
        return labels

# The NoDocWidget is visible when no document is open. It contains the SLF logo.
class NoDocWidget(QWidget):

    def __init__(self, parent=None):
        # noinspection PyArgumentList
        super(NoDocWidget, self).__init__(parent)
        self.label = QLabel()
        icon = QIcon(':/icons/slflogo@2x.png')
        pixmap = icon.pixmap(icon.actualSize(QSize(512, 512)))
        pixmap.setDevicePixelRatio(3)
        self.label.setPixmap(pixmap)
        layout = QVBoxLayout()
        layout.addWidget(self.label, alignment=Qt.AlignHCenter)
        self.setLayout(layout)


class NotificationDialog(QDialog):
    def __init__(self, *args):
        super(NotificationDialog, self).__init__(*args)

        self.hint_label = QLabel()
        self.hint_label.setWordWrap(True)
        self.content_textedit = QTextEdit()
        self.content_textedit.setReadOnly(True)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        close_button.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))

        layout = QVBoxLayout()
        layout.addWidget(self.hint_label)
        layout.addWidget(self.content_textedit)
        layout.addWidget(close_button)
        layout.setAlignment(close_button, Qt.AlignRight)

        self.setLayout(layout)
        self.resize(500, 200)

    def notifyFilesWritten(self, files, hint_text=''):
        if isinstance(files, str):
            files = [files]
        self.setWindowTitle('Notification')
        multipe = len(files) > 1
        if hint_text != '':
            hint_text = '<b>NOTE:</b> ' + hint_text + '<br><br>'
        hint_text = hint_text + 'File{} written:'.format('s' if multipe else '')
        self.hint_label.setText(hint_text)
        self.content_textedit.setText('\n'.join([str(f) for f in files]))
        self.exec()


class MarkerDialog(QDialog):
    def __init__(self, parent, *args):
        super(MarkerDialog, self).__init__(parent, *args)
        self.mainwin = parent
        self.setWindowTitle('Add Marker')

        self.label_editline = QLineEdit()
        self.label_editline.setMinimumWidth(150)
        self.value_lineedit = QLineEdit()
        self.value_lineedit.setMinimumWidth(150)
        self.validator = QDoubleValidator()
        self.value_lineedit.setValidator(self.validator)
        ok_and_cancel = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(ok_and_cancel)

        def check():
            log.info('Checking for already existing marker labels')
            ok_button = self.button_box.button(QDialogButtonBox.Ok)
            name = self.label_editline.text()
            existing_markers = [k for k, v in self.mainwin.current_document.profile.markers.items()]
            valid_name = bool(name) and (name not in existing_markers)
            valid_value = self.validator.validate(self.value_lineedit.text(), 0)[
                              0] == QValidator.Acceptable
            ok_button.setEnabled(valid_name and valid_value)

        self.label_editline.textChanged.connect(check)
        self.value_lineedit.textChanged.connect(check)

        self.button_box.rejected.connect(self.reject)
        self.button_box.accepted.connect(self.accept)

        form_layout = QFormLayout()
        form_layout.addRow('Label:', self.label_editline)
        form_layout.addRow('Value:', self.value_lineedit)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.button_box)
        self.setLayout(main_layout)

    def getMarker(self, default_value, default_label='label'):
        self.value_lineedit.setText(str(default_value))
        # We need setting to '' first, cause when we just setting  default_label
        # again, no textChanged signal is emitted and therefore no check for
        # already existing marker labels is skipped!
        self.label_editline.setText('')
        self.label_editline.setText(default_label)
        self.label_editline.setFocus()
        self.label_editline.selectAll()
        result = self.exec()
        if result == QDialog.Accepted:
            name = self.label_editline.text()
            value = float(self.value_lineedit.text())
            return name, value
        return None, None

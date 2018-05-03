import logging
from os.path import expanduser, dirname, abspath, join
from string import Template

from PyQt5.QtCore import QRect, Qt, QSettings, QSize
from PyQt5.QtGui import QIcon, QDoubleValidator, QValidator
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar

import snowmicropyn.examiner.icons
import snowmicropyn.examiner.kml
from snowmicropyn import Profile
from snowmicropyn.examiner.document import Document
from snowmicropyn.examiner.globals import APP_NAME, VERSION, GITHASH
from snowmicropyn.examiner.map_window import MapWindow
from snowmicropyn.examiner.plot_canvas import PlotCanvas
from snowmicropyn.examiner.sidebar import SidebarWidget

# This import statement is important, no icons appear in case it's missing!
import snowmicropyn.examiner.icons

log = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    SETTING_LAST_DIRECTORY = 'MainFrame/last_directory'
    SETTING_GEOMETRY = 'MainFrame/geometry'
    SETTING_PLOT_SURFACE = 'MainFrame/plot/surface'
    SETTING_PLOT_GROUND = 'MainFrame/plot/ground'
    SETTING_PLOT_MARKERS = 'MainFrame/plot/markers'
    SETTING_PLOT_SSA_PROKSCH2015 = 'MainFrame/plot/ssa_proksch2015'
    SETTING_PLOT_DENSITY_PROKSCH2015 = 'MainFrame/plot/density_proksch2015'

    DEFAULT_GEOMETRY = QRect(100, 100, 800, 600)

    def __init__(self, log_window, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle(APP_NAME)

        self.log_window = log_window
        self.map_window = MapWindow()
        self.notify_dialog = NotificationDialog()
        self.marker_dialog = MarkerDialog(self)

        self.documents = []

        self._last_directory = QSettings().value(self.SETTING_LAST_DIRECTORY, defaultValue=expanduser('~'))

        self.plotcanvas = PlotCanvas(main_window=self)

        self.plotcanvas.toolbar = NavigationToolbar(self.plotcanvas, self)
        self.addToolBar(Qt.BottomToolBarArea, self.plotcanvas.toolbar)

        self.sidebar = SidebarWidget(self)

        splitter = QSplitter()
        splitter.addWidget(self.plotcanvas)
        splitter.addWidget(self.sidebar)

        self.stacked_widget = QStackedWidget(self)
        self.stacked_widget.addWidget(NoDocWidget())
        self.stacked_widget.addWidget(splitter)

        self.setCentralWidget(self.stacked_widget)

        self.about_action = QAction('About', self)
        self.quit_action = QAction('Quit', self)
        self.settings_action = QAction('Settings', self)
        self.open_action = QAction('&Open', self)
        self.save_action = QAction('&Save', self)
        self.saveall_action = QAction('Save &All', self)
        self.drop_action = QAction('&Drop', self)
        self.export_action = QAction('&Export', self)
        self.next_action = QAction('Next Profile', self)
        self.previous_action = QAction('Previous Profile', self)
        self.plot_surface_action = QAction('Plot Surface', self)
        self.plot_ground_action = QAction('Plot Ground', self)
        self.plot_markers_action = QAction('Plot other Markers', self)
        self.plot_ssa_proksch2015_action = QAction('Proksch 2015', self)
        self.plot_density_proksch2015_action = QAction('Proksch 2015', self)
        self.detect_surface_action = QAction('Detect Surface', self)
        self.detect_ground_action = QAction('Detect Ground', self)
        self.add_marker_action = QAction('New Marker', self)
        self.map_action = QAction('Show Map', self)
        self.kml_action = QAction('Export to KML', self)
        self.show_log_action = QAction('Show Log', self)

        self.profile_combobox = QComboBox(self)

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
        # Call MainFrame.close when user want's to quit the application,
        # causing a call of MainFrame.closeEvent where we close all
        # other windows too (like LogWindow for example), which quits
        # the application itself
        action.triggered.connect(self.close)

        action = self.settings_action
        action.setIcon(QIcon(':/icons/settings.png'))
        action.setShortcut('Ctrl+;')
        action.setStatusTip('Settings')

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

        action = self.export_action
        action.setIcon(QIcon(':/icons/csv.png'))
        action.setShortcut('Ctrl+E')
        action.setStatusTip('Export Profile to CSV')
        action.triggered.connect(self._export_triggered)

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
            self.switch_document()

        action = self.plot_surface_action
        action.setShortcut('Alt+S')
        action.setStatusTip('Plot Surface')
        action.setCheckable(True)
        action.triggered.connect(force_plot)
        setting = MainWindow.SETTING_PLOT_SURFACE
        enabled = QSettings().value(setting, defaultValue=True, type=bool)
        action.setChecked(enabled)

        action = self.plot_ground_action
        action.setShortcut('Alt+G')
        action.setStatusTip('Plot Ground')
        action.setCheckable(True)
        action.triggered.connect(force_plot)
        setting = MainWindow.SETTING_PLOT_GROUND
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

        action = self.add_marker_action
        action.setShortcut('Ctrl+M')
        action.setIcon(QIcon(':/icons/marker_add.png'))
        action.setStatusTip('Add New Marker...')
        action.triggered.connect(lambda checked: self.add_marker(default_value=0))

        action = self.plot_ssa_proksch2015_action
        action.setShortcut('Alt+A,P')
        action.setStatusTip('Show SSA according Proksch 2015')
        action.setCheckable(True)
        action.triggered.connect(force_plot)
        setting = MainWindow.SETTING_PLOT_SSA_PROKSCH2015
        enabled = QSettings().value(setting, defaultValue=True, type=bool)
        action.setChecked(enabled)

        action = self.plot_density_proksch2015_action
        action.setShortcut('Alt+D,P')
        action.setStatusTip('Show Density according Proksch 2015')
        action.setCheckable(True)
        action.triggered.connect(force_plot)
        setting = MainWindow.SETTING_PLOT_DENSITY_PROKSCH2015
        enabled = QSettings().value(setting, defaultValue=True, type=bool)
        action.setChecked(enabled)

        action = self.map_action
        action.setIcon(QIcon(':/icons/map.png'))
        action.setShortcut('Ctrl+M')
        action.setStatusTip('Show Map')
        action.triggered.connect(self._showmap_triggered)

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

        menubar = self.menuBar()

        menu = menubar.addMenu('&File')
        menu.addAction(self.about_action)
        menu.addAction(self.quit_action)
        menu.addAction(self.open_action)
        menu.addAction(self.save_action)
        menu.addAction(self.saveall_action)
        menu.addSeparator()
        menu.addAction(self.export_action)
        menu.addSeparator()
        menu.addAction(self.drop_action)

        menu = menubar.addMenu('&View')
        menu.addAction(self.plot_surface_action)
        menu.addAction(self.plot_ground_action)
        menu.addAction(self.plot_markers_action)
        menu.addSeparator()

        ssa_menu = menu.addMenu('Plot &SSA')
        ssa_menu.addAction(self.plot_ssa_proksch2015_action)

        density_menu = menu.addMenu('Plot &Density')
        density_menu.addAction(self.plot_density_proksch2015_action)

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
        toolbar.addAction(self.settings_action)
        toolbar.addSeparator()
        toolbar.addAction(self.open_action)
        toolbar.addAction(self.drop_action)
        toolbar.addAction(self.save_action)
        toolbar.addAction(self.export_action)
        toolbar.addSeparator()
        toolbar.addAction(self.detect_surface_action)
        toolbar.addAction(self.detect_ground_action)
        toolbar.addAction(self.add_marker_action)
        toolbar.addSeparator()
        toolbar.addAction(self.previous_action)
        toolbar.addWidget(self.profile_combobox)
        toolbar.addAction(self.next_action)
        toolbar.addSeparator()
        toolbar.addAction(self.map_action)
        toolbar.addAction(self.kml_action)
        toolbar.addAction(self.saveall_action)

    def closeEvent(self, event):
        log.info('Saving settings of MainWindow')
        QSettings().setValue(MainWindow.SETTING_GEOMETRY, self.geometry())
        QSettings().setValue(MainWindow.SETTING_LAST_DIRECTORY, self._last_directory)
        QSettings().setValue(MainWindow.SETTING_PLOT_SURFACE, self.plot_surface_action.isChecked())
        QSettings().setValue(MainWindow.SETTING_PLOT_GROUND, self.plot_ground_action.isChecked())
        QSettings().setValue(MainWindow.SETTING_PLOT_MARKERS, self.plot_markers_action.isChecked())
        QSettings().setValue(MainWindow.SETTING_PLOT_SSA_PROKSCH2015, self.plot_ssa_proksch2015_action.isChecked())
        QSettings().setValue(MainWindow.SETTING_PLOT_DENSITY_PROKSCH2015, self.plot_density_proksch2015_action.isChecked())

        # This is the main window. In case it's closed, we close all
        # other windows too which results in quitting the application
        QApplication.instance().closeAllWindows()

    def _open_triggered(self):
        cap = "Open Profile(s)"
        filtr = "pnt Files (*.pnt)"
        opts = QFileDialog.ReadOnly
        startdir = self._last_directory
        # noinspection PyTypeChecker
        files, _ = QFileDialog.getOpenFileNames(self, cap, startdir, filtr, options=opts)
        if files:
            self.open_pnts(files)

        # Save directory where we were to open at same place next time
        # for user's convenience
        if self.current_document:
            self._last_directory = dirname(self.current_document.profile.pnt_filename)

    def open_pnts(self, files):
        new_docs = []
        for f in files:
            p = Profile.load(f)
            doc = Document(p)
            new_docs.append(doc)
        self.documents.extend(new_docs)
        first_new_index = self.profile_combobox.count()
        self.profile_combobox.addItems([d.profile.name for d in new_docs])

        # Set active to first of newly loaded profiles
        self.profile_combobox.setCurrentIndex(first_new_index)

    def _save_triggered(self):
        self.current_document.profile.save()
        f = self.current_document.profile.ini_filename
        self.notify_dialog.notifyFilesWritten([f])

    def _saveall_triggered(self):
        for doc in self.documents:
            doc.profile.save()
        f = [doc.profile.ini_filename for doc in self.documents]
        self.notify_dialog.notifyFilesWritten(f)

    def _export_triggered(self):
        p = self.current_document.profile
        meta_file = p.export_meta(include_pnt_header=True)
        samples_file = p.export_samples()
        p.model_shotnoise(save_to_file=True)
        p.model_ssa(save_to_file=True)
        self.notify_dialog.notifyFilesWritten([meta_file, samples_file])

    @property
    def current_document(self):
        i = self.profile_combobox.currentIndex()
        if i == -1:
            return None
        return self.documents[i]

    def _drop_triggered(self):
        log.debug('method drop_profile called')
        i = self.profile_combobox.currentIndex()
        del self.documents[i]
        # We just remove the item from the combobox, which causes
        # a call of method ``switch_profile``. The work is done there.
        self.profile_combobox.removeItem(i)

    def _next_triggered(self):
        log.debug('method next_profile called')
        i = self.profile_combobox.currentIndex() + 1
        size = self.profile_combobox.count()
        if i > size-1:
            i = 0
        # We just set a new index on the combobox, which causes a call
        # of method ``switch_profile``. The work is done there.
        self.profile_combobox.setCurrentIndex(i)

    def _previous_triggered(self):
        log.debug('method previous_profile called')
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
        self.switch_document()

    def _detect_surface_triggered(self):
        doc = self.current_document
        doc.profile.detect_surface()
        self.switch_document()

    def _showmap_triggered(self):
        self.map_window.set_documents(self.documents)
        self.map_window.show()
        self.map_window.activateWindow()
        self.map_window.raise_()

    def _showlog_triggered(self):
        self.log_window.show()
        self.log_window.activateWindow()
        self.log_window.raise_()

    @staticmethod
    def _about_triggered():
        # Read the content of the file about.html which must be located
        # in the same directory as this file, read its content and use
        # string.Template to replace some content
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

    def _kml_triggered(self):
        profile = self.current_document.profile
        f = join(dirname(profile.pnt_filename),'snowmicropyn_profiles.kml')
        snowmicropyn.examiner.kml.export2kml(f, self.documents)
        self.notify_dialog.notifyFilesWritten(f)

    def switch_document(self):
        doc = self.current_document

        at_least_one = len(self.documents) > 0
        multiple = len(self.documents) >= 2
        self.profile_combobox.setEnabled(at_least_one)
        self.previous_action.setEnabled(multiple)
        self.next_action.setEnabled(multiple)
        self.drop_action.setEnabled(at_least_one)
        self.save_action.setEnabled(at_least_one)
        self.saveall_action.setEnabled(at_least_one)
        self.export_action.setEnabled(at_least_one)
        self.detect_ground_action.setEnabled(at_least_one)

        self.stacked_widget.setCurrentIndex(1 if at_least_one else 0)

        self.sidebar.set_document(doc)
        self.plotcanvas.set_document(doc)
        self.plotcanvas.draw()

    # This method is called by PlotCanvas and Sidebar when a marker is set to
    # a new value. This method then causes the required update of visualization
    def set_marker(self, label, value):
        p = self.current_document.profile
        value = value
        if value is not None:
            value = float(value)
        log.info('Setting marker {} of profile {} to {}'.format(repr(label), p.name, value))
        p.set_marker(label, value)

        self.sidebar.set_marker(label, value)
        self.plotcanvas.set_document(self.current_document)
        self.plotcanvas.draw()

    def add_marker(self, default_value=0):
        name, value = self.marker_dialog.getMarker(default_value=default_value)
        if name and value:
            self.set_marker(name, value)


# The NoDocWidget is visible when no document is open. It's just a label
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

    def notifyFilesWritten(self, files):
        if isinstance(files, str):
            files = [files]
        multipe = len(files) > 1
        self.setWindowTitle('Notification')
        self.hint_label.setText('File{} written:'.format('s' if multipe else ''))
        self.content_textedit.setText('\n'.join(files))
        self.exec()


class MarkerDialog(QDialog):
    def __init__(self, parent, *args):
        super(MarkerDialog, self).__init__(parent, *args)
        self.mainwin = parent
        self.setWindowTitle('Add Marker')

        self.label_editline = QLineEdit()
        self.label_editline.setMinimumWidth(200)
        self.value_lineedit = QLineEdit()
        self.value_lineedit.setMinimumWidth(200)
        self.validator = QDoubleValidator()
        self.value_lineedit.setValidator(self.validator)
        ok_and_cancel = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(ok_and_cancel)

        def check():
            ok_button = self.button_box.button(QDialogButtonBox.Ok)
            name = self.label_editline.text()
            existing_markers = [k for k, v in self.mainwin.current_document.profile.markers]
            valid_name = bool(name) and (name not in existing_markers)
            valid_value = self.validator.validate(self.value_lineedit.text(), 0)[0] == QValidator.Acceptable
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
        self.label_editline.setText(default_label)
        self.label_editline.setFocus()
        self.label_editline.selectAll()
        result = self.exec()
        if result == QDialog.Accepted:
            name = self.label_editline.text()
            value = float(self.value_lineedit.text())
            return name, value
        return None, None

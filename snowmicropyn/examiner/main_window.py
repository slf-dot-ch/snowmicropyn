import logging
from html import escape
from os.path import expanduser, dirname, abspath, join
from string import Template

from PyQt5.QtCore import QRect, Qt, QSettings
from PyQt5.QtGui import QIcon, QCursor, QFont
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from snowmicropyn import Profile
from snowmicropyn.examiner.globals import APP_NAME, VERSION
from snowmicropyn.examiner.info_view import InfoView

# This import statement is important, no icons appear in case it's missing!
import snowmicropyn.examiner.icons

log = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    SETTING_LAST_DIRECTORY = 'MainFrame/last_directory'
    SETTING_GEOMETRY = 'MainFrame/geometry'
    SETTING_SHOW_SURFACE = 'MainFrame/show_surface'
    SETTING_SHOW_GROUND = 'MainFrame/show_ground'
    SETTING_SHOW_SSA = 'MainFrame/show_ssa'
    SETTING_SHOW_DENSITY = 'MainFrame/show_density'

    DEFAULT_GEOMETRY = QRect(200, 200, 800, 600)

    def __init__(self, log_window, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle(APP_NAME)

        self.profiles = []

        self._last_directory = QSettings().value('MainFrame/last_directory', defaultValue=expanduser('~'))

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.mpl_connect('button_press_event', self.mouse_button_pressed)

        self.profile_info = InfoView()

        splitter = QSplitter()
        splitter.addWidget(self.canvas)
        splitter.addWidget(self.profile_info)

        self.stacked_widget = QStackedWidget(self)
        self.stacked_widget.addWidget(NoProfileWidget())
        self.stacked_widget.addWidget(splitter)

        self.setCentralWidget(self.stacked_widget)

        self.navtoolbar = NavigationToolbar(self.canvas, self)
        self.canvas.toolbar = self.navtoolbar
        self.addToolBar(Qt.BottomToolBarArea, self.navtoolbar)

        set_surface_action = QAction('Set Surface', self)
        set_surface_action.triggered.connect(self.set_surface)
        set_ground_action = QAction('Set Ground', self)
        set_ground_action.triggered.connect(self.set_ground)

        self.context_menu = QMenu()
        self.context_menu.addAction(set_surface_action)
        self.context_menu.addAction(set_ground_action)
        self.clicked_distance = None

        self.about_action = QAction('About', self)
        self.quit_action = QAction('Quit', self)
        self.settings_action = QAction('Settings', self)
        self.open_action = QAction('&Open', self)
        self.save_action = QAction('&Save', self)
        self.saveall_action = QAction('Save &All', self)
        self.drop_action = QAction('Drop', self)
        self.export_action = QAction('Export', self)
        self.info_action = QAction('Info', self)
        self.next_action = QAction('Next Profile', self)
        self.previous_action = QAction('Previous Profile', self)
        self.surface_action = QAction('Show Surface', self)
        self.ground_action = QAction('Show Ground', self)
        self.ssa_action = QAction('Show SSA', self)
        self.density_action = QAction('Show Density', self)
        self.autodetect_action = QAction('Detect Surface + Ground', self)
        self.map_action = QAction('Show Map', self)
        self.show_log_action = QAction('Show Log', self)

        self.profile_combobox = QComboBox(self)

        self.log_window = log_window

        self.init_ui()
        self.update_ui()

    def closeEvent(self, event):
        log.info('Saving settings of MainWindow')
        QSettings().setValue(MainWindow.SETTING_GEOMETRY, self.geometry())
        QSettings().setValue(MainWindow.SETTING_LAST_DIRECTORY, self._last_directory)
        QSettings().setValue(MainWindow.SETTING_SHOW_SURFACE, self.surface_action.isChecked())
        QSettings().setValue(MainWindow.SETTING_SHOW_GROUND, self.ground_action.isChecked())
        QSettings().setValue(MainWindow.SETTING_SHOW_SSA, self.ssa_action.isChecked())
        QSettings().setValue(MainWindow.SETTING_SHOW_DENSITY, self.density_action.isChecked())

        # This is the main window. In case it's closed, we close all
        # other windows too which results in quitting the application

        # noinspection PyArgumentList
        QApplication.instance().closeAllWindows()

    def init_ui(self):
        geometry = QSettings().value('MainFrame/geometry', defaultValue=MainWindow.DEFAULT_GEOMETRY)
        self.setGeometry(geometry)

        self.profile_combobox.currentIndexChanged.connect(self.switch_profile)

        action = self.about_action
        action.setStatusTip('About ' + APP_NAME)
        action.triggered.connect(self.about)

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
        action.triggered.connect(self.open_profile)

        action = self.save_action
        action.setIcon(QIcon(':/icons/save.png'))
        action.setShortcut('Ctrl+S')
        action.setStatusTip('Save')
        action.triggered.connect(self.save_profile)

        action = self.saveall_action
        action.setIcon(QIcon(':/icons/saveall.png'))
        action.setShortcut('Ctrl+Alt+S')
        action.setStatusTip('Save All Profiles')
        action.triggered.connect(self.save_profiles)

        action = self.drop_action
        action.setIcon(QIcon(':/icons/drop.png'))
        action.setShortcut('Ctrl+X')
        action.setStatusTip('Drop Profile')
        action.triggered.connect(self.drop_profile)

        action = self.export_action
        action.setIcon(QIcon(':/icons/export.png'))
        action.setShortcut('Ctrl+E')
        action.setStatusTip('Export Profile to CSV')
        action.triggered.connect(self.export_profile)

        action = self.info_action
        action.setIcon(QIcon(':/icons/info.png'))
        action.setShortcut('Ctrl+I')
        action.setStatusTip('Info')

        action = self.next_action
        action.setIcon(QIcon(':/icons/next.png'))
        action.setShortcut('Ctrl+N')
        action.setStatusTip('Next Profile')
        action.triggered.connect(self.next_profile)

        action = self.previous_action
        action.setIcon(QIcon(':/icons/previous.png'))
        action.setShortcut('Ctrl+P')
        action.setStatusTip('Previous Profile')
        action.triggered.connect(self.previous_profile)

        action = self.autodetect_action
        action.setIcon(QIcon(':/icons/autodetect.png'))
        action.setShortcut('Ctrl+D')
        action.setStatusTip('Autodetect Surface and Ground')
        action.triggered.connect(self.autodetect)

        def force_plot():
            self.plot_profile(self.current_profile)

        action = self.surface_action
        action.setShortcut('Alt+S')
        action.setStatusTip('Show Surface')
        action.setCheckable(True)
        action.triggered.connect(force_plot)
        action.setChecked(QSettings().value(MainWindow.SETTING_SHOW_SURFACE, defaultValue=True))

        action = self.ground_action
        action.setShortcut('Alt+G')
        action.setStatusTip('Show Ground')
        action.setCheckable(True)
        action.triggered.connect(force_plot)
        action.setChecked(QSettings().value(MainWindow.SETTING_SHOW_GROUND, defaultValue=True))

        action = self.ssa_action
        action.setShortcut('Alt+A')
        action.setStatusTip('Show SSA')
        action.setCheckable(True)
        action.triggered.connect(force_plot)
        action.setChecked(QSettings().value(MainWindow.SETTING_SHOW_SSA, defaultValue=True))

        action = self.density_action
        action.setShortcut('Alt+D')
        action.setStatusTip('Show Density')
        action.setCheckable(True)
        action.triggered.connect(force_plot)
        action.setChecked(QSettings().value(MainWindow.SETTING_SHOW_DENSITY, defaultValue=True))

        action = self.map_action
        action.setIcon(QIcon(':/icons/map.png'))
        action.setShortcut('Ctrl+M')
        action.setStatusTip('Show Map')
        action.triggered.connect(self.show_map)

        action = self.show_log_action
        action.setIcon(QIcon(':/icons/logs.png'))
        action.setShortcut('Ctrl+L')
        action.setStatusTip('Show Log Window')
        action.triggered.connect(self.show_log)

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
        menu.addAction(self.surface_action)
        menu.addAction(self.ground_action)
        menu.addAction(self.ssa_action)
        menu.addAction(self.density_action)
        menu.addSeparator()
        menu.addAction(self.next_action)
        menu.addAction(self.previous_action)
        menu.addSeparator()
        menu.addAction(self.show_log_action)

        menu = menubar.addMenu('&Profile')
        menu.addAction(self.autodetect_action)

        toolbar = self.addToolBar('Exit')
        toolbar.addAction(self.quit_action)
        toolbar.addAction(self.settings_action)
        toolbar.addSeparator()
        toolbar.addAction(self.open_action)
        toolbar.addAction(self.save_action)
        toolbar.addAction(self.saveall_action)
        toolbar.addAction(self.drop_action)
        toolbar.addAction(self.export_action)
        toolbar.addSeparator()
        toolbar.addAction(self.info_action)
        toolbar.addAction(self.autodetect_action)
        toolbar.addAction(self.previous_action)
        toolbar.addWidget(self.profile_combobox)
        toolbar.addAction(self.next_action)
        toolbar.addSeparator()
        toolbar.addAction(self.map_action)

    @staticmethod
    def about():
        # Read the content of the file about.html which must be located
        # in the same directory as this file, read its content and use
        # string.Template to replace some content
        folder = dirname(abspath(__file__))
        with open(join(folder, 'about.html')) as f:
            content = f.read()
        content = Template(content).substitute(app_name=escape(APP_NAME), version=escape(VERSION))

        label = QLabel()
        label.setText(content)
        label.setOpenExternalLinks(True)

        layout = QVBoxLayout()
        layout.addWidget(label)

        # noinspection PyArgumentList
        dialog = QDialog()
        dialog.setWindowTitle('About')
        dialog.setLayout(layout)
        dialog.exec_()

    @property
    def current_profile(self):
        i = self.profile_combobox.currentIndex()
        if i == -1:
            return None
        return self.profiles[i]

    def open_profile(self):
        cap = "Open Profile(s)"
        filtr = "pnt Files (*.pnt)"
        opts = QFileDialog.ReadOnly
        startdir = self._last_directory
        # noinspection PyTypeChecker
        files, _ = QFileDialog.getOpenFileNames(self, cap, startdir, filtr, options=opts)
        if files:
            new_profiles = []
            for f in files:
                p = Profile.load(f)
                new_profiles.append(p)
            # Set active to first of newly loaded profiles
            self.profiles.extend(new_profiles)
            first_new_index = self.profile_combobox.count()
            self.profile_combobox.addItems([p.name for p in new_profiles])
            self.profile_combobox.setCurrentIndex(first_new_index)

        # Save directory where we were to open at same place next time
        # for user's convenience
        if self.current_profile:
            self._last_directory = dirname(self.current_profile.pnt_filename)

    def save_profile(self):
        self.current_profile.save()

    def save_profiles(self):
        for p in self.profiles:
            p.save()

    def export_profile(self):
        p = self.current_profile
        p.export_meta(full_pnt_header=True)
        p.export_samples()

    def drop_profile(self):
        log.debug('method drop_profile called')
        i = self.profile_combobox.currentIndex()
        del self.profiles[i]
        # We just remove the item from the combobox, which causes
        # a call of method ``switch_profile``. The work is done there.
        self.profile_combobox.removeItem(i)

    def next_profile(self):
        log.debug('method next_profile called')
        i = self.profile_combobox.currentIndex() + 1
        size = self.profile_combobox.count()
        if i > size-1:
            i = 0
        # We just set a new index on the combobox, which causes a call
        # of method ``switch_profile``. The work is done there.
        self.profile_combobox.setCurrentIndex(i)

    def previous_profile(self):
        log.debug('method previous_profile called')
        i = self.profile_combobox.currentIndex() - 1
        size = self.profile_combobox.count()
        if i < 0:
            i = size - 1
        # We just set a new index on the combobox, which causes a call
        # of method ``switch_profile`` The work is done there.
        self.profile_combobox.setCurrentIndex(i)

    def switch_profile(self):
        log.debug('method switch_profile called')
        self.update_ui()
        self.plot_profile(self.current_profile)

    def update_ui(self):
        at_least_one = len(self.profiles) > 0
        multiples = len(self.profiles) >= 2

        self.profile_combobox.setEnabled(at_least_one)

        self.previous_action.setEnabled(multiples)
        self.next_action.setEnabled(multiples)
        self.drop_action.setEnabled(at_least_one)

        self.save_action.setEnabled(at_least_one)
        self.saveall_action.setEnabled(at_least_one)
        self.export_action.setEnabled(at_least_one)

        self.autodetect_action.setEnabled(at_least_one)

        self.stacked_widget.setCurrentIndex(1 if at_least_one else 0)

    def autodetect(self):
        p = self.current_profile
        p.detect_ground()
        p.detect_surface()
        self.plot_profile(p)

    def plot_profile(self, p):
        if not p:
            self.figure.clf()
            self.canvas.draw()
            return

        self.profile_info.set_profile(p)

        FORCE_COLOR = 'C0'
        SSA_COLOR = 'C1'
        DENSITY_COLOR = 'C2'
        SURFACE_COLOR = 'C3'
        GROUND_COLOR = 'C4'

        self.figure.clf()
        host = self.figure.add_subplot(111)
        host.set_title(p.pnt_filename, y=1.04)

        if self.surface_action.isChecked() and p.surface:
            host.axvline(x=p.surface, color=SURFACE_COLOR)
            middle = p.max_force
            host.text(x=p.surface, y=middle, s='surface', rotation=90, verticalalignment='top', color=SURFACE_COLOR)

        if self.ground_action.isChecked() and p.ground:
            host.axvline(x=p.ground, color=GROUND_COLOR)
            middle = p.max_force
            host.text(x=p.ground, y=middle, s='ground', rotation=90, verticalalignment='top', color=GROUND_COLOR)

        host.xaxis.set_label_text('Distance [mm]')
        host.yaxis.set_label_text('Force [N]')
        host.plot(p.samples.distance, p.samples.force, FORCE_COLOR)
        host.yaxis.label.set_color(FORCE_COLOR)

        ssa_data = p.model_ssa()

        if self.ssa_action.isChecked():
            ssa = host.twinx()
            ssa.yaxis.label.set_text('SSA [$m^2/m^3$]')
            ssa.yaxis.label.set_color(SSA_COLOR)
            ssa.plot(ssa_data.distance, ssa_data.ssa, SSA_COLOR)

        if self.density_action.isChecked():
            density = host.twinx()
            density.yaxis.set_label_text('Density [$kg/m^3$]')
            density.yaxis.label.set_color(DENSITY_COLOR)
            density.plot(ssa_data.distance, ssa_data.rho, DENSITY_COLOR)
            # Place y-axis outside in case SSA axis is also present
            if self.ssa_action.isChecked():
                density.spines['right'].set_position(('outward', 60))

        self.figure.tight_layout(pad=3)
        self.canvas.draw()

    def mouse_button_pressed(self, event):
        log.debug('context click. x={}'.format(event))
        if event.button == 3:
            # Save distance value where the click was, we need it when
            # the uses selects an action on it like set_surface or
            # set_ground
            self.clicked_distance = event.xdata
            cursor = QCursor()
            self.context_menu.popup(cursor.pos())

    def set_surface(self):
        self.current_profile.set_marker('surface', self.clicked_distance)
        self.plot_profile(self.current_profile)

    def set_ground(self):
        self.current_profile.set_marker('ground', self.clicked_distance)
        self.plot_profile(self.current_profile)

    def show_map(self):
        pass

    def show_log(self):
        self.log_window.show()
        self.log_window.activateWindow()


class NoProfileWidget(QWidget):
    def __init__(self, parent=None):
        # noinspection PyArgumentList
        super(NoProfileWidget, self).__init__(parent)
        font = QFont()
        font.setPointSize(30)
        self.label = QLabel('No open pnt Files')
        self.label.setFont(font)
        self.setStyleSheet('color: lightgray')
        layout = QVBoxLayout()
        layout.addWidget(self.label, alignment=Qt.AlignHCenter)
        self.setLayout(layout)

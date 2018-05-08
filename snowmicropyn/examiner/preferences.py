import logging

import PyQt5.Qt as Qt

log = logging.getLogger(__name__)

_GAP = 20
_LINEEDIT_WIDTH = 50

PREFS_WINDOWSSIZE = 'Preferences/window_size'
PREFS_WINDOWSSIZE_DEFAULT = 2.5
PREFS_OVERLAP = 'Preferences/overlap'
PREFS_OVERLAP_DEFAULT = 50

PREFS_DISTANCE_AXIS_FIX = 'Preferences/distance_axis_fix'
PREFS_DISTANCE_AXIS_FIX_DEFAULT = False
PREFS_DISTANCE_AXIS_FROM = 'Preferences/distance_axis_from'
PREFS_DISTANCE_AXIS_FROM_DEFAULT = -50
PREFS_DISTANCE_AXIS_TO = 'Preferences/distance_axis_to'
PREFS_DISTANCE_AXIS_TO_DEFAULT = 1050

PREFS_FORCE_AXIS_FIX = 'Preferences/force_axis_fix'
PREFS_FORCE_AXIS_FIX_DEFAULT = False
PREFS_FORCE_AXIS_FROM = 'Preferences/force_axis_from'
PREFS_FORCE_AXIS_FROM_DEFAULT = -4
PREFS_FORCE_AXIS_TO = 'Preferences/force_axis_to'
PREFS_FORCE_AXIS_TO_DEFAULT = 84

PREFS_DENSITY_AXIS_FIX = 'Preferences/density_axis_fix'
PREFS_DENSITY_AXIS_FIX_DEFAULT = False
PREFS_DENSITY_AXIS_FROM = 'Preferences/density_axis_from'
PREFS_DENSITY_AXIS_FROM_DEFAULT = -30
PREFS_DENSITY_AXIS_TO = 'Preferences/density_axis_to'
PREFS_DENSITY_AXIS_TO_DEFAULT = 630

PREFS_SSA_AXIS_FIX = 'Preferences/ssa_axis_fix'
PREFS_SSA_AXIS_FIX_DEFAULT = False
PREFS_SSA_AXIS_FROM = 'Preferences/ssa_axis_from'
PREFS_SSA_AXIS_FROM_DEFAULT = -2
PREFS_SSA_AXIS_TO = 'Preferences/ssa_axis_to'
PREFS_SSA_AXIS_TO_DEFAULT = 42


class Preferences:

    def __init__(self):
        self.window_size = PREFS_WINDOWSSIZE_DEFAULT
        self.overlap = PREFS_OVERLAP_DEFAULT

        self.distance_axis_fix = PREFS_DISTANCE_AXIS_FIX_DEFAULT
        self.distance_axis_from = PREFS_DISTANCE_AXIS_FROM_DEFAULT
        self.distance_axis_to = PREFS_DISTANCE_AXIS_TO_DEFAULT

        self.force_axis_fix = PREFS_FORCE_AXIS_FIX_DEFAULT
        self.force_axis_from = PREFS_FORCE_AXIS_FROM_DEFAULT
        self.force_axis_to = PREFS_FORCE_AXIS_TO_DEFAULT

        self.density_axis_fix = PREFS_DENSITY_AXIS_FIX_DEFAULT
        self.density_axis_from = PREFS_DENSITY_AXIS_FROM_DEFAULT
        self.density_axis_to = PREFS_DENSITY_AXIS_TO_DEFAULT

        self.ssa_axis_fix = PREFS_SSA_AXIS_FIX_DEFAULT
        self.ssa_axis_from = PREFS_SSA_AXIS_FROM_DEFAULT
        self.ssa_axis_to = PREFS_SSA_AXIS_TO_DEFAULT

    @staticmethod
    def load():
        log.info('Loading Preferences')
        instance = Preferences()

        f = Qt.QSettings().value
        instance.window_size = f(PREFS_WINDOWSSIZE, PREFS_WINDOWSSIZE_DEFAULT, float)
        instance.overlap = f(PREFS_OVERLAP, PREFS_OVERLAP_DEFAULT, float)

        instance.distance_axis_fix = f(PREFS_DISTANCE_AXIS_FIX, PREFS_DISTANCE_AXIS_FIX_DEFAULT, bool)
        instance.distance_axis_from = f(PREFS_DISTANCE_AXIS_FROM, PREFS_DISTANCE_AXIS_FROM_DEFAULT, float)
        instance.distance_axis_to = f(PREFS_DISTANCE_AXIS_TO, PREFS_DISTANCE_AXIS_TO_DEFAULT, float)

        instance.force_axis_fix = f(PREFS_FORCE_AXIS_FIX, PREFS_FORCE_AXIS_FIX_DEFAULT, bool)
        instance.force_axis_from = f(PREFS_FORCE_AXIS_FROM, PREFS_FORCE_AXIS_FROM_DEFAULT, float)
        instance.force_axis_to = f(PREFS_FORCE_AXIS_TO, PREFS_FORCE_AXIS_TO_DEFAULT, float)

        instance.density_axis_fix = f(PREFS_DENSITY_AXIS_FIX, PREFS_DENSITY_AXIS_FIX_DEFAULT, bool)
        instance.density_axis_from = f(PREFS_DENSITY_AXIS_FROM, PREFS_DENSITY_AXIS_FROM_DEFAULT, float)
        instance.density_axis_to = f(PREFS_DENSITY_AXIS_TO, PREFS_DENSITY_AXIS_TO_DEFAULT, float)

        instance.ssa_axis_fix = f(PREFS_SSA_AXIS_FIX, PREFS_SSA_AXIS_FIX_DEFAULT, bool)
        instance.ssa_axis_from = f(PREFS_SSA_AXIS_FROM, PREFS_SSA_AXIS_FROM_DEFAULT, float)
        instance.ssa_axis_to = f(PREFS_SSA_AXIS_TO, PREFS_SSA_AXIS_TO_DEFAULT, float)
        return instance

    def save(self):
        log.info('Saving Preferences')
        Qt.QSettings().setValue(PREFS_WINDOWSSIZE, self.window_size)
        Qt.QSettings().setValue(PREFS_OVERLAP, self.overlap)

        Qt.QSettings().setValue(PREFS_DISTANCE_AXIS_FROM, self.distance_axis_from)
        Qt.QSettings().setValue(PREFS_DISTANCE_AXIS_TO, self.distance_axis_to)

        Qt.QSettings().setValue(PREFS_FORCE_AXIS_FROM, self.force_axis_from)
        Qt.QSettings().setValue(PREFS_FORCE_AXIS_TO, self.force_axis_to)

        Qt.QSettings().setValue(PREFS_DENSITY_AXIS_FROM, self.density_axis_from)
        Qt.QSettings().setValue(PREFS_DENSITY_AXIS_TO, self.density_axis_to)

        Qt.QSettings().setValue(PREFS_SSA_AXIS_FROM, self.ssa_axis_from)
        Qt.QSettings().setValue(PREFS_SSA_AXIS_TO, self.ssa_axis_to)

        Qt.QSettings().sync()


class AxisSettings(Qt.QWidget):
    def __init__(self, unit=None):
        super(AxisSettings, self).__init__()

        self._auto_radiobutton = Qt.QRadioButton('Automatic')
        self._fix_radiobutton = Qt.QRadioButton('Fixed')
        self._auto_radiobutton.clicked.connect(lambda checked: self._enable_fix(False))
        self._fix_radiobutton.clicked.connect(lambda checked: self._enable_fix(True))

        self.upper_layout = Qt.QHBoxLayout()
        self.upper_layout.addWidget(self._auto_radiobutton)

        self._from_lineedit = Qt.QLineEdit()
        self._from_lineedit.setFixedWidth(_LINEEDIT_WIDTH)
        self._from_lineedit.setValidator(Qt.QDoubleValidator())
        self._from_lineedit.setAlignment(Qt.Qt.AlignRight)

        self._to_label = Qt.QLabel('to')
        self._to_lineedit = Qt.QLineEdit()
        self._to_lineedit.setFixedWidth(_LINEEDIT_WIDTH)
        self._to_lineedit.setValidator(Qt.QDoubleValidator())
        self._to_lineedit.setAlignment(Qt.Qt.AlignRight)

        self._unit_label = Qt.QLabel(unit) if unit else None

        self.lower_layout = Qt.QHBoxLayout()
        self.lower_layout.addWidget(self._fix_radiobutton)
        self.lower_layout.addWidget(self._from_lineedit)
        self.lower_layout.addWidget(self._to_label)
        self.lower_layout.addWidget(self._to_lineedit)
        if self._unit_label:
            self.lower_layout.addWidget(self._unit_label)

        self._button_group = Qt.QButtonGroup()
        self._button_group.addButton(self._auto_radiobutton)
        self._button_group.addButton(self._fix_radiobutton)

    def set_values(self, fix, from_value, to_value):
        self._from_lineedit.setText(str(from_value))
        self._to_lineedit.setText(str(to_value))
        if fix:
            self._fix_radiobutton.click()
        else:
            self._auto_radiobutton.click()

    def _enable_fix(self, enable):
        self._from_lineedit.setEnabled(enable)
        self._to_label.setEnabled(enable)
        self._to_lineedit.setEnabled(enable)
        if self._unit_label:
            self._unit_label.setEnabled(enable)

    @property
    def fix_enabled(self):
        return self._fix_radiobutton.isChecked()

    @property
    def from_value(self):
        return float(self._from_lineedit.text())

    @property
    def to_value(self):
        return float(self._to_lineedit.text())


class PreferencesDialog(Qt.QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Preferences')

        self.windows_size_lineedit = Qt.QLineEdit()
        self.windows_size_lineedit.setFixedWidth(_LINEEDIT_WIDTH)
        self.windows_size_lineedit.setValidator(Qt.QDoubleValidator())
        self.windows_size_lineedit.setAlignment(Qt.Qt.AlignRight)

        self.overlap_factor_lineedit = Qt.QLineEdit()
        self.overlap_factor_lineedit.setFixedWidth(_LINEEDIT_WIDTH)
        self.overlap_factor_lineedit.setValidator(Qt.QDoubleValidator())
        self.overlap_factor_lineedit.setAlignment(Qt.Qt.AlignRight)

        self.apply_button = Qt.QPushButton('&Apply')
        self.apply_button = Qt.QPushButton('&Defaults')

        buttons = Qt.QDialogButtonBox.RestoreDefaults | Qt.QDialogButtonBox.Ok | Qt.QDialogButtonBox.Cancel
        self.button_box = Qt.QDialogButtonBox(buttons)

        self.button_box.rejected.connect(self.reject)
        self.button_box.accepted.connect(self.accept)
        self.button_box.button(Qt.QDialogButtonBox.RestoreDefaults).clicked.connect(self.restore_defaults)

        self.distance_setting = AxisSettings('mm')
        self.force_setting = AxisSettings('N')
        self.density_setting = AxisSettings('kg/m<sup>3</sup>')
        self.ssa_setting = AxisSettings('m<sup>2</sup>/m<sup>3</sup>')

        self.init_ui()
        self.setMinimumWidth(500)

    def init_ui(self):
        derivations_box = Qt.QGroupBox('Derivations')
        layout = Qt.QFormLayout()
        layout.setHorizontalSpacing(20)
        derivations_box.setLayout(layout)

        content_layout = Qt.QHBoxLayout()
        content_layout.addWidget(self.windows_size_lineedit)
        content_layout.addWidget(Qt.QLabel('mm'))
        layout.addRow('Window Size', content_layout)

        content_layout = Qt.QHBoxLayout()
        content_layout.addWidget(self.overlap_factor_lineedit)
        content_layout.addWidget(Qt.QLabel('%'))
        layout.addRow('Overlap Factor', content_layout)

        axes_box = Qt.QGroupBox('Plot Axes')
        layout = Qt.QFormLayout()
        layout.setVerticalSpacing(0)
        layout.setHorizontalSpacing(20)
        axes_box.setLayout(layout)

        setting = self.distance_setting
        layout.addRow('Distance Axis', setting.upper_layout)
        layout.addRow(None, setting.lower_layout)
        setting.lower_layout.setContentsMargins(0, 0, 0, _GAP)

        setting = self.force_setting
        layout.addRow('Force Axis', setting.upper_layout)
        layout.addRow(None, setting.lower_layout)
        setting.lower_layout.setContentsMargins(0, 0, 0, _GAP)

        setting = self.density_setting
        layout.addRow('Density Axis', setting.upper_layout)
        layout.addRow(None, setting.lower_layout)
        setting.lower_layout.setContentsMargins(0, 0, 0, _GAP)

        setting = self.ssa_setting
        layout.addRow('SSA Axis', setting.upper_layout)
        layout.addRow(None, setting.lower_layout)

        layout = Qt.QVBoxLayout()
        layout.addWidget(derivations_box)
        layout.addWidget(axes_box)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

    def modifyPreferences(self, preferences):
        self._set_values(preferences)
        result = self.exec()
        if result == Qt.QDialog.Accepted:
            preferences.window_size = float(self.windows_size_lineedit.text())
            preferences.overlap = float(self.overlap_factor_lineedit.text())

            preferences.distance_axis_fix = self.distance_setting.fix_enabled
            preferences.distance_axis_from = self.distance_setting.from_value
            preferences.distance_axis_to = self.distance_setting.to_value

            preferences.force_axis_fix = self.force_setting.fix_enabled
            preferences.force_axis_from = self.force_setting.from_value
            preferences.force_axis_to = self.force_setting.to_value

            preferences.density_axis_fix = self.density_setting.fix_enabled
            preferences.density_axis_from = self.density_setting.from_value
            preferences.density_axis_to = self.density_setting.to_value

            preferences.ssa_axis_fix = self.ssa_setting.fix_enabled
            preferences.ssa_axis_from = self.ssa_setting.from_value
            preferences.ssa_axis_to = self.ssa_setting.to_value
            return True
        return False

    def _set_values(self, prefs):
        self.windows_size_lineedit.setText(str(prefs.window_size))
        self.overlap_factor_lineedit.setText(str(prefs.overlap))
        self.distance_setting.set_values(prefs.distance_axis_fix,
                                         prefs.distance_axis_from,
                                         prefs.distance_axis_to)
        self.force_setting.set_values(prefs.force_axis_fix,
                                      prefs.force_axis_from,
                                      prefs.force_axis_to)
        self.density_setting.set_values(prefs.density_axis_fix,
                                        prefs.density_axis_from,
                                        prefs.density_axis_to)
        self.ssa_setting.set_values(prefs.ssa_axis_fix,
                                    prefs.ssa_axis_from,
                                    prefs.ssa_axis_to)

    def restore_defaults(self):
        defaults = Preferences()
        self._set_values(defaults)

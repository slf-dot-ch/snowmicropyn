import logging

from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QDoubleValidator, QIntValidator
from PyQt5.QtWidgets import QWidget, QLineEdit, QFormLayout, QHBoxLayout, QVBoxLayout, \
    QLabel, QDialogButtonBox, QDialog, QVBoxLayout

log = logging.getLogger(__name__)

_LINEEDIT_WIDTH = 50

EXPORT_SLOPE_ANGLE = 'Preferences/export_slope_angle'
EXPORT_SLOPE_ANGLE_DEFAULT = 0
EXPORT_DATA_THINNING = 'Preferences/export_data_thinning'
EXPORT_DATA_THINNING_DEFAULT = 150
EXPORT_STRETCH_FACTOR = 'Preferences/export_stretch_factor'
EXPORT_STRETCH_FACTOR_DEFAULT = 1

class ExportSettings:

    def __init__(self):
        self.export_slope_angle = EXPORT_SLOPE_ANGLE_DEFAULT
        self.export_data_thinning = EXPORT_DATA_THINNING_DEFAULT
        self.export_stretch_factor = EXPORT_STRETCH_FACTOR_DEFAULT

    @staticmethod
    def load():
        instance = ExportSettings()

        f = QSettings().value
        instance.export_slope_angle = f(EXPORT_SLOPE_ANGLE, EXPORT_SLOPE_ANGLE_DEFAULT, float)
        instance.export_data_thinning = f(EXPORT_DATA_THINNING, EXPORT_DATA_THINNING_DEFAULT, int)
        instance.export_stretch_factor = f(EXPORT_STRETCH_FACTOR, EXPORT_STRETCH_FACTOR_DEFAULT, float)
        return instance

    def write(self):
        QSettings().setValue(EXPORT_SLOPE_ANGLE, self.export_slope_angle)
        QSettings().setValue(EXPORT_DATA_THINNING, self.export_data_thinning)
        QSettings().setValue(EXPORT_STRETCH_FACTOR, self.export_stretch_factor)
        QSettings().sync()


class ExportDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Export for niViz')

        self.slope_angle_lineedit = QLineEdit()
        self.slope_angle_lineedit.setFixedWidth(_LINEEDIT_WIDTH)
        self.slope_angle_lineedit.setValidator(QDoubleValidator())
        self.slope_angle_lineedit.setAlignment(Qt.AlignRight)
        self.data_thinning_lineedit = QLineEdit()
        self.data_thinning_lineedit.setFixedWidth(_LINEEDIT_WIDTH)
        self.data_thinning_lineedit.setValidator(QIntValidator())
        self.data_thinning_lineedit.setAlignment(Qt.AlignRight)
        self.stretch_factor_lineedit = QLineEdit()
        self.stretch_factor_lineedit.setFixedWidth(_LINEEDIT_WIDTH)
        self.stretch_factor_lineedit.setValidator(QDoubleValidator())
        self.stretch_factor_lineedit.setAlignment(Qt.AlignRight)

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(buttons)

        self.button_box.rejected.connect(self.reject)
        self.button_box.accepted.connect(self.accept)

        self.setMinimumWidth(500)
        self.init_ui()

    def init_ui(self):

        main_layout = QVBoxLayout()

        layout = QFormLayout()
        layout.setHorizontalSpacing(20)

        content_layout = QHBoxLayout()
        content_layout.addWidget(self.slope_angle_lineedit)
        content_layout.addWidget(QLabel('°'))
        layout.addRow('Slope angle:', content_layout)

        content_layout = QHBoxLayout()
        content_layout.addWidget(self.data_thinning_lineedit)
        layout.addRow('Thinning:', content_layout)

        content_layout = QHBoxLayout()
        content_layout.addWidget(self.stretch_factor_lineedit)
        layout.addRow('Stretch factor:', content_layout)

        layout.addWidget(self.button_box)

        main_layout.addWidget(QLabel('Export profile as CSV directly readable by \
            <b><a href="https://run.niviz.org">niViz</a></b>:'))

        main_layout.addLayout(layout)
        self.setLayout(main_layout)

    def exportForNiviz(self, export_settings):
        self._set_values(export_settings)
        result = self.exec()
        if result == QDialog.Accepted:
            export_settings.export_slope_angle = 0 if not self.slope_angle_lineedit.text() \
                    else float(self.slope_angle_lineedit.text())
            export_settings.export_data_thinning = 1 if not self.data_thinning_lineedit.text() \
                    else int(self.data_thinning_lineedit.text())
            export_settings.export_stretch_factor = 1 if not self.stretch_factor_lineedit.text() \
                    else float(self.stretch_factor_lineedit.text())
            return True
        return False

    def _set_values(self, export_settings):
        self.slope_angle_lineedit.setText(str(export_settings.export_slope_angle))
        self.data_thinning_lineedit.setText(str(export_settings.export_data_thinning))
        self.stretch_factor_lineedit.setText(str(export_settings.export_stretch_factor))

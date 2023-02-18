"""CAAML export settings dialog.

"""

import logging

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDoubleValidator, QDesktopServices
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QGroupBox, QHBoxLayout, QLabel, QLineEdit, \
    QTabWidget, QVBoxLayout, QWidget

log = logging.getLogger('snowmicropyn')

_MIN_WIDTH = 600

class ExportDialog(QDialog):
    def __init__(self):
        super().__init__()
        self._init_widgets()
        self._init_ui()

    def _init_widgets(self):
        
        widget_width = lambda : int(_MIN_WIDTH / 5)

        self.station_name_lineedit = QLineEdit()
        self.station_name_lineedit.setFixedWidth(widget_width())
        self.station_name_lineedit.setAlignment(Qt.AlignRight)
        self.station_height_lineedit = QLineEdit()
        self.station_height_lineedit.setFixedWidth(widget_width())
        self.station_height_lineedit.setValidator(QDoubleValidator())
        self.station_height_lineedit.setAlignment(Qt.AlignRight)
        self.slope_angle_lineedit = QLineEdit()
        self.slope_angle_lineedit.setFixedWidth(widget_width())
        self.slope_angle_lineedit.setValidator(QDoubleValidator())
        self.slope_angle_lineedit.setAlignment(Qt.AlignRight)
        self.aggregation_lineedit = QLineEdit()
        self.aggregation_lineedit.setFixedWidth(widget_width())
        self.aggregation_lineedit.setValidator(QDoubleValidator())
        self.aggregation_lineedit.setAlignment(Qt.AlignRight)

        buttons = QDialogButtonBox.Help | QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(buttons)

        self.button_box.rejected.connect(self.reject)
        self.button_box.accepted.connect(self.accept)
        self.button_box.helpRequested.connect(lambda: QDesktopServices.openUrl(
            QUrl('https://snowmicropyn.readthedocs.io/en/latest/api_reference.html#snowmicropyn.Profile.export_samples_niviz')))


    def _init_ui(self):
        # Window settings
        self.setWindowTitle('CAAML export')
        self.setMinimumWidth(_MIN_WIDTH)
        caaml_layout = QVBoxLayout()

        # Metadata settings
        metadata_layout = QVBoxLayout()
        item_layout = QHBoxLayout()
        item_layout.addWidget(QLabel('Station name:'))
        item_layout.addWidget(self.station_name_lineedit)
        item_layout.addWidget(QLabel(''))
        metadata_layout.addLayout(item_layout)
        item_layout = QHBoxLayout()
        item_layout.addWidget(QLabel('Station height:'))
        item_layout.addWidget(self.station_height_lineedit)
        item_layout.addWidget(QLabel('m'))
        metadata_layout.addLayout(item_layout)
        item_layout = QHBoxLayout()
        item_layout.addWidget(QLabel('Slope angle:'))
        item_layout.addWidget(self.slope_angle_lineedit)
        item_layout.addWidget(QLabel('°'))
        metadata_layout.addLayout(item_layout)
        meta_frame = QGroupBox(self) 
        meta_frame.setTitle('Metadata')
        meta_frame.setLayout(metadata_layout)
        caaml_layout.addWidget(meta_frame)

        # Data aggregation
        aggregation_layout = QVBoxLayout()
        item_layout = QHBoxLayout()
        item_layout.addWidget(QLabel('Keep % of data (approx.):'))
        item_layout.addWidget(self.aggregation_lineedit)
        item_layout.addWidget(QLabel('%'))
        aggregation_layout.addLayout(item_layout)
        aggregation_frame = QGroupBox(self) 
        aggregation_frame.setTitle('Data aggregation')
        aggregation_frame.setLayout(aggregation_layout)
        caaml_layout.addWidget(aggregation_frame)

        # Tabs and main layout
        tabs = QTabWidget()
        tab_caaml = QWidget()
        tab_ai = QWidget()
        tab_caaml.setLayout(caaml_layout)
        tabs.addTab(tab_caaml, 'CAAML')
        tabs.addTab(tab_ai, 'Grain shape')

        main_layout = QVBoxLayout()
        main_layout.addWidget(tabs)
        main_layout.addWidget(self.button_box)
        self.setLayout(main_layout)

    def confirmExportCAAML(self):
        result = self.exec()
        return (result == QDialog.Accepted)

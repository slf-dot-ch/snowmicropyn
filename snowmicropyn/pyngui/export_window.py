"""CAAML export settings dialog.

"""

import logging

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDoubleValidator, QDesktopServices
from PyQt5.QtWidgets import QCheckBox, QComboBox, QDialog, QDialogButtonBox, QGroupBox, \
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QTabWidget, QVBoxLayout, QWidget

log = logging.getLogger('snowmicropyn')

_window_min_width = 600

class ExportDialog(QDialog):
    def __init__(self):
        super().__init__()
        self._inputs = {}
        self._init_widgets()
        self._init_ui()

    def _init_widgets(self):
        
        widget_width = lambda : int(_window_min_width / 5)

        # CAAML tab
        self._inputs['location_name'] = QLineEdit()
        self._inputs['location_name'].setFixedWidth(widget_width())
        self._inputs['location_name'].setAlignment(Qt.AlignRight)
        self._inputs['altitude'] = QLineEdit()
        self._inputs['altitude'].setFixedWidth(widget_width())
        self._inputs['altitude'].setValidator(QDoubleValidator())
        self._inputs['altitude'].setAlignment(Qt.AlignRight)
        self._inputs['slope_angle'] = QLineEdit()
        self._inputs['slope_angle'].setFixedWidth(widget_width())
        self._inputs['slope_angle'].setValidator(QDoubleValidator())
        self._inputs['slope_angle'].setAlignment(Qt.AlignRight)
        self._inputs['slope_exposition'] = QLineEdit()
        self._inputs['slope_exposition'].setFixedWidth(widget_width())
        self._inputs['slope_exposition'].setValidator(QDoubleValidator())
        self._inputs['slope_exposition'].setAlignment(Qt.AlignRight)
        self._inputs['aggregation'] = QLineEdit()
        self._inputs['aggregation'].setFixedWidth(widget_width())
        self._inputs['aggregation'].setValidator(QDoubleValidator())
        self._inputs['aggregation'].setAlignment(Qt.AlignRight)

        # Grain shape tab:
        self._inputs['export_grainshape'] = QCheckBox('Export grainshape estimation')
        self._inputs['use_pretrained_model'] = QCheckBox('Use pretrained model')
        self._inputs['model_input_path'] = QLineEdit()
        self._inputs['scaler'] = QComboBox()
        self._inputs['model'] = QComboBox()
        self._inputs['svc_gamma'] = QLineEdit()
        self._inputs['training_data_folder'] = QLineEdit()
        self._inputs['save_model'] = QCheckBox('Save trained model state')
        self._inputs['model_output_path'] = QLineEdit()

        # Buttons:
        buttons = QDialogButtonBox.Help | QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(buttons)

        self.button_box.rejected.connect(self.reject)
        self.button_box.accepted.connect(self.accept)
        self.button_box.helpRequested.connect(lambda: QDesktopServices.openUrl(
            QUrl('https://snowmicropyn.readthedocs.io/en/latest/api_reference.html#snowmicropyn.Profile.export_samples_niviz')))


    def _init_ui(self):
        # Window settings:
        self.setWindowTitle('CAAML export')
        self.setMinimumWidth(_window_min_width)
        caaml_layout = QVBoxLayout()
        grainshape_layout = QVBoxLayout()
        preprocessing_layout = QVBoxLayout()

        # Metadata settings:
        metadata_layout = QVBoxLayout()
        item_layout = QHBoxLayout()
        item_layout.addWidget(QLabel('Location name:'))
        item_layout.addWidget(self._inputs['location_name'])
        item_layout.addWidget(QLabel(''))
        metadata_layout.addLayout(item_layout)
        item_layout = QHBoxLayout()
        item_layout.addWidget(QLabel('Altitude:'))
        item_layout.addWidget(self._inputs['altitude'])
        item_layout.addWidget(QLabel('m'))
        metadata_layout.addLayout(item_layout)
        item_layout = QHBoxLayout()
        item_layout.addWidget(QLabel('Slope angle:'))
        item_layout.addWidget(self._inputs['slope_angle'])
        item_layout.addWidget(QLabel('°'))
        metadata_layout.addLayout(item_layout)
        item_layout = QHBoxLayout()
        item_layout.addWidget(QLabel('Exposition:'))
        item_layout.addWidget(self._inputs['slope_exposition'])
        item_layout.addWidget(QLabel('°'))
        metadata_layout.addLayout(item_layout)
        meta_frame = QGroupBox(self) 
        meta_frame.setTitle('Metadata')
        meta_frame.setLayout(metadata_layout)
        caaml_layout.addWidget(meta_frame)

        # Data aggregation:
        aggregation_layout = QVBoxLayout()
        item_layout = QHBoxLayout()
        item_layout.addWidget(QLabel('Keep % of data (approx.):'))
        item_layout.addWidget(self._inputs['aggregation'])
        item_layout.addWidget(QLabel('%'))
        aggregation_layout.addLayout(item_layout)
        aggregation_frame = QGroupBox(self) 
        aggregation_frame.setTitle('Data aggregation')
        aggregation_frame.setLayout(aggregation_layout)
        caaml_layout.addWidget(aggregation_frame)

        # Grain shape estimation:
        grainshape_layout.addWidget(self._inputs['export_grainshape'])
        grainshape_layout.addWidget(self._inputs['use_pretrained_model'])
        item_layout = QHBoxLayout()
        item_layout.addWidget(QLabel('Path:'))
        item_layout.addWidget(self._inputs['model_input_path'])
        item_layout.addWidget(QPushButton("..."))
        grainshape_layout.addLayout(item_layout)

        # Grain shape training:
        training_layout = QVBoxLayout()
        item_layout = QHBoxLayout()
        item_layout.addWidget(QLabel('Scaler:'))
        item_layout.addWidget(self._inputs['scaler'])
        training_layout.addLayout(item_layout)
        item_layout = QHBoxLayout()
        item_layout.addWidget(QLabel('Model:'))
        item_layout.addWidget(self._inputs['model'])
        training_layout.addLayout(item_layout)
        item_layout = QHBoxLayout()
        item_layout.addWidget(QLabel('Training data folder:'))
        item_layout.addWidget(self._inputs['training_data_folder'])
        training_layout.addLayout(item_layout)
        training_layout.addWidget(self._inputs['save_model'])
        item_layout = QHBoxLayout()
        item_layout.addWidget(QLabel('Path:'))
        item_layout.addWidget(self._inputs['model_output_path'])
        training_layout.addLayout(item_layout)
        training_frame = QGroupBox(self)
        training_frame.setTitle('Model training')
        training_frame.setLayout(training_layout)
        grainshape_layout.addWidget(training_frame)

        # Tabs:
        tabs = QTabWidget()
        tab_caaml = QWidget()
        tab_caaml.setLayout(caaml_layout)
        tabs.addTab(tab_caaml, 'CAAML')
        tab_grainshape = QWidget()
        tab_grainshape.setLayout(grainshape_layout)
        tabs.addTab(tab_grainshape, 'Grain shape')
        tab_preprocessing = QWidget()
        tab_preprocessing.setLayout(preprocessing_layout)
        tabs.addTab(tab_preprocessing, 'Preprocessing')

        # Main layout:
        main_layout = QVBoxLayout()
        main_layout.addWidget(tabs)
        main_layout.addWidget(self.button_box)
        self.setLayout(main_layout)

    def confirmExportCAAML(self):
        result = self.exec()
        return (result == QDialog.Accepted)

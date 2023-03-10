"""CAAML export settings dialog.

"""

import logging

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDoubleValidator, QDesktopServices
from PyQt5.QtWidgets import QCheckBox, QComboBox, QDialog, QDialogButtonBox, QGroupBox, \
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QTabWidget, QVBoxLayout, QWidget

log = logging.getLogger('snowmicropyn')

_window_min_width = 600
_widget_width = int(_window_min_width / 5)
_spacer_width = int(_window_min_width / 20)
_spacer_height = _spacer_width

class LabelText(QWidget):
    _lineedit = None
    def __init__(self, label, small=False, indent=False):
        super().__init__()
        self._init_ui(label, small, indent)

    def _init_ui(self, label, small, indent):
        self._lineedit = QLineEdit()
        main_layout = QHBoxLayout()
        if indent:
            main_layout.addSpacing(_spacer_width)
        main_layout.addWidget(QLabel(label))
        main_layout.addWidget(self._lineedit)
        self.setLayout(main_layout)
        if small:
            self._lineedit.setFixedWidth(_widget_width)
            self._lineedit.setAlignment(Qt.AlignRight)
        self.setContentsMargins(0, 0, 0, 0)
        main_layout.setContentsMargins(0,0,0,0)

    @property
    def text(self):
        return self._lineedit.text

class FilePicker(QWidget):
    _lineedit = None
    _button = None
    def __init__(self, label, indent=False):
        super().__init__()
        self._init_ui(label, indent)

    def _init_ui(self, label, indent):
        self._lineedit = QLineEdit()
        self._button = QPushButton('...')
        main_layout = QHBoxLayout()
        if indent:
            main_layout.addSpacing(_spacer_width)
        main_layout.addWidget(QLabel(label))
        main_layout.addWidget(self._lineedit)
        main_layout.addWidget(self._button)
        self.setLayout(main_layout)
        self.setContentsMargins(0, 0, 0, 0)
        main_layout.setContentsMargins(0,0,0,0)

    @property
    def text(self):
        return self._lineedit.text

class ExportDialog(QDialog):
    def __init__(self):
        super().__init__()
        self._inputs = {}
        self._init_widgets()
        self._init_ui()

    def _init_widgets(self):

        # CAAML tab
        self._inputs['location_name'] = QLineEdit()
        self._inputs['location_name'].setFixedWidth(_widget_width)
        self._inputs['location_name'].setAlignment(Qt.AlignRight)
        self._inputs['altitude'] = QLineEdit()
        self._inputs['altitude'].setFixedWidth(_widget_width)
        self._inputs['altitude'].setValidator(QDoubleValidator())
        self._inputs['altitude'].setAlignment(Qt.AlignRight)
        self._inputs['slope_angle'] = QLineEdit()
        self._inputs['slope_angle'].setFixedWidth(_widget_width)
        self._inputs['slope_angle'].setValidator(QDoubleValidator())
        self._inputs['slope_angle'].setAlignment(Qt.AlignRight)
        self._inputs['slope_exposition'] = QLineEdit()
        self._inputs['slope_exposition'].setFixedWidth(_widget_width)
        self._inputs['slope_exposition'].setValidator(QDoubleValidator())
        self._inputs['slope_exposition'].setAlignment(Qt.AlignRight)
        self._inputs['aggregation'] = QLineEdit()
        self._inputs['aggregation'].setFixedWidth(_widget_width)
        self._inputs['aggregation'].setValidator(QDoubleValidator())
        self._inputs['aggregation'].setAlignment(Qt.AlignRight)

        # Grain shape tab:
        self._inputs['export_grainshape'] = QCheckBox('Export grainshape estimation')
        self._inputs['use_pretrained_model'] = QCheckBox('Use pretrained model')
        self._inputs['model_input_path'] = FilePicker('Path:', indent=True)
        self._inputs['scaler'] = QComboBox()
        self._inputs['model'] = QComboBox()
        self._inputs['training_data_folder'] = FilePicker('Training data folder:')
        self._inputs['save_model'] = QCheckBox('Save trained model state')
        self._inputs['model_output_path'] = FilePicker('Path:', indent=True)

        # Preprocessing tab:
        self._inputs['remove_negative_forces'] = QCheckBox('Remove negative forces')
        self._inputs['remove_noise'] = QCheckBox('Noise threshold:')
        self._inputs['noise_threshold'] = QLineEdit()
        self._inputs['noise_threshold'].setFixedWidth(_widget_width)
        self._inputs['discard_thin_layers'] = QCheckBox('Discard layers thinner than:')
        self._inputs['discard_layer_thickness'] = QLineEdit()
        self._inputs['discard_layer_thickness'].setFixedWidth(_widget_width)
        self._inputs['exclude_samples_boundaries'] = QCheckBox('Exclude samples at layer boundaries')

        # Model specific inputs:
        self._inputs['svc_gamma'] = LabelText('Gamma:', small=True, indent=True)
        self._inputs['multinomialnb_alpha'] = LabelText('Alpha:', small=True, indent=True)

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
        grainshape_layout.addWidget(self._inputs['model_input_path'])

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
        training_layout.addWidget(self._inputs['svc_gamma'])
        training_layout.addWidget(self._inputs['multinomialnb_alpha'])
        training_layout.addWidget(self._inputs['training_data_folder'])
        training_layout.addWidget(self._inputs['save_model'])
        training_layout.addWidget(self._inputs['model_output_path'])
        training_frame = QGroupBox(self)
        training_frame.setTitle('Model training')
        training_frame.setLayout(training_layout)
        grainshape_layout.addWidget(training_frame)

        # Preprocessing:
        preprocessing_layout = QVBoxLayout()
        preprocessing_layout.addWidget(self._inputs['remove_negative_forces'])
        item_layout = QHBoxLayout()
        item_layout.addWidget(self._inputs['remove_noise'])
        item_layout.addWidget(self._inputs['noise_threshold'])
        item_layout.addWidget(QLabel('N'))
        preprocessing_layout.addLayout(item_layout)
        item_layout = QHBoxLayout()
        item_layout.addWidget(self._inputs['discard_thin_layers'])
        item_layout.addWidget(self._inputs['discard_layer_thickness'])
        item_layout.addWidget(QLabel('mm'))
        preprocessing_layout.addLayout(item_layout)

        # Preprocessing specific to training data:
        pre_training_layout = QVBoxLayout()
        pre_training_layout.addWidget(self._inputs['exclude_samples_boundaries'])
        pre_training_frame = QGroupBox(self)
        pre_training_frame.setTitle('Preprocessing of training data')
        pre_training_frame.setLayout(pre_training_layout)
        preprocessing_layout.addSpacing(_spacer_height)
        preprocessing_layout.addWidget(pre_training_frame)

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
        caaml_layout.addStretch() # align all widgets to top
        grainshape_layout.addStretch()
        preprocessing_layout.addStretch()
        main_layout = QVBoxLayout()
        main_layout.addWidget(tabs)
        main_layout.addWidget(self.button_box)
        self.setLayout(main_layout)

    def confirmExportCAAML(self):
        result = self.exec()
        return (result == QDialog.Accepted)

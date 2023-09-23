"""CAAML export settings dialog.

"""

from awio import get_scriptpath
from collections import defaultdict
import logging
from PyQt5.QtCore import QSettings, Qt, QUrl
from PyQt5.QtGui import QDoubleValidator, QDesktopServices
from PyQt5.QtWidgets import QCheckBox, QComboBox, QDialog, QDialogButtonBox, QDoubleSpinBox, QFileDialog, QGroupBox, \
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QTabWidget, QVBoxLayout, QWidget
import sys

log = logging.getLogger('snowmicropyn')

_window_min_width = 600
_widget_width = int(_window_min_width / 5)
_spacer_width = int(_window_min_width / 20)
_spacer_height = _spacer_width

class LabelNumber(QWidget):
    _spinbox = None

    def __init__(self, label, small=False, indent=False):
        super().__init__()
        self._init_ui(label, small, indent)

    def _init_ui(self, label, small, indent):
        self._spinbox = QDoubleSpinBox()
        self._spinbox.setMinimum(sys.float_info.min)
        self._spinbox.setMaximum(sys.float_info.max)
        main_layout = QHBoxLayout()
        if indent:
            main_layout.addSpacing(_spacer_width)
        main_layout.addWidget(QLabel(label))
        main_layout.addWidget(self._spinbox)
        self.setLayout(main_layout)
        self.setContentsMargins(0, 0, 0, 0)
        main_layout.setContentsMargins(0,0,0,0)

    def setValue(self, value):
        self._spinbox.setValue(value)

    def value(self):
        return self._spinbox.value()

class FilePicker(QWidget):
    _lineedit = None
    _button = None
    _directory = False
    _save_mode = False

    def __init__(self, label, directory=False, save_mode=False, indent=False):
        super().__init__()
        self._directory = directory
        self._save_mode = save_mode
        self._init_ui(label, indent)

    def _init_ui(self, label, indent):
        self._lineedit = QLineEdit()
        self._button = QPushButton('...')
        self._button.clicked.connect(self.on_button_click)
        main_layout = QHBoxLayout()
        if indent:
            main_layout.addSpacing(_spacer_width)
        main_layout.addWidget(QLabel(label))
        main_layout.addWidget(self._lineedit)
        main_layout.addWidget(self._button)
        self.setLayout(main_layout)
        self.setContentsMargins(0, 0, 0, 0)
        main_layout.setContentsMargins(0,0,0,0)

    def on_button_click(self):
        if self._directory:
            fname = QFileDialog.getExistingDirectory(self, 'Open folder', '.')
        else:
            if self._save_mode:
                fname, _ = QFileDialog.getSaveFileName(self, 'Save file', '.')
            else:
                fname, _ = QFileDialog.getOpenFileName(self, 'Open file', '.')
        if fname:
            self._lineedit.setText(fname)

    def setText(self, text):
        self._lineedit.setText(text)

    def text(self):
        return self._lineedit.text()

class ExportDialog(QDialog):

    _settings_root = 'export/caaml'

    def __init__(self):
        super().__init__()
        self._inputs = {}
        self._init_widgets()
        self._init_ui()
        self._fill_from_settings()

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

        # Grain shape tab:
        # (For now we offer only the most important defaults for a one-click-solution
        # which are overwritten by user settings)
        self._inputs['export_grainshape'] = QCheckBox('Export grain shape estimation')
        self._inputs['use_pretrained_model'] = QCheckBox('Use pre-trained model')
        self._inputs['use_pretrained_model'].setChecked(True)
        self._inputs['trained_input_path'] = FilePicker('Path:', indent=True)
        default_trained_path = get_scriptpath(__file__) + '../ai/trained_model_rhossa.dat'
        self._inputs['trained_input_path'].setText(default_trained_path)
        self._inputs['scaler'] = QComboBox()
        self._inputs['scaler'].addItem('Standard Scaler', 'standard')
        self._inputs['scaler'].addItem('Min/Max Scaler', 'minmax')
        self._inputs['model'] = QComboBox()
        self._inputs['model'].addItem('Support Vector Machine', 'svc')
        self._inputs['model'].addItem('Linear Regression', 'lr')
        self._inputs['model'].addItem('Gaussian Naive Bayes', 'gaussiannb')
        self._inputs['model'].addItem('Multinomial Naive Bayes', 'multinomialnb')
        self._inputs['model'].currentIndexChanged.connect(self._on_model_changed)
        self._inputs['training_data_folder'] = FilePicker('Training data folder:', directory=True)
        self._inputs['training_data_method'] = QComboBox()
        self._inputs['training_data_method'].addItem('exact', 'exact')
        self._inputs['training_data_method'].addItem('markers', 'markers')
        self._inputs['training_data_method'].setToolTip('Method of parsing for training dataset')
        self._inputs['save_model'] = QCheckBox('Save trained model state')
        self._inputs['trained_output_path'] = FilePicker('Path:', save_mode=True, indent=True)

        # Preprocessing tab:
        self._inputs['remove_negative_data'] = QCheckBox('Remove negative forces and derivatives')
        self._inputs['remove_noise'] = QCheckBox('Noise threshold:')
        self._inputs['noise_threshold'] = QLineEdit()
        self._inputs['noise_threshold'].setFixedWidth(_widget_width)
        self._inputs['smoothing'] = QCheckBox('Apply smoothing')
        self._inputs['merge_layers'] = QCheckBox('Merge layers with all microparameters within')
        self._inputs['similarity_percent'] = QLineEdit()
        self._inputs['similarity_percent'].setFixedWidth(_widget_width)
        self._inputs['similarity_percent'].setValidator(QDoubleValidator())
        self._inputs['discard_thin_layers'] = QCheckBox('Discard layers thinner than:')
        self._inputs['discard_layer_thickness'] = QLineEdit()
        self._inputs['discard_layer_thickness'].setFixedWidth(_widget_width)
        self._inputs['exclude_samples_boundaries'] = QCheckBox('Exclude samples at layer boundaries')

        # Model specific inputs:
        self._inputs['model_svc_gamma'] = LabelNumber('Gamma:', small=True, indent=True)
        self._inputs['model_multinomialnb_alpha'] = LabelNumber('Alpha:', small=True, indent=True)
        self._on_model_changed(0) # show/hide appropriate widgets

        # Buttons:
        buttons = QDialogButtonBox.Help | QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(buttons)

        self.button_box.rejected.connect(self.reject)
        self.button_box.accepted.connect(self.accept)
        self.button_box.helpRequested.connect(lambda: QDesktopServices.openUrl(
            QUrl('https://snowmicropyn.readthedocs.io/en/latest/snowpit.html')))


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
        item_layout.addWidget(QLabel('Altitude:')) # Since this is for all open profiles, we do not try to parse...
        item_layout.addWidget(self._inputs['altitude']) # ... from a .pnt file (which may or may not have it).
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

        # Grain shape export:
        grain_export_layout = QVBoxLayout()
        grain_export_layout.addWidget(self._inputs['export_grainshape'])
        grain_export_frame = QGroupBox(self)
        grain_export_frame.setTitle('Grain shape')
        grain_export_frame.setLayout(grain_export_layout)
        caaml_layout.addWidget(grain_export_frame)

        # Pre-trained model file:
        pretrained_layout = QVBoxLayout()
        pretrained_layout.addWidget(self._inputs['use_pretrained_model'])
        pretrained_layout.addWidget(self._inputs['trained_input_path'])
        pretrained_frame = QGroupBox(self)
        pretrained_frame.setTitle('Pre-trained data')
        pretrained_frame.setLayout(pretrained_layout)
        grainshape_layout.addWidget(pretrained_frame)

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
        training_layout.addWidget(self._inputs['model_svc_gamma'])
        training_layout.addWidget(self._inputs['model_multinomialnb_alpha'])
        item_layout = QHBoxLayout()
        item_layout.addWidget(self._inputs['training_data_folder'])
        item_layout.addWidget(self._inputs['training_data_method'])
        training_layout.addLayout(item_layout)
        training_layout.addWidget(self._inputs['save_model'])
        training_layout.addWidget(self._inputs['trained_output_path'])
        training_frame = QGroupBox(self)
        training_frame.setTitle('Model training')
        training_frame.setLayout(training_layout)
        grainshape_layout.addWidget(training_frame)

        # Preprocessing:
        preprocessing_layout = QVBoxLayout()
        pre_smp_layout = QVBoxLayout()
        pre_smp_layout.addWidget(self._inputs['remove_negative_data'])
        item_layout = QHBoxLayout()
        item_layout.addWidget(self._inputs['remove_noise'])
        item_layout.addWidget(self._inputs['noise_threshold'])
        item_layout.addWidget(QLabel('N'))
        pre_smp_layout.addLayout(item_layout)
        pre_smp_layout.addWidget(self._inputs['smoothing'])
        item_layout = QHBoxLayout()
        item_layout.addWidget(self._inputs['merge_layers'])
        item_layout.addWidget(self._inputs['similarity_percent'])
        item_layout.addWidget(QLabel('%'))
        pre_smp_layout.addLayout(item_layout)
        item_layout = QHBoxLayout()
        item_layout.addWidget(self._inputs['discard_thin_layers'])
        item_layout.addWidget(self._inputs['discard_layer_thickness'])
        item_layout.addWidget(QLabel('mm'))
        pre_smp_layout.addLayout(item_layout)
        pre_smp_frame = QGroupBox(self)
        pre_smp_frame.setTitle('Preprocessing of SMP data')
        pre_smp_frame.setLayout(pre_smp_layout)
        preprocessing_layout.addWidget(pre_smp_frame)

        # Preprocessing specific to training data:
        #pre_training_layout = QVBoxLayout()
        #pre_training_layout.addWidget(self._inputs['exclude_samples_boundaries'])
        #pre_training_frame = QGroupBox(self)
        #pre_training_frame.setTitle('Preprocessing of training data')
        #pre_training_frame.setLayout(pre_training_layout)
        #preprocessing_layout.addWidget(pre_training_frame)

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

    def _on_model_changed(self, value):
        model_str = self._inputs['model'].itemData(value)
        for key, wid in self._inputs.items():
            if not key.startswith('model_'):
                continue
            wid.setVisible(key.startswith(f'model_{model_str}'))

    def _collect_settings(self):
        settings = defaultdict(lambda: None) # easier working with missing keys
        for key, panel in self._inputs.items():
            if isinstance(panel, QCheckBox):
                settings[key] = panel.isChecked()
            elif isinstance(panel, QComboBox):
                settings[key] = panel.itemData(panel.currentIndex())
            elif isinstance(panel, LabelNumber):
                settings[key] = panel.value()
            else: # line edit, FilePicker
                if not panel.text() == '':
                    settings[key] = panel.text()
        return settings

    def _fill_from_settings(self):
        for key, panel in self._inputs.items():
            value = QSettings().value(f'{self._settings_root}/{key}')
            if not value:
                continue
            if isinstance(panel, QCheckBox):
                panel.setChecked(value == 'true')
            elif isinstance(panel, QComboBox):
                for idx in range(panel.count()):
                    if panel.itemData(idx) == value:
                        panel.setCurrentIndex(idx)
                        break
            elif isinstance(panel, LabelNumber):
                panel.setValue(float(value))
            else: # line edit, FilePicker
                panel.setText(str(value))

    def _save_export_settings(self):
        settings = self._collect_settings()
        for key, value in settings.items():
            QSettings().setValue(f'{self._settings_root}/{key}', value)
        QSettings().sync()

    def confirmExportCAAML(self):
        result = self.exec()
        if result != QDialog.Accepted:
            return False
        self._save_export_settings()
        return self._collect_settings()

from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon, QDoubleValidator
from PyQt5.QtWidgets import *
import logging

import snowmicropyn.examiner.icons

log = logging.getLogger(__name__)


class ButtonThing(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        layout = QHBoxLayout()

        self.value_textedit = QLineEdit()
        self.value_textedit.setValidator(QDoubleValidator())

        self.setAutoFillBackground(True)

        self.detect_button = QPushButton()
        self.detect_button.setIcon(QIcon(':/icons/autodetect.png'))
        self.detect_button.setToolTip('Detect automatically')

        def detect():
            log.info('The toolbutton was clicked!')

        self.detect_button.clicked.connect(detect)

        layout.addWidget(self.value_textedit)
        layout.addWidget(self.detect_button)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


class Sidebar(QTreeView):

    def __init__(self, main_win, *args, **kwargs):
        self.main_window = main_win
        super().__init__(*args, **kwargs)

        self.doc = None

        self.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.setModel(QStandardItemModel(0, 2, self))

        # Get rid of the ugly focus rectangle and border
        self.setAttribute(Qt.WA_MacShowFocusRect, False)
        self.setStyleSheet('outline: 0; border: 0;')

        # Hide header of tree view
        self.header().hide()

        self.section_recording = QStandardItem('Recording')
        self.name = QStandardItem()
        self.name.setEditable(False)
        self.pnt_filename = QStandardItem()
        self.pnt_filename.setEditable(False)
        self.timestamp = QStandardItem()
        self.timestamp.setEditable(False)
        self.location = QStandardItem()
        self.location.setEditable(False)
        self.samples_count = QStandardItem()
        self.samples_count.setEditable(False)
        self.spatial_res = QStandardItem()
        self.spatial_res.setEditable(False)
        self.overload = QStandardItem()
        self.overload.setEditable(False)
        self.speed = QStandardItem()
        self.speed.setEditable(False)

        self.section_smp = QStandardItem('SnowMicroPen')
        self.smp_serial = QStandardItem()
        self.smp_serial.setEditable(False)
        self.smp_firmware = QStandardItem()
        self.smp_firmware.setEditable(False)
        self.smp_length = QStandardItem()
        self.smp_length.setEditable(False)
        self.smp_tipdiameter = QStandardItem()
        self.smp_tipdiameter.setEditable(False)
        self.smp_amp = QStandardItem()
        self.smp_amp.setEditable(False)

        self.section_markers = QStandardItem('Markers')

        self.section_noise = QStandardItem('Noise, Drift, Offset')
        self.offset = QStandardItem()
        self.offset.setEditable(False)
        self.drift = QStandardItem()
        self.drift.setEditable(False)
        self.noise = QStandardItem()
        self.noise.setEditable(False)

        self.init_ui()
        self.expandAll()
        self.resizeColumnToContents(0)

    def init_ui(self):
        model = self.model()

        section = self.section_recording
        section.setEnabled(False)
        model.appendRow(section)

        label = QStandardItem('Name')
        label.setEnabled(False)
        section.appendRow((label, self.name))

        label = QStandardItem('Filename')
        label.setEnabled(False)
        section.appendRow((label, self.pnt_filename))

        label = QStandardItem('Timestamp')
        label.setEnabled(False)
        section.appendRow((label, self.timestamp))

        label = QStandardItem('Location')
        label.setEnabled(False)
        section.appendRow((label, self.location))

        label = QStandardItem('Samples')
        label.setEnabled(False)
        section.appendRow((label, self.samples_count))

        label = QStandardItem('Spatial Resolution')
        label.setEnabled(False)
        section.appendRow((label, self.spatial_res))

        label = QStandardItem('Overload')
        label.setEnabled(False)
        section.appendRow((label, self.overload))

        label = QStandardItem('Speed')
        label.setEnabled(False)
        section.appendRow((label, self.speed))

        section = self.section_smp
        section.setEnabled(False)
        model.appendRow(section)

        label = QStandardItem('Serial Number')
        label.setEnabled(False)
        section.appendRow((label, self.smp_serial))

        label = QStandardItem('Firmware Version')
        label.setEnabled(False)
        section.appendRow((label, self.smp_firmware))

        label = QStandardItem('Length')
        label.setEnabled(False)
        section.appendRow((label, self.smp_length))

        label = QStandardItem('Tip Diameter')
        label.setEnabled(False)
        section.appendRow((label, self.smp_tipdiameter))

        label = QStandardItem('Amplifier Serial')
        label.setEnabled(False)
        section.appendRow((label, self.smp_amp))

        section = self.section_markers
        section.setEnabled(False)
        model.appendRow(section)

        section = self.section_noise
        section.setEnabled(False)
        model.appendRow(section)

        label = QStandardItem('Offset')
        label.setEnabled(False)
        section.appendRow((label, self.offset))

        label = QStandardItem('Drift')
        label.setEnabled(False)
        section.appendRow((label, self.drift))

        label = QStandardItem('Noise')
        label.setEnabled(False)
        section.appendRow((label, self.noise))

    def set_document(self, doc):
        if doc is None:
            return

        self.doc = doc

        profile = doc.profile
        self.name.setText(profile.name)
        self.pnt_filename.setText(profile.pnt_filename)
        self.timestamp.setText(str(profile.timestamp))
        loc = 'None'
        if profile.coordinates:
            loc = '{:.5f}, {:.5f}'.format(*profile.coordinates)
        self.location.setText(loc)
        self.samples_count.setText(str(profile.samples.shape[0]))
        self.spatial_res.setText('{:.1f} µm'.format(profile.spatial_resolution*1000))
        self.overload.setText('{:.1f} N'.format(profile.overload))
        self.speed.setText('{:.1f} mm/s'.format(profile.speed))

        self.smp_serial.setText(str(profile.smp_serial))
        self.smp_firmware.setText(str(profile.smp_firmware))
        self.smp_length.setText('{} mm'.format(profile.smp_length))
        self.smp_tipdiameter.setText('{:.1f} mm'.format(profile.smp_tipdiameter/1000))
        self.smp_amp.setText(str(profile.amplifier_serial))

        self.init_markers(profile)

    def init_markers(self, profile):
        # Remove all existing children from marker section
        self.section_markers.removeRows(0, self.section_markers.rowCount())

        for label, value in profile.markers:
            label_item = QStandardItem(label)
            label_item.setEditable(False)
            placeholder = QStandardItem('')

            self.section_markers.appendRow((label_item, placeholder))

            lineedit_with_button = ButtonThing()
            lineedit_with_button.value_textedit.setText('{:.3f}'.format(value))

            value_func = lineedit_with_button.value_textedit.text
            slot = partial(self.main_window.set_marker, label, value_func)
            lineedit_with_button.value_textedit.editingFinished.connect(slot)

            self.setIndexWidget(placeholder.index(), lineedit_with_button)

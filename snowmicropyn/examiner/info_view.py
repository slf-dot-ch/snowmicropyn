from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QAbstractItemView, QTreeView


class InfoView(QTreeView):
    def __init__(self):
        super().__init__()
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

        model = QStandardItemModel(0, 2, self)

        # Get rid of the ugly focus rectangle and border
        self.setAttribute(Qt.WA_MacShowFocusRect, False)
        self.setStyleSheet('outline: 0; border: 0;')

        # Hide header of tree view
        self.header().hide()

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

        self.setModel(model)
        self.init_ui()
        self.expandAll()
        self.resizeColumnToContents(0)

    def init_ui(self):
        model = self.model()

        section = QStandardItem('Recording')
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

        section = QStandardItem('SnowMicroPen')
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

        section = QStandardItem('Markers')
        section.setEnabled(False)
        model.appendRow(section)

        section = QStandardItem('Noise, Drift, Offset')
        section.setEnabled(False)
        model.appendRow(section)

    def set_profile(self, profile):
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


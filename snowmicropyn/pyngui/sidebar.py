import logging

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QDoubleValidator
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QLineEdit, QPushButton, QLabel

log = logging.getLogger(__name__)


class SidebarWidget(QTreeWidget):
    TEXT_COLUMN = 4

    def __init__(self, main_win, *args, **kwargs):
        self.main_window = main_win
        super().__init__(*args, **kwargs)

        # Get rid of the ugly focus rectangle and border
        self.setAttribute(Qt.WA_MacShowFocusRect, False)
        self.setStyleSheet('outline: 0; border: 0;')

        self.doc = None
        self.marker_items = {}

        self.setColumnCount(5)
        self.setHeaderHidden(True)

        # top level items

        self.recording_item = QTreeWidgetItem(('Recording',), QTreeWidgetItem.Type)
        self.smp_item = QTreeWidgetItem(('SnowMicroPen',), QTreeWidgetItem.Type)
        self.markers_item = QTreeWidgetItem(('Markers',), QTreeWidgetItem.Type)
        self.drift_item = QTreeWidgetItem(('Drift, Offset, Noise',), QTreeWidgetItem.Type)

        self.addTopLevelItem(self.recording_item)
        self.addTopLevelItem(self.smp_item)
        self.addTopLevelItem(self.markers_item)
        self.addTopLevelItem(self.drift_item)

        self.setFirstItemColumnSpanned(self.recording_item, True)
        self.setFirstItemColumnSpanned(self.smp_item, True)
        self.setFirstItemColumnSpanned(self.markers_item, True)
        self.setFirstItemColumnSpanned(self.drift_item, True)

        # recording items

        self.name_item = QTreeWidgetItem((None, None, 'Name', None, ''))
        self.timestamp_item = QTreeWidgetItem((None, None, 'Timestamp', None, ''))
        self.rec_length_item = QTreeWidgetItem((None, None, 'Length', None, ''))
        self.pnt_filename_item = QTreeWidgetItem((None, None, 'Pnt File', None, ''))
        self.coordinates_item = QTreeWidgetItem((None, None, 'Coordinates', None, ''))
        self.spatial_res_item = QTreeWidgetItem((None, None, 'Spatial Resolution', None, ''))
        self.overload_item = QTreeWidgetItem((None, None, 'Overload Force', None, ''))
        self.speed_item = QTreeWidgetItem((None, None, 'Speed', None, ''))

        self.recording_item.addChild(self.name_item)
        self.recording_item.addChild(self.pnt_filename_item)
        self.recording_item.addChild(self.timestamp_item)
        self.recording_item.addChild(self.coordinates_item)
        self.recording_item.addChild(self.rec_length_item)
        self.recording_item.addChild(self.spatial_res_item)
        self.recording_item.addChild(self.overload_item)
        self.recording_item.addChild(self.speed_item)

        # smp items

        self.smp_serial_item = QTreeWidgetItem((None, None, 'Serial Number', None, ''))
        self.smp_firmware_item = QTreeWidgetItem((None, None, 'Firmware Version', None, ''))
        self.smp_length_item = QTreeWidgetItem((None, None, 'Max. Recording Length', None, ''))
        self.smp_tipdiameter_item = QTreeWidgetItem((None, None, 'Tip Diameter', None, ''))
        self.smp_sensor_sensitivity_item = QTreeWidgetItem((None, None, 'Sensor Sensitivity', None, ''))
        self.smp_sensor_serial_item = QTreeWidgetItem((None, None, 'Sensor Serial Number', None, ''))
        self.smp_amp_item = QTreeWidgetItem((None, None, 'Amplifier Serial Number', None, ''))

        self.smp_item.addChild(self.smp_serial_item)
        self.smp_item.addChild(self.smp_firmware_item)
        self.smp_item.addChild(self.smp_length_item)
        self.smp_item.addChild(self.smp_tipdiameter_item)
        self.smp_item.addChild(self.smp_sensor_sensitivity_item)
        self.smp_item.addChild(self.smp_sensor_serial_item)
        self.smp_item.addChild(self.smp_amp_item)

        # drift items
        self.drift_begin_item = QTreeWidgetItem((None, None, 'Begin', None, ''))
        self.drift_end_item = QTreeWidgetItem((None, None, 'End', None, ''))
        self.drift_value_item = QTreeWidgetItem((None, None, 'Drift', None, ''))
        self.offset_value_item = QTreeWidgetItem((None, None, 'Offset', None, ''))
        self.noise_value_item = QTreeWidgetItem((None, None, 'Noise', None, ''))

        self.drift_item.addChild(self.drift_begin_item)
        self.drift_item.addChild(self.drift_end_item)
        self.drift_item.addChild(self.drift_value_item)
        self.drift_item.addChild(self.offset_value_item)
        self.drift_item.addChild(self.noise_value_item)

        # Tight up the columns
        self.expandAll()
        self.setColumnWidth(0, 0)
        self.resizeColumnToContents(1)
        self.resizeColumnToContents(2)
        self.resizeColumnToContents(3)

    def set_document(self, doc):
        if doc is None:
            return

        p = doc.profile

        self.name_item.setText(self.TEXT_COLUMN, p.name)
        self.pnt_filename_item.setText(self.TEXT_COLUMN, str(p.pnt_file))
        self.timestamp_item.setText(self.TEXT_COLUMN, str(p.timestamp))
        self.rec_length_item.setText(self.TEXT_COLUMN, '{:.0f} mm ({:n} Samples)'.format(p.recording_length, len(p)))

        if p.coordinates:
            lat, long = ['{:.6f}'.format(c) for c in p.coordinates]
            url = '<a href="https://www.google.com/maps/search/?api=1&query={lat},{long}">{lat}, {long}</a>'.format(
                lat=lat, long=long)
        else:
            url = 'None'
        url_label = QLabel(url)
        url_label.setContentsMargins(5, 0, 0, 0)
        url_label.setOpenExternalLinks(True)
        self.setItemWidget(self.coordinates_item, 4, url_label)

        spatial_res = '{:.3f} µm'.format(p.spatial_resolution * 1000)
        self.spatial_res_item.setText(self.TEXT_COLUMN, spatial_res)
        overload = '{:.1f} N'.format(p.overload)
        self.overload_item.setText(self.TEXT_COLUMN, overload)
        speed = '{:.1f} mm/s'.format(p.speed)
        self.speed_item.setText(self.TEXT_COLUMN, speed)

        self.smp_serial_item.setText(self.TEXT_COLUMN, p.smp_serial)
        self.smp_firmware_item.setText(self.TEXT_COLUMN, p.smp_firmware)
        length = '{} mm'.format(p.smp_length)
        self.smp_length_item.setText(self.TEXT_COLUMN, length)
        tipdiameter = '{:.1f} mm'.format(p.smp_tipdiameter / 1000)
        self.smp_tipdiameter_item.setText(self.TEXT_COLUMN, tipdiameter)
        self.smp_sensor_serial_item.setText(self.TEXT_COLUMN, p.sensor_serial)
        self.smp_sensor_sensitivity_item.setText(self.TEXT_COLUMN, '{}  pC/N'.format(p.sensor_sensitivity))
        self.smp_amp_item.setText(self.TEXT_COLUMN, p.amplifier_serial)

        # Drop all existing markers
        for label, item in self.marker_items.items():
            self.markers_item.removeChild(item)
        self.marker_items = {}

        for label, value in p.markers.items():
            self.set_marker(label, value)

    def set_marker(self, label, value):
        if value is None:
            if label in self.marker_items:
                item = self.marker_items[label]
                self.markers_item.removeChild(item)
                del self.marker_items[label]
            return

        value = '{:.3f}'.format(value)
        if label not in self.marker_items:
            item = MarkerTreeItem(self.markers_item, label)

            # This is a bit tricky: We call the methods on main_window which
            # call this method again...

            def set_marker():
                self.main_window.set_marker(label, item.lineedit.text())

            item.lineedit.editingFinished.connect(set_marker)

            def delete_marker(checked):
                self.main_window.set_marker(label, None)

            item.delete_button.clicked.connect(delete_marker)

            self.marker_items[label] = item
            self.markers_item.addChild(item)

        item = self.marker_items[label]
        item.lineedit.setText(value)

    def set_drift(self, begin_label, end_label, drift, offset, noise):
        self.drift_begin_item.setText(self.TEXT_COLUMN, begin_label)
        self.drift_end_item.setText(self.TEXT_COLUMN, end_label)
        self.drift_value_item.setText(self.TEXT_COLUMN, '{:.2g} mN/m'.format(drift * 1000 * 1000))
        self.offset_value_item.setText(self.TEXT_COLUMN, '{:.2f} mN'.format(offset * 1000))
        self.noise_value_item.setText(self.TEXT_COLUMN, '{:.2f} mN'.format(noise * 1000))


class MarkerTreeItem(QTreeWidgetItem):

    def __init__(self, parent, name, deletable=True):
        super(MarkerTreeItem, self).__init__(parent)

        self.delete_button = QPushButton()
        self.delete_button.setIcon(QIcon(':/icons/delete.png'))

        self.detect_button = QPushButton()
        self.detect_button.setIcon(QIcon(':/icons/autodetect.png'))

        self.lineedit = QLineEdit(self.treeWidget())
        self.lineedit.setValidator(QDoubleValidator())

        if deletable:
            self.treeWidget().setItemWidget(self, 1, self.delete_button)
        self.setText(2, name)
        if name in ['surface', 'ground']:
            self.treeWidget().setItemWidget(self, 3, self.detect_button)
        self.treeWidget().setItemWidget(self, 4, self.lineedit)

    @property
    def name(self):
        return self.text(2)

    @property
    def value(self):
        return self.lineedit.value()

    def lineedit_focused(self):
        pass

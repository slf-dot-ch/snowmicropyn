import logging
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from snowmicropyn.examiner.globals import APP_TECH_NAME, VERSION
from snowmicropyn.examiner.log_window import LogWindow
from snowmicropyn.examiner.main_window import MainWindow


app = QApplication(sys.argv)
app.setAttribute(Qt.AA_UseHighDpiPixmaps)
app.setOrganizationName('SLF')
app.setOrganizationDomain('slf.ch')
app.setApplicationName(APP_TECH_NAME)

log_window = LogWindow()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(log_window)

log = logging.getLogger(__name__)
log.info('Launching snowmicropyn Profile Examiner, Version {}'.format(VERSION))

main_window = MainWindow(log_window)
main_window.show()

sys.exit(app.exec_())

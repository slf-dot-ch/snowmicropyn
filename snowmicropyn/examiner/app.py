import logging
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from snowmicropyn.examiner.globals import *
from snowmicropyn.examiner.log_window import LogWindow
from snowmicropyn.examiner.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app.setOrganizationName(ORG_NAME)
    app.setOrganizationDomain(ORG_DOMAIN)
    app.setApplicationName(APP_NAME.replace(' ', '_').lower())
    app.setApplicationVersion(VERSION)

    log_window = LogWindow()
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(log_window)
    logger.addHandler(logging.StreamHandler(stream=sys.stdout))

    log = logging.getLogger(__name__)
    log.info('Launching {}, Version {}, Git Hash: {}'.format(APP_NAME, VERSION, GITHASH))

    main_window = MainWindow(log_window)
    main_window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

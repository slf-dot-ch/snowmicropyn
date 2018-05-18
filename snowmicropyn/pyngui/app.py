import logging
import sys
import pathlib

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from snowmicropyn.pyngui.globals import *
from snowmicropyn.pyngui.log_window import LogWindow
from snowmicropyn.pyngui.main_window import MainWindow


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
    log.info('Launching {}, version {}, git hash: {}'.format(APP_NAME, VERSION, GITHASH))

    main_window = MainWindow(log_window)
    paths = [pathlib.Path(p) for p in sys.argv[1:]]
    pnt_files = [p for p in paths if p.is_file() and p.suffix == '.pnt']
    for f in pnt_files:
        log.info('Opening file {}'.format(f))
        main_window.open_pnts([f])

    main_window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()

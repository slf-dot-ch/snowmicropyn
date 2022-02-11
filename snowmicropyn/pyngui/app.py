"""GUI entry point."""

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

    logger = logging.getLogger('pyngui')
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler(stream=sys.stdout))
    logger.addHandler(LogWindow()) # do not keep LogWindow in scope manually --> crashes

    logger.info('Launching {}, version {}, git hash: {}'.format(APP_NAME, VERSION, GITHASH))

    main_window = MainWindow()
    paths = [pathlib.Path(p) for p in sys.argv[1:]]
    pnt_files = [p for p in paths if p.is_file() and p.suffix == '.pnt']
    for f in pnt_files:
        logger.info('Opening file {}'.format(f))
        main_window.open_pnts([f])

    main_window.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()

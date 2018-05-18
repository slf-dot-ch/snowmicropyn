import logging

from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QMainWindow, QPlainTextEdit


class LogWindow(QMainWindow, logging.Handler):
    FORMAT = '%(asctime)s  %(levelname)s  %(message)s'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('Log')
        self.setMinimumSize(200, 200)
        self.setGeometry(100, 100, 600, 300)

        monospace = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        monospace.setPointSize(11)

        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        self.text.setFont(monospace)

        self.setCentralWidget(self.text)

        self.setFormatter(logging.Formatter(self.FORMAT))

    def emit(self, record):
        self.text.appendPlainText(self.format(record))

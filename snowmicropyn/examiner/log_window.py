import logging

from PyQt5.QtWidgets import QMainWindow, QPlainTextEdit


class LogWindow(QMainWindow, logging.Handler):
    FORMAT = '%(asctime)s\t%(levelname)s\t%(message)s'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('Log')
        self.setMinimumSize(200, 200)
        self.setGeometry(100, 100, 600, 300)

        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)

        self.setCentralWidget(self.text)

        self.setFormatter(logging.Formatter(self.FORMAT))

    def emit(self, record):
        self.text.appendPlainText(self.format(record))

import logging
from os.path import dirname, abspath, join
from string import Template

from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QMainWindow

log = logging.getLogger(__name__)


class MapWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('Map')
        self.setMinimumSize(200, 200)
        self.setGeometry(100, 100, 600, 300)

        self.browser = QWebEngineView()

        here = dirname(abspath(__file__))
        with open(join(here, 'map.html'), encoding='utf-8') as f:
            self.template = Template(f.read())

        self.setCentralWidget(self.browser)

    def set_documents(self, docs):
        # json must look like:
        # {"title": "Name", "lat": 46.845104217529297, "lng": 9.871776580810547},...

        if docs:
            profiles = [d.profile for d in docs if d.profile.coordinates]
            json_line = '{{"title": "{name}", "lat": {lat}, "lng": {lng}}}'
            json = ','.join([json_line.format(name=p.name, lat=p.coordinates[0], lng=p.coordinates[1]) for p in profiles])

            content = self.template.substitute(json=json)
            self.browser.setHtml(content)
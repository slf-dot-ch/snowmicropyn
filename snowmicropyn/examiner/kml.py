import logging

log = logging.getLogger(__name__)

_basics = """
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>SMP</name>
    <Folder>
{content}
    </Folder>
  </Document>
</kml>
""".strip()

_placemark = """
      <Placemark>
        <name>{name}</name>
        <description>
        <![CDATA[
        {desc}
        ]]>
        </description>
        <Point>
          <coordinates>{longitude},{latitude}</coordinates>
        </Point>
      </Placemark>
"""

_desc = 'SnowMicroPen Profile, recorded at {}.</p>'


def export2kml(filename, documents):

    placemarks = []
    for doc in documents:
        p = doc.profile
        if p.coordinates:
            long = p.coordinates[1]
            lat = p.coordinates[0]
            desc = _desc.format(p.timestamp)
            pm = _placemark.format(name=p.name, desc=desc, longitude=long, latitude=lat)
            placemarks.append(pm)

    if placemarks:
        with open(filename, 'w') as f:
            kml = _basics.format(content=''.join(placemarks))
            f.write(kml)

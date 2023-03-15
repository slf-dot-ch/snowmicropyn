#!/usr/bin/env python3
# Unit test for CAAML output: validation against its schema

from lxml import etree
import os
import requests
import snowmicropyn as smp
from snowmicropyn.pyngui.document import Document

def validate(xml_file: str, xsd_file: str):
    xml_doc = etree.parse(xml_file)
    schema_doc = etree.parse(xsd_file)
    schema = etree.XMLSchema(schema_doc)
    schema.assertValid(xml_doc)

if __name__ == "__main__":
    pro = smp.Profile.load('../examples/profiles/S37M0876.pnt')
    testfile = "./test_caaml.caaml"
    doc = Document(pro)
    doc.export_caaml(testfile)

    xsd_file = "./CAAMLv6_SnowProfileIACS.xsd"
    if not os.path.exists(xsd_file):
        res = requests.get(f"http://caaml.org/Schemas/SnowProfileIACS/v6.0.3/{xsd_file}")
        open(xsd_file, "wb").write(res.content)
    #validate(testfile, xsd_file)
    validate("../examples/profiles/S37M0876_smp.caaml", xsd_file)

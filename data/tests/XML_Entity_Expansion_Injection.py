import xml.etree.ElementTree as ET

tree = ET.parse('country_data.xml')
root = ET.fromstring(country_data_as_string)
result = ET.iterparse(source)
result = ET.XML(source)
result = ET.XMLID(source)

from xml.dom import minidom

result = minidom.parse(filename_or_file)
result = minidom.parseString(string)

from xml.dom import pulldom

doc = pulldom.parse('sales_items.xml')
doc = pulldom.parseString(string)

import xml.sax

result = xml.sax.make_parser()
result = xml.sax.parse(filename_or_stream, handler)
result = xml.sax.parseString(string, handler)

from xml.parsers.expat import ParserCreate, ExpatError, errors
p = ParserCreate()
p.Parse(some_xml_document)
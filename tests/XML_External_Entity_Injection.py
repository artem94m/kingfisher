from xml.dom import pulldom

doc = pulldom.parse('sales_items.xml')
doc = pulldom.parseString(string)

import xml.sax

result = xml.sax.make_parser()
result = xml.sax.parse(filename_or_stream, handler)
result = xml.sax.parseString(string, handler)
from lxml import etree as ET
import sys
import os
import re

import httplib2
import codecs
import urllib
h = httplib2.Http()

useragent='openOV/syntus_0.1'
headers={'user-agent': useragent}

structuur = re.compile('([0-9]+)_([0-9]+)_([0-9]+)_(.+)_(.+) naar: (.+)')
lijnen = set()

for (root, dirs, files) in os.walk(sys.argv[1]):
    for f in files:
        try:
            x = ET.parse('%s/%s'%(sys.argv[1], f)).getroot()
            lijnnummers = x.findall('.//Lijnnummer')
            for ln in lijnnummers:
                lijnen.add(ln.text)
        except:
            pass

print '\n'.join(lijnen)

poly_url = "http://www.syntus.nl/reisinfozho/sim/getPolyline.aspx?lijn=%s&richting=%s&start=%s&stop=%s&variant=%s"

for lijn in lijnen:
    s = structuur.match(lijn)
    id = s.group(1)
    richting = s.group(2)
    start = urllib.quote_plus(s.group(5))
    stop = urllib.quote_plus(s.group(6))
    variant = s.group(3)

    response, content = h.request(poly_url%(id, richting, start, stop, variant))
    f = codecs.open('polyline_xml/%s_%s_%s.xml'%(id,richting,variant), 'w', 'UTF-8')
    f.write(content)
    f.close()


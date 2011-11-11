from lxml import etree as ET
import sys
import os
import re

import datetime
import httplib2
import codecs
import urllib
h = httplib2.Http()

useragent='openOV/syntus_0.1'
headers={'user-agent': useragent}

structuur = re.compile('([0-9]+)_([0-9]+)_([0-9]+)_(.+)_(.+) naar: (.+)')
lijnen = set()

url="http://www.syntus.nl/reisinfozho/sim/haltestaat.aspx?Lijn=%s&Richting=%s&Reisdatum=%s&variant=%s"

for (root, dirs, files) in os.walk('xml'):
    for f in files:
        try:
            x = ET.parse('xml/%s'%(f)).getroot()
            lijnnummers = x.findall('.//Lijnnummer')
            for ln in lijnnummers:
                lijnen.add(ln.text)
        except:
            pass

for lijn in lijnen:
    s = structuur.match(lijn)
    lijnid = s.group(1)
    richting = s.group(2)
    start = urllib.quote_plus(s.group(5))
    stop = urllib.quote_plus(s.group(6))
    variant = s.group(3)
    
    datum = datetime.datetime.now()

    for delta in range(0,6):
        datum += datetime.timedelta(1)
        datum_str = datum.strftime('%Y%m%d')
        response, content = h.request(url%(lijnid,richting,datum_str,variant))
        f = codecs.open('haltestaten/%s_%s_%s.html'%(datum_str,lijnid,richting), 'w', 'UTF-8')
        f.write(content)
        f.close()

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

url="http://www.syntus.nl/reisinfozho/sim/PopupHalteInfoNew.aspx?type=lijn&Lijn=%s,%s,%s,%s,%s&Richting=%s&Haltenummer=%s&variant=%s"

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

    x = ET.parse('polyline_xml/%s_%s_%s.xml'%(lijnid,richting,variant)).getroot()
    haltes = x.findall('.//Halte')
    for halte in haltes:
        halteid = halte.find('Nummer').text
        halte_url = url%(lijnid, richting, start, stop, variant, richting, halteid, variant)
    
        response, content = h.request(halte_url)
        f = codecs.open('halte_xml/%s_%s_%s.xml'%(lijnid,richting,halteid), 'w', 'UTF-8')
        f.write(content)
        f.close()

from lxml import etree as ET
import sys
import os
import re

import httplib2
import codecs

from polyline_decode import decode_line

output = '<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://earth.google.com/kml/2.2">\n'

for (root, dirs, files) in os.walk('xml_polyline'):
    for f in files:
        print f
        x = ET.parse('%s/%s'%('xml_polyline', f)).getroot()
        polyline = x.find('.//PolyLine').text
        polyline = decode_line(polyline)
        coordinates = ' '.join([str(t[0])+','+str(t[1]) for t in polyline])
        route = x.find('.//route').text
        lijnid = x.find('.//lijnNummer').text
        output += '<Document id="%s"><Placemark id="%s"><name>%s</name><LineString><coordinates>%s</coordinates></LineString></Placemark>\n'%(f, lijnid, route, coordinates)

        haltes = x.findall('.//Halte')
        for halte in haltes:
            naam = halte.find('Naam').text
            lat = halte.find('Lat').text
            lng = halte.find('Lng').text
            id = halte.find('Nummer').text

            output += '<Placemark id="%s"><name>%s</name><Point><coordinates>%s,%s</coordinates></Point></Placemark>\n'%(id, naam, lng, lat)

        output += '</Document>'

output += '</kml>'
print output

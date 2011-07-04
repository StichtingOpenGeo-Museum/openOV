# -*- coding: utf-8 -*-
import json
import codecs
import sys

f = codecs.open(sys.argv[1], encoding='utf-8', mode='r')
j = json.load(f)

o = codecs.open('connexxion.kml', encoding='utf-8', mode='w')
o.write('<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://earth.google.com/kml/2.2"><Document>')

for i in range(1, len(j['HALTELIST']['ID'])):
	o.write("<Placemark id='%s'><name>%s</name><Point><coordinates>%s,%s</coordinates></Point></Placemark>" % (j['HALTELIST']['ID'][i], j['HALTELIST']['KORTENAAM'][i].replace('&', '&amp;'), j['HALTELIST']['X'][i]/10000000.0, j['HALTELIST']['Y'][i]/10000000.0))

o.write('</Document></kml>')
o.close()

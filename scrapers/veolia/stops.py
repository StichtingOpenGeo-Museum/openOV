import simplejson
import sys
import codecs

output = codecs.open( sys.argv[2], "w", "utf-8" )
output.write('<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://earth.google.com/kml/2.2"><Document>')

def parse(filename):
	i = codecs.open(filename, 'r', 'utf-8').read()
	stopid = 1

	for row in i.split('\n'):
		try:
			[coords, town, name] = row.split(', ')
			[lat, lon] = coords.replace(' ', '').split(',')
			town = town.replace("\\'", "'")
			name = name.replace("\\'", "'")
		
			output.write("<Placemark id='%s'><name>%s</name><Point><coordinates>%s,%s</coordinates></Point></Placemark>" % (stopid, town+', '+name.replace('&', '&amp;'), lon, lat))
			stopid += 1
		except:
			print row
			pass


parse(sys.argv[1])

output.write('</Document></kml>')

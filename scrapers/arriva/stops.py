import simplejson
import sys
import codecs

output = codecs.open( sys.argv[2], "w", "utf-8" )
output.write('<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://earth.google.com/kml/2.2"><Document>')

def parse(filename):
	rows = simplejson.load(open(filename))['rows']

	for row in rows:
		v = row['value']
		lon = v['Longitude']
		lat = v['Latitude']
		name = v['Name']
		lineids = v['LineIds']
		cityid = v['CityId']
		bus = v['TransportType']['Bus'] == 1
		train = v['TransportType']['Train'] == 1

		for stopid, val in v['StopIds'].items():
			shelter = val['Shelter'] == 1
			bicycle = val['BicycleRack'] == 1
			lighting = val['Lighting'] == 1
			access = val['Accessibility'] == 1
			avail = val['Availability'] == 1

			output.write("<Placemark id='%s'><name>%s</name><Point><coordinates>%s,%s</coordinates></Point></Placemark>" % (stopid, name.replace('&', '&amp;'), lon, lat))


parse(sys.argv[1])

output.write('</Document></kml>')

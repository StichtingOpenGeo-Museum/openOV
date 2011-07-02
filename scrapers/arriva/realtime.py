import sys
from BeautifulSoup import BeautifulSoup

f = open(sys.argv[1])

soup = BeautifulSoup(f.read())

realtime = soup.find('table', {"id" : "realtime-table" })

if realtime is not None:
	for row in realtime.findAll('tr')[1:]:
		items = row.findAll('td')
		[linenumber, linename] = items[0].text[5:].split(' naar ')
		target = items[1].text
		expected = items[2].text

		if expected == '-':
			expected = ''

		print '%s\t%s\t%s\t%s' % (linenumber, linename, target, expected)

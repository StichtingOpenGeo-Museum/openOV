import sys
import datetime
from BeautifulSoup import BeautifulSoup

f = open(sys.argv[1])

soup = BeautifulSoup(f.read())

operdate = soup.find('input', {"id" : "realtime-date" })['value']
operdate = datetime.datetime.strptime(operdate, "%d-%m-%Y").date()

realtime = soup.find('table', {"id" : "realtime-table" })

if realtime is not None:
	prev = 0
	for row in realtime.findAll('tr')[1:]:
		items = row.findAll('td')
		[linenumber, linename] = items[0].text[5:].split(' naar ')
		target = items[1].text
		expected = items[2].text

		now = int(target.split(':')[0])
		if prev > now:
			operdate = operdate.replace(day = operdate.day + 1)

		prev = now

		if expected == '-':
			expected = ''

		print '%s\t%s\t%s\t%s\t%s' % (operdate, linenumber, linename, target, expected)

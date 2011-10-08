import re
import httplib2
import sqlite3
import os
from BeautifulSoup import BeautifulSoup

h = httplib2.Http()
useragent="Mozilla/5.0 (iPod; U; CPU iPhone OS 3_1_2 like Mac OS X; nl-nl) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7D11 Safari/528.16"
headers={'user-agent': useragent}
halteurl = "http://www.ret.nl/Reizen-met-RET/Dienstregeling/Halte-informatie.aspx?id=%s"
onloadlatlon = re.compile('.*\(([0-9\.]+),([0-9\.]+)\).*')

batch = []

conn = sqlite3.connect('ret.sqlite3')
c = conn.cursor()
c.execute('select distinct stop_id from stops')
stops = []
for row in c:
    stops.append(row[0])

for root, dirs, files in os.walk('stops'):
    for fname in files:
            stop_id, stop_name = fname.split(',')
            if stop_id not in stops:
                soup = BeautifulSoup(open('stops/%s'%(fname)).read())
                stop_name = unicode(stop_name, 'utf-8').replace('_', '/')
                latlon = onloadlatlon.match(soup.find('body')['onload'])

                batch.append((stop_id, stop_name, latlon.group(1), latlon.group(2)))

c.executemany('insert into stops (stop_id, stop_name, stop_lat, stop_lon) values (?,?,?,?)', batch)
conn.commit()
conn.close()

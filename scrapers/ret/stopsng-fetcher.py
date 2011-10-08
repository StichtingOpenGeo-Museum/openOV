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
c.execute('select distinct stop_id, stop_name from lookup_stops')
for row in c:
    filename = 'stops/%s,%s'%(row[0],row[1].replace('/','_'))
    if not os.path.exists(filename):
        url = halteurl%(row[0])
        print url
        response, content = h.request(url, headers=headers)
        if response['status'] == '200':
            f = open(filename, 'w')
            f.write(content)
            f.close()

    try:
        soup = BeautifulSoup(open(filename).read())
        latlon = onloadlatlon.match(soup.find('body')['onload'])

        batch.append((row[0], row[1], latlon.group(1), latlon.group(2)))
    except:
        pass

c.executemany('insert into stops (stop_id, stop_name, stop_lat, stop_lon) values (?,?,?,?)', batch)
conn.commit()
conn.close()

#!/usr/bin/env python

import httplib2
import codecs
h = httplib2.Http()

useragent='openOV/syntus_0.1'
headers={'user-agent': useragent}

url = "http://www.syntus.nl/reisinfozho/sim/getHaltes.aspx?showlijnen=true&nex=%d&ney=%d&swx=%d&swy=%d"

for x in range(5, 8, 2):
    for y in range(51, 53, 1):
        response, content = h.request(url%(x+2, y+1, x, y))
        f = codecs.open('xml/%d_%d.xml'%(x, y), 'w', 'UTF-8')
        f.write(content)
        f.close()


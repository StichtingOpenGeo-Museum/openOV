import httplib2
import urllib
import re
import os
import codecs
import sqlite3
from BeautifulSoup import BeautifulSoup

haltehref = re.compile('.*id=(.*?)&.*')
linehref = re.compile('.*selectedline=([0-9]+)&.*')

def fetchevent(content):
    chunks = content.split('|')
    eventvalidation = None
    viewstate = None
    seq = 0
    while ((eventvalidation is None or viewstate is None) and seq < len(chunks)):
        if chunks[seq]=='__EVENTVALIDATION':
            seq += 1
            eventvalidation = chunks[seq]
        elif chunks[seq]=='__VIEWSTATE':
            seq += 1
            viewstate = chunks[seq]
        else:
            seq += 1

    return [eventvalidation, viewstate]

def fetcheventplain(soup):
    viewstate = soup.findAll(id="__VIEWSTATE")[0]['value']
    eventvalidation = soup.findAll(id="__EVENTVALIDATION")[0]['value']
    return [eventvalidation, viewstate]

def parsehaltes(content):
    soup = BeautifulSoup(content)
    hlLink = soup.findAll(id=re.compile("^content_.*_hlLink$"))
    haltes = {}
    for halte in hlLink:
        matches = haltehref.match(halte['href'])
        
        halteid = matches.group(1)
        haltenaam = halte.text

        haltes[halteid] = haltenaam

    return haltes

def fetchroutelater(content, url, headers):
    eventvalidation, viewstate = fetchevent(content)
    data = {'scm1' : 'content_0$UpdatePanel1|content_0$lnkLater',
            'content_0$ddlTimeOffset': '100',
            '__VIEWSTATE': viewstate,
            '__EVENTVALIDATION': eventvalidation,
            '__ASYNCPOST': 'true',
            '__EVENTTARGET': 'content_0$lnkLater'}

    response, content = h.request(url, "POST", urllib.urlencode(data), headers=headers)
    if response['status'] == '200':
        return parsehaltes(content)

def fetchroute(content, url, direction, headers):
    directionlookup = {0: 'Heen', 1: 'Terug'}
    
    ht = directionlookup[direction]
    headers['X-MicrosoftAjax'] = 'Delta=true'
    headers['Content-type'] = 'application/x-www-form-urlencoded'

    soup = BeautifulSoup(content)
    eventvalidation, viewstate = fetcheventplain(soup)
    routetext = soup.findAll(id=re.compile("btn%s$"%(ht)))[0]['value'].replace('Richting ', '').replace('/', '_')
    print routetext

    data = {'__VIEWSTATE': viewstate,
            '__EVENTVALIDATION': eventvalidation,
            '__ASYNCPOST': 'true',
            'scm1': 'content_0$UpdatePanel1|content_0$btn%s'%(ht),
            'content_0$btn%s'%(ht): soup.findAll(id=re.compile("btn%s$"%(ht)))[0]['value'] }

    response, content = h.request(url, "POST", urllib.urlencode(data), headers=headers)
    if response['status'] == '200':
        first  = parsehaltes(content)
#        if len(first) > 0 and direction == 0:
#            second = fetchroutelater(content, url, headers)
#            first.update(second)
#        print first
        return first

def fetchlinelist(modality, headers):
    response, content = h.request("http://www.ret.nl/Reizen-met-RET/Dienstregeling.aspx?modality=%s"%(modality), headers=headers)
    if response['status'] == '200':
        headers['Cookie'] = response['set-cookie']
        soup = BeautifulSoup(content)
        return soup.findAll(id=re.compile('content_0_rpLines_ctl[0-9][0-9]_hlLink'))

def fetchline(modality, id, headers):
    url = "http://www.ret.nl/Reizen-met-RET/Dienstregeling/%s.aspx?selectedline=%s&modality=%s" % (modalities[modality], id, modality)
    print url
    response, content = h.request(url, headers=headers)
    if response['status'] == '200':
        haltes = {}
        haltes[0] = fetchroute(content, url, 0, headers)
        haltes[1] = fetchroute(content, url, 1, headers)
        return haltes

def fetchferry(modality, headers):
    url = "http://www.ret.nl/Reizen-met-RET/Dienstregeling/%s.aspx?modality=%s" % (modalities[modality], modality)
    print url
    response, content = h.request(url, headers=headers)
    if response['status'] == '200':
        first  = parsehaltes(content)
        if len(first) > 0:
            second = fetchroutelater(content, url, headers)
            first.update(second)
 
        haltes = {0: first}
        return haltes

def writehaltes(modality, route_short_name, haltes):
    modalitylookup = { 'T': 0, 'M': 1, 'B': 3, 'F': 4 }
    route_type = modalitylookup[modality]
    batch = []
    for (direction_id, stops) in haltes.items():
        for (stop_id, stop_name) in stops.items():
            batch.append((str(stop_id), str(route_type), str(route_short_name), str(direction_id), stop_name))

    if len(batch) > 0:
        print batch
        conn = sqlite3.connect('ret.sqlite3')
        c = conn.cursor()
        c.executemany('insert into lookup_stops (stop_id, route_type, route_short_name, direction_id, stop_name) values (?,?,?,?,?)', batch)
        conn.commit()
        conn.close()
        
useragent="Mozilla/5.0 (iPod; U; CPU iPhone OS 3_1_2 like Mac OS X; nl-nl) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7D11 Safari/528.16"
headers={'user-agent': useragent}
h = httplib2.Http()

modalities = {'T': 'Tram', 'B': 'Bus', 'M': 'Metro'}

for modality, modality_name in modalities.items():
    linelist = fetchlinelist(modality, headers)
    for line in linelist:
        haltes = fetchline(modality, linehref.match(line['href']).group(1), headers)
        writehaltes(modality, line.text.split(' ')[1].replace('/', '_'), haltes)

modalities['F'] = 'Fast-Ferry'

haltes = fetchferry('F', headers)
writehaltes('F', 'F', haltes)

import httplib2
import urllib
import re
import os
import codecs
import time
import datetime
from BeautifulSoup import BeautifulSoup
from timetables import parsetimetable
from fuzzydict import FuzzyDict
import cPickle as pickle

transformdate = re.compile('.* ([0-9]+)-([0-9]+)-([0-9]+)')
tmp_cm = set(())

def gcalendar(service_id, monday, tuesday, wednesday, thursday, friday, saturday, sunday, start_date, end_date):
    line = ','.join([str(service_id), str(monday), str(tuesday), str(wednesday), str(thursday), str(friday), str(saturday), str(sunday), start_date, end_date])
    calendartxt.write(line+'\n')
    calendartxt.flush()

def stop_times(trip_id, arrival_time, departure_time, stop_id, stop_sequence, stop_headsign, pickup_type, drop_off_type, shape_dist_traveled):
    line = ','.join([trip_id, arrival_time, departure_time, stop_id, stop_sequence, stop_headsign, pickup_type, drop_off_type, shape_dist_traveled])
    stop_timestxt.write(line+'\n')
    stop_timestxt.flush()

def trips(route_id, service_id, trip_id, trip_headsign, trip_short_name, direction_id, block_id, shape_id):
    line = ','.join([str(route_id), str(service_id), str(trip_id), trip_headsign, trip_short_name, direction_id, block_id, shape_id])
    tripstxt.write(line+'\n')
    tripstxt.flush()

def calendarmagic(d, start_date, end_date):
    service_id = 0
    for x in d.keys():
        service_id += 2**(d[x]*x)

    if service_id not in tmp_cm:
        tmp_cm.add(service_id)
        gcalendar(service_id, d[0]*1, d[1]*1, d[2]*1, d[3]*1, d[4]*1, d[5]*1, d[6]*1, start_date, end_date)
    return service_id

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

def aankomstvertrek_topickup(value):
    if True: # dan alleen aankomst
        return '1'
    else:
        return '0'

linehref = re.compile('.*selectedline=([0-9]+)&.*')

useragent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.159 Safari/535.1'
headers={'user-agent': useragent}
h = httplib2.Http()

operator='RET'

def tmp(content, *args):
    tmp = open('tmp/TEST-%s'%'-'.join(args), 'w')
    tmp.write(content)
    tmp.close()

def tmp2(content, *args):
    tmp = open('tmp/TEST-%s.pickle'%'-'.join(args), 'w')
    pickle.dump(content,tmp)
    tmp.close()

def incache2(*args):
    path = 'tmp/TEST-%s.pickle'%'-'.join(args)
    if os.path.exists(path):
        print path
        f = open(path, 'r')
        result = pickle.load(f)
        f.close()
        return result
    else:
        return False

def incache(*args):
    path = 'tmp/TEST-%s'%'-'.join(args)
    if os.path.exists(path):
        print path
        f = open(path)
        contents = f.read()
        f.close()
        return contents
    else:
        return False

fuzzlookup = {}
for _root, _dirs, files in os.walk('stops'):
    for fname in files:
        stopid, name = fname.split(',')
        fuzzlookup[name.replace('_', '/')] = stopid

f = open('tmp/stops.pickle')
stoplookup = pickle.load(f)
f.close()

fuzzylookup = FuzzyDict(fuzzlookup)

calendartxt = open('%s/calendar.txt'%(operator), 'w')
calendartxt.write('service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date\n')
stop_timestxt = open('%s/stop_times.txt'%(operator), 'w')
stop_timestxt.write('trip_id,arrival_time,departure_time,stop_id,stop_sequence,stop_headsign,pickup_type,drop_off_type,shape_dist_traveled\n')
tripstxt = open('%s/trips.txt'%(operator), 'w')
tripstxt.write('route_id,service_id,trip_id,trip_headsign,trip_short_name,direction_id,block_id,shape_id\n')

lasttripid = 0
dates = {}

response, content = h.request("http://www.ret.nl/reizen-met-ret/dienstregeling/Metro.aspx")
if response['status'] == '200':
    tmp(content, operator, 'M')
    soup = BeautifulSoup(content)
    datelist = soup.findAll(id='plhmiddle_0_plhcontent_0_ddlDate')[0]
    today = datetime.date.today()
    for option in datelist.findAll('option'):
        dateparts = transformdate.match(option.text)
        thisdate = datetime.date(int(dateparts.group(3)), int(dateparts.group(2)), int(dateparts.group(1)))
        if thisdate >= today and thisdate.day < 15: # 15 vanwege lijn 92, haltes nog onbekend
            dates[int(option['value'])] = '%.4d%.2d%.2d'%(int(dateparts.group(3)), int(dateparts.group(2)), int(dateparts.group(1)))

sorted(dates)
calendarresults = {}
start_date = min(dates.values())
end_date = max(dates.values())

modalities = {'T': 'tram', 'B': 'bus', 'M': 'metro'}
directions = {'To': 0, 'Return': 1}

for (internal, datum) in dates.items():
    print 'Verwerken... %s'%(datum)

    for modality, modality_name in modalities.items():
        response, content = h.request("http://www.ret.nl/reizen-met-ret/dienstregeling/%s.aspx"%(modality_name))
        if response['status'] == '200':
            tmp(content, operator, modality)
            headers['Cookie'] = response['set-cookie']

            soup = BeautifulSoup(content)

            viewstate = soup.findAll(id="__VIEWSTATE")[0]['value']
            eventvalidation = soup.findAll(id="__EVENTVALIDATION")[0]['value']
            headers['X-MicrosoftAjax'] = 'Delta=true'
            headers['Content-type'] = 'application/x-www-form-urlencoded'

            offset = '0'
            last = None

            linelist = soup.findAll(id='plhmiddle_0_plhcontent_0_ddlLine')[0]
            for line in linelist.findAll('option'):
                linenumber = line.text.split(' ')[1].replace('/','_')
                lineid     = line['value']

                for direction in directions.keys():

                    calendar = {0: False, 1: False, 2: False, 3: False, 4: False, 5: False, 6: False}
                    tripids = set()

                    while True:
                        cached = incache2(operator, modality, lineid, str(directions[direction]), datum, offset)
                        if not cached:
                            cached = incache(operator, modality, lineid, str(directions[direction]), datum, offset)
                            if not cached:
                                print 'Downloading... viewstate %d'%len(viewstate)
                                data = {'__VIEWSTATE': viewstate, '__EVENTVALIDATION': eventvalidation, '__EVENTTARGET': 'plhmiddle_0$plhcontent_0$ddlDate',
                                         'ScriptManager1': 'plhmiddle_0$plhcontent_0$UpdatePanel1|plhmiddle_0$plhcontent_0$ddlDate',
                                         'plhmiddle_0$plhcontent_0$Direction': 'rbTrip'+direction,
                                         'plhmiddle_0$plhcontent_0$ddlLine': lineid,
                                         'plhmiddle_0$plhcontent_0$ddlDate': internal,
                                         'plhmiddle_0$plhcontent_0$ddlTimeOffset': offset,
                                         '__ASYNCPOST': 'true',
                                         '__EVENTARGUMENT': '',
                                         '__LASTFOCUS:': ''
                                        }

                                response, content = h.request("http://www.ret.nl/reizen-met-ret/dienstregeling/%s.aspx"%(modality_name), "POST", urllib.urlencode(data), headers=headers)
                                if response['status'] == '200':
                                    headers['Cookie'] = response['set-cookie']
                                    tmp(content, operator, modality, lineid, str(directions[direction]), datum, offset)
                                    eventvalidation, viewstate = fetchevent(content)
                                    cached = content

                            prevoffset = offset
                            lasttripid, offset, last, result = parsetimetable(cached, lasttripid, offset, last)
                            tmp2([lasttripid, offset, last, result], operator, modality, lineid, str(directions[direction]), datum, prevoffset)
                        else:
                            prevoffset = offset
                            lasttripid, offset, last, result = cached
                            if prevoffset == offset:
                                offset = None
                            #print offset
                        
                        if len(result) > 0:
                            calendar[datetime.datetime.strptime(datum, '%Y%m%d').weekday()] = True
                            for (tripid,v) in result.items():
                                tripids.add(tripid)

                                for trip in v:
                                    if trip[2] in ['Melanchtonweg IP', 'Tussenwater Ca']: # Zijn beide technische stops, geen echte data, skippen dus
                                        continue

                                    if not linenumber.isdigit():
                                        needle = linenumber+'_'+trip[2]
                                    else:
                                        needle = linenumber+'_'+str(directions[direction])+'_'+trip[2]

                                    if needle in stoplookup:
                                        stopid = stoplookup[needle]
                                    else:
                                        try:
                                            print 'Fuzzy...(%s) %s'%(needle, trip[2])
                                            stopid = fuzzylookup[trip[2]]
                                        except:
                                            stopid = 'not_found'
                                            print 'NOT FOUND: '+linenumber+'_'+trip[2]

                                    stop_times(str(tripid), str(trip[0]), str(trip[0]), stopid, str(trip[1]), '', aankomstvertrek_topickup(trip[3]), '0', '')
                   
                        if offset is None:
                            offset = '0'
                            last = None
                            break;

                        # helemaal geen tijden => volgende dag
                        # lege kolom => volgende dag
                        # anders: laagste tijd in de vierde kolom in uren = timeoffset
                    for tripid in tripids:
                        trips(lineid, calendarmagic(calendar, start_date, end_date), str(tripid), '', '', str(directions[direction]), '', '')


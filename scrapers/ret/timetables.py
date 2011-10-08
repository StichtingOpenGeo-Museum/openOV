from BeautifulSoup import BeautifulSoup
import re
from operator import itemgetter, attrgetter
from gtfstime import GTFSTime

def parsetimetable(content, tripid, lastoffset, last):
    soup = BeautifulSoup(content.split('|')[3])
    #print soup.findAll(id=re.compile('plhmiddle_0_plhcontent_0_ddlDate'))[0]
    #print soup.findAll(id=re.compile('plhmiddle_0_plhcontent_0_ddlTimeOffset'))[0]

    timetable = soup.find('table')
    result = {}
    offset = None

    if timetable is not None:
        timetable = timetable.findAll('tr')
        if len(timetable) > 1:
            lasttime = last
            xlen = len(timetable[1].findAll('td'))
            for y in range(1, len(timetable)):
                tds = timetable[y].findAll('td')
                for x in range(2, xlen):
                    if tds[x].text != '':
                        if tripid+(x-2) not in result:
                            result[tripid+(x-2)] = []
                        thistime = GTFSTime(tds[x].text)

                        # Als een tijd van 23 > 0 gaat, moet dat eerst worden afgevangen...
                        if lasttime is not None and lasttime.hour > 22 and thistime.hour >= 0 and thistime.hour < 5:
                            thistime.hour += 24

                        result[tripid+(x-2)].append([thistime, y, tds[0].text, (tds[1].text == 'A')])
                        lasttime = thistime
            tripid += (xlen-2)

            # Nu moeten alle waarden uit de staat, die niet oplopend continue zijn aangevuld worden
            # zodat ze altijd oplopen. Wanneer gebeurd dit? Bij cirkel lijnen, die op het midden beginnen.

            again = (len(result) == 6)

            for key in result.keys():
                result[key] = sorted(result[key])
                if last is not None and result[key][0][0] <= last:
                    del result[key]
            
            if len(result) > 0:
                for (k,x) in result.items():
#                    if x[0][1] != 1:
                    last = x[0][1]
                    for y in range(1, len(x)):
                        if x[y][1] <= x[y-1][1]:
                            x[y][1] = x[y-1][1]+1

                    if last != 1:
                        last -= 1
                        for y in range(0, len(x)):
                            x[y][1] -= last

                last = result[max(result.keys())][0][0]

                if again:
                    if int(last.minute) > 30:
                        minutes = '30'
                    else:
                        minutes = '00';
                    
                    if last.hour < 24:
                        offset = str(last.hour)+minutes
                        if lastoffset == offset:
                            if minutes == '00':
                                offset = str(last.hour)+'30'
                            elif minutes == '30' and last.hour < 23:
                                offset = str(last.hour+1)+'00'
                            else:
                                offset = None

            else:
                last = last
     
    return [tripid, offset, last, result]

def main():
    import sys
    tripid, offset, last, table = parsetimetable(open(sys.argv[1]).read(), 0, '2330', GTFSTime('0:00'))
    print tripid
    print offset
    print last
    for x in table.values():
        print x

if __name__ == "__main__":
    main()

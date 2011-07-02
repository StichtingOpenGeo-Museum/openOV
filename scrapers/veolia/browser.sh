#!/bin/sh

mkdir -p tmp
cd tmp

curl -A "Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/532.5 (KHTML, like Gecko) Chrome/4.0.248.0 Safari/532.5" -c cookies.jar -o main -c cookies.jar http://timetables.vtnl.net/
BLA=`grep __VIEWSTATE main | sed "s/.*name=\"\(__.*\)\" .* value=\"\(.*\)\" .*/\2/g"`
BLA2=`grep __EVENTVALIDATION main | sed "s/.*name=\"\(__.*\)\" .* value=\"\(.*\)\" .*/\2/g"`
value=`perl -MURI::Escape -e "print uri_escape('$BLA');"`
value2=`perl -MURI::Escape -e "print uri_escape('$BLA2');"`

grep "option value" main | sed "s/.*value=\"\([0-9]\+\)\".*/\1/g" | while read NUM; do
	echo "ctl00%24Scriptmanager1=ctl00%24plhMain%24updPanel1%7Cctl00%24plhMain%24searchPanel%24ddlArea&__EVENTTARGET=ctl00%24plhMain%24searchPanel%24ddlArea&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE=$value&__EVENTVALIDATION=$value2&ctl00%24plhMain%24searchPanel%24ddlArea=$NUM&__ASYNCPOST=true" > topost
	curl -o area-$NUM -A "Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/532.5 (KHTML, like Gecko) Chrome/4.0.248.0 Safari/532.5" -c cookies.jar -e http://timetables.vtnl.net -H "Expect:" -H "Origin: http://timetables.vtnl.net" -H "X-MicrosoftAjax: Delta=true" -d @topost http://timetables.vtnl.net/default.aspx

	grep -e "option.*value" area-$NUM | grep "value=\"\([0-9]\{6\}\)\"" | sed "s/.*value=\"\([0-9]\{6\}\)\".*/\1/g" | while read TOWN; do
		if [ -f town-$NUM-$TOWN ]; then
			echo "Already got town-$NUM-$TOWN";
		else
			BLA=`grep __VIEWSTATE area-$NUM | sed "s/.*VIEWSTATE|\(.*\)/\1/g;s/|.*//g"`
			BLA2=`grep __EVENTVALIDATION area-$NUM | sed "s/.*EVENTVALIDATION|\(.*\)/\1/g;s/|.*//g"`
			
			value=`echo -n "use URI::Escape; print uri_escape('$BLA');" > exe.pl; perl exe.pl`
			value2=`perl -MURI::Escape -e "print uri_escape('$BLA2');"`
			echo "ctl00%24Scriptmanager1=ctl00%24plhMain%24updPanel1%7Cctl00%24plhMain%24searchPanel%24ddlTowns&ctl00%24plhMain%24searchPanel%24ddlArea=$NUM&ctl00%24plhMain%24searchPanel%24ddlTowns=$TOWN&__EVENTTARGET=ctl00%24plhMain%24searchPanel%24ddlTowns&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE=$value&__EVENTVALIDATION=$value2&__ASYNCPOST=true" > topost
			curl -o town-$NUM-$TOWN -A "Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/532.5 (KHTML, like Gecko) Chrome/4.0.248.0 Safari/532.5" -c cookies.jar -e http://timetables.vtnl.net -H "Expect:" -H "Origin: http://timetables.vtnl.net" -H "X-MicrosoftAjax: Delta=true" -d @topost http://timetables.vtnl.net/default.aspx
			sleep 1
		fi
	grep "Lijn " town-$NUM-$TOWN | sed "s/.*value=\"\(.*\)\">.*/\1/g" | while read LINE; do

		if [ -f "line-$LINE" ]; then
			echo "Already got line-$LINE";
		else
		BLA=`grep __VIEWSTATE town-$NUM-$TOWN | sed "s/.*VIEWSTATE|\(.*\)/\1/g;s/|.*//g"`
		BLA2=`grep __EVENTVALIDATION town-$NUM-$TOWN | sed "s/.*EVENTVALIDATION|\(.*\)/\1/g;s/|.*//g"`
			
		value=`echo -n "use URI::Escape; print uri_escape('$BLA');" > exe.pl; perl exe.pl`
		value2=`perl -MURI::Escape -e "print uri_escape('$BLA2');"`
		line=`perl -MURI::Escape -e "print uri_escape('$LINE');"`
		echo "ctl00%24Scriptmanager1=ctl00%24plhMain%24updPanel1%7Cctl00%24plhMain%24searchPanel%24ddlLines&ctl00%24plhMain%24searchPanel%24ddlArea=$NUM&ctl00%24plhMain%24searchPanel%24ddlTowns=$TOWN&ctl00%24plhMain%24searchPanel%24ddlLines=$line&__EVENTTARGET=ctl00%24plhMain%24searchPanel%24ddlLiness&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE=$value&__EVENTVALIDATION=$value2&__ASYNCPOST=true" > topost
		curl -o "line-$LINE" -A "Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/532.5 (KHTML, like Gecko) Chrome/4.0.248.0 Safari/532.5" -c cookies.jar -e http://timetables.vtnl.net -H "Expect:" -H "Origin: http://timetables.vtnl.net" -H "X-MicrosoftAjax: Delta=true" -d @topost http://timetables.vtnl.net/default.aspx

		POINT=`grep -A 1 "id=\"ctl00_plhMain_searchPanel_ddlPoints\"" "line-$LINE" | tail -n 1 | sed "s/.*value=\"\(.*\)\".*/\1/g"`

		BLA=`grep __VIEWSTATE "line-$LINE" | sed "s/.*VIEWSTATE|\(.*\)/\1/g;s/|.*//g"`
		BLA2=`grep __EVENTVALIDATION "line-$LINE" | sed "s/.*EVENTVALIDATION|\(.*\)/\1/g;s/|.*//g"`
			
		value=`echo -n "use URI::Escape; print uri_escape('$BLA');" > exe.pl; perl exe.pl`
		value2=`perl -MURI::Escape -e "print uri_escape('$BLA2');"`

		echo "ctl00%24Scriptmanager1=ctl00%24plhMain%24updPanel1%7Cctl00%24plhMain%24searchPanel%24btnShowTimes&ctl00%24plhMain%24searchPanel%24ddlArea=$NUM&ctl00%24plhMain%24searchPanel%24ddlTowns=$TOWN&ctl00%24plhMain%24searchPanel%24ddlLines=$line&ctl00%24plhMain%24searchPanel%24ddlPoints=$POINT&__EVENTTARGET=&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE=$value&__EVENTVALIDATION=$value2&__ASYNCPOST=true&ctl00%24plhMain%24searchPanel%24btnShowTimes=Toon%20vertrektijden" > topost
		curl -o "line-$LINE-vertrek" -A "Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/532.5 (KHTML, like Gecko) Chrome/4.0.248.0 Safari/532.5" -c cookies.jar -e http://timetables.vtnl.net -H "Expect:" -H "Origin: http://timetables.vtnl.net" -H "X-MicrosoftAjax: Delta=true" -d @topost http://timetables.vtnl.net/default.aspx

		QUERY=`grep TimeTable.aspx "line-$LINE-vertrek" | sed "s/.*TimeTable.aspx?q=\(.*\).*TimetableWindow.*/\1/g;s/=.*/=/g"`

		echo "http://timetables.vtnl.net/TimeTable.aspx?q=$QUERY"

		curl -o "line-$LINE-timetable" -A "Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/532.5 (KHTML, like Gecko) Chrome/4.0.248.0 Safari/532.5" -c cookies.jar -e http://timetables.vtnl.net -H "Expect:" -H "Origin: http://timetables.vtnl.net" "http://timetables.vtnl.net/TimeTable.aspx?q=$QUERY"

		BLA=`grep __VIEWSTATE "line-$LINE-timetable" | sed "s/.*name=\"\(__.*\)\" .* value=\"\(.*\)\" .*/\2/g"`
		BLA2=`grep __EVENTVALIDATION "line-$LINE-timetable" | sed "s/.*name=\"\(__.*\)\" .* value=\"\(.*\)\" .*/\2/g"`
		value=`echo -n "use URI::Escape; print uri_escape('$BLA');" > exe.pl; perl exe.pl`
		value2=`perl -MURI::Escape -e "print uri_escape('$BLA2');"`

		echo "__EVENTTARGET=ctl00%24plhMain%24bttnMap&__EVENTARGUMENT=&__VIEWSTATE=$value&__EVENTVALIDATION=$value2" > topost
		curl -o "line-$LINE-map" -A "Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/532.5 (KHTML, like Gecko) Chrome/4.0.248.0 Safari/532.5" -c cookies.jar -e "http://timetables.vtnl.net/TimeTable.aspx?q=$QUERY" -H "Expect:" -d @topost "http://timetables.vtnl.net/TimeTable.aspx?q=$QUERY"

		grep -A 1 "new GMarker" "line-$LINE-map" | grep point | sed "s/.*GLatLng(//g;s/.*<b>Halte : //g;s/), markerOptions.*/,/g;s/<\/b>.*/;/g" | tr "\n" " " | tr ";" "\n" > "line-$LINE-coords"
		fi
	done
	done
done

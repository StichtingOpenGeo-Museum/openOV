#!/bin/sh

mkdir -p tmp
cd tmp

# Thanks to the wonderful implementation of CouchDB that doesn't allow replication we just implement a Conexxion alike give me all you got.
for x in `seq 166 171`; do
	for y in `seq 105 109`; do
		wget -O "arriva-stops-$x-$y.js" "http://www.arriva.nl/couchdb-proxy.php?/topology/_design/stops/_view/clusterZ14?startkey=[$((${x} * 100 + 1)),$((${y} * 100 + 1))]&endkey=[$((($x + 1) * 100)),$((($y + 1) * 100))]"
		sleep 1
	done
done

#wget -O tmp/id-stop.html http://www.arriva.nl/nc/reisinformatie/vertrektijden-zoeken/actuele-vertrektijden/detailpagina/?tx_bwrealtime_pi1[stop]=74670020

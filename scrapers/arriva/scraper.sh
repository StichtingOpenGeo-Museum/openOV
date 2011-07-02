#!/bin/sh

mkdir -p tmp
cd tmp

# Thanks to the wonderful implementation of CouchDB that doesn't allow replication we just implement a Conexxion alike give me all you got.
wget -O arriva-stops.js "http://www.arriva.nl/couchdb-proxy.php?/topology/_design/stops/_view/clusterZ14?startkey=[1,1]&endkey=[20000,20000]"

wget -O tmp/id-stop.html "http://www.arriva.nl/nc/reisinformatie/actuele-vertrektijden/detailpagina/?tx_bwrealtime_pi1%5Bstop%5D=74670020"

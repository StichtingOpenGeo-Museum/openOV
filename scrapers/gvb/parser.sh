ls -1 tmp/* | while read i; do
	LIJN=`echo "$i" | sed 's/.*\/\([0-9]\+\)\+-\([0-1]\)/\1\t\2/g'`
	grep area "$i" | sed "s/.*Halte: \(.*\). Rolstoel toegankelijk: \(ja\|nee\).*/\1\t\2/g;s/\tja/\tTRUE/g;s/\tnee/\tFALSE/g" | nl -n ln | sed "s/\(.*\)/$LIJN\t\1/g"
done 

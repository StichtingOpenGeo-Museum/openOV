if [ -e "SelectLijn.aspx" ]; then
	echo "Hebben we al"
else
	wget -O SelectLijn.aspx http://195.193.209.12/gvbpublicatieinternet/SelectLijn.aspx
fi

#grep SelectRichting SelectLijn.aspx | sed 's/.*href="\(.*\)".*/\1/g' | sed 's/.*lijnnummer=\([0-9]\+\).*/\1/g' | sort -u -n

mkdir -p tmp
cd tmp

grep SelectRichting ../SelectLijn.aspx | sed 's/.*?\(.*\)".*/\1/g' | sort -u | while read i; do
	LIJN=`echo $i | sed 's/.*lijnnummer=\([0-9]\+\).*/\1/g'`
	DAG='WE'

	if [ -e "$LIJN-0" ]; then
		echo "Hebben we al"
	else
		wget -O "$LIJN-0" "http://195.193.209.12/gvbpublicatieinternet/TimeTable.aspx?$i&dagsoort=$DAG&richting=H"
	fi

	if [ -e "$LIJN-1" ]; then
		echo "Hebben we al"	
	else
		wget -O "$LIJN-1" "http://195.193.209.12/gvbpublicatieinternet/TimeTable.aspx?$i&dagsoort=$DAG&richting=T"
	fi
done

grep -L area * | while read i; do rm $i; done

grep SelectRichting ../SelectLijn.aspx | sed 's/.*?\(.*\)".*/\1/g' | sort -u | while read i; do
	LIJN=`echo $i | sed 's/.*lijnnummer=\([0-9]\+\).*/\1/g'`
	DAG='MA'

	if [ -e "$LIJN-0" ]; then
		echo "Hebben we al"
	else
		wget -O "$LIJN-0" "http://195.193.209.12/gvbpublicatieinternet/TimeTable.aspx?$i&dagsoort=$DAG&richting=H"
	fi

	if [ -e "$LIJN-1" ]; then
		echo "Hebben we al"	
	else
		wget -O "$LIJN-1" "http://195.193.209.12/gvbpublicatieinternet/TimeTable.aspx?$i&dagsoort=$DAG&richting=T"
	fi
done

grep -L area * | while read i; do rm $i; done

grep SelectRichting ../SelectLijn.aspx | sed 's/.*?\(.*\)".*/\1/g' | sort -u | while read i; do
	LIJN=`echo $i | sed 's/.*lijnnummer=\([0-9]\+\).*/\1/g'`
	DAG='ZA'

	if [ -e "$LIJN-0" ]; then
		echo "Hebben we al"
	else
		wget -O "$LIJN-0" "http://195.193.209.12/gvbpublicatieinternet/TimeTable.aspx?$i&dagsoort=$DAG&richting=H"
	fi

	if [ -e "$LIJN-1" ]; then
		echo "Hebben we al"	
	else
		wget -O "$LIJN-1" "http://195.193.209.12/gvbpublicatieinternet/TimeTable.aspx?$i&dagsoort=$DAG&richting=T"
	fi
done


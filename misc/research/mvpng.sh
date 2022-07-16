#!/bin/sh
for y in `seq 001 386`; do
	x=`ls $y* | wc -l`
	if  [ "$x" -eq "2" ]; then 
		echo "true for $y"; 
		`mv $y* PNG/`
	fi
done
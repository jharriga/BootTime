#!/bin/bash
# reads '.log' files created by initramfsResults.sh
# echos to stdout the values in single column form for
# easier pasting into spreadsheet

cnt=1
for logfile in ./*.log; do
	echo
	echo "BEGIN---------------------------------"
	echo "LOGFILE #${cnt}: $logfile"
	cat $logfile | awk -F ":" '{gsub(/ /,""); print $2}'
	echo "DONE---------------------------------"
	cnt=$((cnt + 1))
done

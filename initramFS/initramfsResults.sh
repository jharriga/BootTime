#!/bin/bash

# dmesg | grep -m 1 {} | cut -d '[' -f2 | cut -d ']' -f1

########################################################
echo "INITRAMFS Timings"
unpack=$(dmesg | grep -m1 "unpack rootfs image" | cut -d '[' -f2 | cut -d ']' -f1)
echo "> BEGIN unpack: $unpack"

init=$(dmesg | grep -m1 "as init process" | cut -d '[' -f2 | cut -d ']' -f1)
echo "> Run /init: $init"

# interval: unpack to /init
##interval1=$(bc <<< "scale=4;$init-$unpack")
interval1=$(bc <<< "$init-$unpack")
echo ">> INTERVAL, unpack to /init: $interval1" 

systemd=$(dmesg | grep -m1 "running in system mode" | cut -d '[' -f2 | cut -d ']' -f1)
echo "> Systemd running: $systemd"
interval2=$(bc <<< "$systemd-$init")
echo ">> INTERVAL, /init to systemd: $interval2" 

earlysvc=$(dmesg | grep -m1 "early service example" | cut -d '[' -f2 | cut -d ']' -f1)
if [ -z "$earlysvc" ]; then
    echo "> Early service example: MARKER NOT FOUND"
    echo ">> INTERVAL, systemd to earlySvc: NA" 
else
    echo "> Early service example: $earlysvc"
    interval3=$(bc <<< "$earlysvc-$systemd")
    echo ">> INTERVAL, systemd to earlySvc: $interval3" 
fi

########################################################
echo; echo "DLKM Timings"
echo "> Systemd running: $systemd"          # re-use from above

udevcontrol=$(dmesg | grep -m1 "udev Control Socket" | cut -d '[' -f2 | cut -d ']' -f1)
echo "> udev Control Socket: $udevcontrol"
interval4=$(bc <<< "$udevcontrol-$systemd")
echo ">> INTERVAL, systemd to udevControlSocket: $interval4" 

startld=$(dmesg | grep -m1 "Starting Load Kernel" | cut -d '[' -f2 | cut -d ']' -f1)
echo "> Start Load: $startld"
interval5=$(bc <<< "$startld-$udevcontrol")
echo ">> INTERVAL, udevControlSocket to startLoad: $interval5" 

finishld=$(dmesg | grep -m1 "Finished Load Kernel" | cut -d '[' -f2 | cut -d ']' -f1)
echo "> Finished Load: $finishld"
interval6=$(bc <<< "$finishld-$startld")
echo ">> INTERVAL, startLoad to finishLoad: $interval6" 
echo

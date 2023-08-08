#!/bin/bash
# Parses through kernel msg buffer looking for boot related timings
# dmesg | grep -m 1 {} | cut -d '[' -f2 | cut -d ']' -f1
# Checks for empty values before calculating intervals
####################################################################

#
# For clock_tick section, all values must be converted to seconds
echo "clock_tick Timings"
# [    0.000031] mark: primary_entry(): 84051058
# Purpose of 'xargs' is to remove whitespace
primary_ts=$(dmesg | grep -m1 "mark: primary_entry" | \
	cut -d ':' -f3 | xargs)
primary_sec=$(echo "scale=3; $primary_ts / 19200000" | bc -l)
echo "> TIMESTAMP primary_entry: $primary_sec"

# [	0.000043] mark: time_init(): 97888608 (11904)
timeinit_ts=$(dmesg | grep -m1 "mark: setup_arch" | \
	cut -d ':' -f3 | cut -d ' ' -f2 | cut -d ' ' -f1)
timeinit_sec=$(echo "scale=3; $timeinit_ts / 19200000" | bc -l)
echo "> TIMESTAMP time_init: $timeinit_sec"

# [	0.000034] mark: setup_arch(): 95023454 (10981089)
setup_ts=$(dmesg | grep -m1 "mark: setup_arch" | \
	cut -d ':' -f3 | cut -d ' ' -f2 | cut -d ' ' -f1)
setup_run=$(dmesg | grep -m1 "mark: setup_arch" | \
	cut -d ':' -f3 | cut -d '(' -f2 | cut -d ')' -f1)
setup_sec=$(echo "scale=3; $setup_run / 19200000" | bc -l)
echo "> RUNTIME setup_arch: $setup_sec"

# Calculate interval from primary_init() to time_init()
if [ -z "$primary_ts" ] || [ -z "$timeinit_ts" ]; then
    interval0="N/A"
else
    interval0=$(bc <<< "$timeinit_ts - $primary_ts")
    int0_sec=$(echo "scale=3; $interval0 / 19200000" | bc -l)
fi
echo ">> INTERVAL, primary_entry to time_init: $int0_sec" 

####################################################################
echo; echo "INITRAMFS Timings"
unpack=$(dmesg | grep -m1 "unpack rootfs image" | \
	cut -d '[' -f2 | cut -d ']' -f1)
echo "> BEGIN unpack: $unpack"

init=$(dmesg | grep -m1 "as init process" | cut -d '[' -f2 | cut -d ']' -f1)
echo "> Run /init: $init"

# interval: unpack to /init
if [ -z "$init" ] || [ -z "$unpack" ]; then
    interval1="N/A"
else
    interval1=$(bc <<< "$init-$unpack")
fi
echo ">> INTERVAL, unpack to /init: $interval1" 

systemd=$(dmesg | grep -m1 "running in system mode" | \
	cut -d '[' -f2 | cut -d ']' -f1)
echo "> Systemd running: $systemd"
if [ -z "$init" ] || [ -z "$systemd" ]; then
    interval2="N/A"
else
    interval2=$(bc <<< "$systemd-$init")
fi
echo ">> INTERVAL, /init to systemd: $interval2" 

earlysvc=$(dmesg | grep -m1 "early service example" | \
	cut -d '[' -f2 | cut -d ']' -f1)
if [ -z "$earlysvc" ]; then
    earlysvc="N/A"
    interval3="N/A"
else
    interval3=$(bc <<< "$earlysvc-$systemd")
fi
echo "> Early service example: $earlysvc"
echo ">> INTERVAL, systemd to earlySvc: $interval3" 

########################################################
echo; echo "DLKM Timings"
echo "> Systemd running: $systemd"          # re-use from above

udevcontrol=$(dmesg | grep -m1 "udev Control Socket" | \
	cut -d '[' -f2 | cut -d ']' -f1)
echo "> udev Control Socket: $udevcontrol"
if [ -z "$udevcontrol" ] || [ -z "$systemd" ]; then
    interval4="N/A"
else
    interval4=$(bc <<< "$udevcontrol-$systemd")
fi
echo ">> INTERVAL, systemd to udevControlSocket: $interval4" 

startld=$(dmesg | grep -m1 "Starting Load Kernel" | \
	cut -d '[' -f2 | cut -d ']' -f1)
echo "> Start Load: $startld"
if [ -z "$udevcontrol" ] || [ -z "$startld" ]; then
    interval5="N/A"
else
    interval5=$(bc <<< "$startld-$udevcontrol")
fi
echo ">> INTERVAL, udevControlSocket to startLoad: $interval5" 

finishld=$(dmesg | grep -m1 "Finished Load Kernel" | \
	cut -d '[' -f2 | cut -d ']' -f1)
echo "> Finished Load: $finishld"
if [ -z "$finishld" ] || [ -z "$startld" ]; then
    interval6="N/A"
else
    interval6=$(bc <<< "$finishld-$startld")
fi
echo ">> INTERVAL, startLoad to finishLoad: $interval6" 
echo

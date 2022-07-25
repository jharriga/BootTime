#!/bin/bash
# Must be run as ROOT on the VM
# Parses myapp timestamps and calculates 'myapp' startup service timings
# DEPENDENCIES: grep, awk, echo, xargs
#
#----------------------------
# EXAMPLE OUTPUT to be parsed
#    dmesg | grep -m 1 myapp | awk -F '[][]' '{print $2}'
#      22.207397
#    dmesg | grep -m 1 myapp | awk -F '-' '{print $2}'
#      1657913795.963792736

# Edit this as needed
HOSTNAME="192.168.122.212"

# Start networking, if not already running
# if test fails then run 'dhclient' else skip it
if [ ! -f /var/run/dhclient.pid ]
then
    echo "Starting networking back to host"
    dhclient
fi

echo "-------"

# Reads start timestamp, provided by 'start_vm.sh'
#start_time=1658172189.432348545
start_val=$(ssh -l devel $HOSTNAME "cat /tmp/vm_start_time")
# remove whitespace
start_time=$(echo $start_val | xargs echo -n)
echo "start_time: $start_time"        # DEBUG

# 
# Get boot stats 
# Example dmesg output:  [   27.227386] myapp - 1657809636.457031712
end_val=$(dmesg | grep -m 1 myapp | awk -F '-' '{print $2}')
end_time=$(echo $end_val | xargs echo -n)
echo "end_time: $end_time"           # DEBUG

dmesg_val=$(dmesg | grep -m 1 myapp | awk -F '[][]' '{print $2}')
dmesg_time=$(echo $dmesg_val | xargs echo -n)
echo "dmesg_time: $dmesg_time"        # DEBUG

echo "-------"
# Report boot-time stats
#total=$(echo $end_time - $start_time | bc -l)
total=$(awk -v a=$end_time -v b=$start_time 'BEGIN{ans=a-b; print ans}')
echo "TOTAL (power on to myapp) boot-time: $total"

#pre_kernel=$(echo $total - $dmesg_time | bc -l)
pre_kernel=$(awk -v a=$total -v b=$dmesg_time 'BEGIN{ans=a-b; print ans}')
echo "PreKernel boot-time: $pre_kernel"

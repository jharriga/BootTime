#!/bin/bash
# Logs timestamp prior to starting VM

# Do any pre-VM start work here

# Records timestamp to temp file
TS=$(date +%s.%N)
echo -n "$TS" > /tmp/vm_start_time

# Start the VM
echo "< Insert VM start cmdline HERE >"

# VM has been powered off. Report start time and clean-up
echo "start time: $TS"
rm /tmp/vm_start_time

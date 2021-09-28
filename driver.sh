#!/bin/bash

# list of hosts
declare -a hostips=('192.168.0.111' '192.168.0.109' '192.168.0.102')
declare -a hostnames=('rpi4' 'auto-02' 'johnagx') 

numhosts=${#hostips[@]}

# Test for ping access
for (( i=0; i<${numhosts}; i++ )); do
    ipaddr="${hostips[$i]}"
    hostnm="${hostnames[$i]}"
    retVal=$(ping -c 3 "${ipaddr}" > /dev/null 2>&1)
    if [[ "$?" -ne 0 ]]; then
        echo "failed to ping ${hostnm} : ${ipaddr}, exiting"
        exit
    else
        echo "SUCCESS pinging ${hostnm} : ${ipaddr}, continuing"
    fi
done

# now perform the systemd-analyze cmds


echo "Finished"

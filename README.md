# BootTime
Collection of scripts useful to investigate linux boot-time

sut_boottest.py : performs boot test runs (sut_boottestREADME.pdf: documents automation flow)
* Reboots remote systems (SUTs) and captures boot timing results
* Writes JSON file in format ready for ingest in ElasticSearch, see 'example.json'
* See sample output: sut_boottest.OUTPUT
* USAGE: # ./sut_boottest.py -s 2 hostname 10.19.243.222 root password

calcstats_json.py : post processes sut_boottest.py produced JSON file
* calculates mean and run-to-run variance stats for markers across multiple runs
* See sample output: calc_stats.OUTPUT
* USAGE: # ./calc_stats.py hostname.json

systemd_unitfile/
Assists with measurement of custom systemd-unitfile timings
* see README.md in directory

Sandbox/
Collection of scripts created during development of Boot-time automation
* reboot_test.py: instruments reboot of remote system under test
* ex_channel.py: paramiko ssh example
* rcv_exit_status.py: illustrates blocking with paramiko exec cmds
* sa_json.py : produces json from both 'time' and 'blame' results
NOTE: requires 'pip3.6 import distro'

VMs/
Two scripts which work together to report on boot-time stats for a VM
* start_vm_boot.sh: execute on HOST. You need to add cmdline to start your VM
* print_boottime.sh: execute in VM, edit $HOSTNAME. Prints boot-time metrics (see sample.txt)
* sample.txt: example of output from 'print_boottime.sh'

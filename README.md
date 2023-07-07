# BootTime
Collection of scripts useful to investigate linux boot-time

sut_boottest.py : latest JSON prototype (sut_boottestREADME.pdf: documents automation flow)
* Reboots remote systems (SUTs) and captures boot timing results
* Writes JSON file in format ready for ingest in ElasticSearch
* See sample output: sut_boottest.OUTPUT

calc_satimes.py : post processes sut_boottest.py JSON file
* calculates run-to-run variance stats for systemd-analyze by parsing 'sa_time' JSON object

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

# BootTime
Collection of scripts useful to investigate linux boot-time
* sut_boottest.py : latest JSON prototype (sample output: sut_boottest.OUTPUT)
* > Reboots remote systems (SUTs) and captures boot timing results
* > Writes JSON file in format ready for ingest in ElasticSearch
* > See sample output: single.json and multiple.json
* testrun.py: older text-based prototype for reboot testing (sample output: testrun.OUTPUT)

Sandbox/
Collection of scripts created during development of Boot-time automation
* reboot_test.py: instruments reboot of remote system under test
* ex_channel.py: paramiko ssh example
* rcv_exit_status.py: illustrates blocking with paramiko exec cmds
* sa_json.py : produces json from both 'time' and 'blame' results
NOTE: requires 'pip3.6 import distro'

VMs/
Two scripts which work together to report on boot-time stats for a VM
* 

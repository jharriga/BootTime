# BootTime
Collection of scripts useful to investigate linux boot-time
* sut_boottest.py : latest JSON prototype (sample output: sut_boottest.OUTPUT)
* > Reboots remote systems (SUTs) and captures boot timing results
* > Writes JSON file in format ready for ingest in ElasticSearch
* testrun.py: older text-based prototype for reboot testing (sample output: testrun.OUTPUT)

Utils/
* reboot_test.py: instruments reboot of remote system under test
* ex_channel.py: paramiko ssh example
* rcv_exit_status.py: illustrates blocking with paramiko exec cmds

JSON/
* sa_both.py : produces json from both 'time' and 'blame' results
* sa_time.py : produces data.json from 'systemd-analyze time'
* sa_blame : produces data.json from 'systemd-analyze blame'
NOTE: requires 'pip3.6 import distro'

## Sample output

    [root@rpi4 SchemaES]# python3.6 sa_time.py
    [root@rpi4 SchemaES]# cat data.json
    {
        "date": "2021-09-22T16:05:44.621685Z",
        "test_config": {
            "cpumodel": "Cortex-A72",
            "kversion": "5.4.60-v8.1.el8",
            "maxMHz": "1500.0000",
            "numcores": "4",
            "systemtgt": "multi-user.target"
        },
        "test_data": {
            "initrd": "NULL",
            "kernel": "1.983",
            "userspace": "29.270"
        }
    }



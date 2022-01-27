# BootTime
Collection of scripts useful to investigate linux boot-time
* sut_boottest.py : latest JSON prototype (sample output: SUT_BOOTTEST.log)
* > Reboots remote systems (SUTs) and captures boot timing results
* > Writes JSON file in format ready for ingest in ElasticSearch
* testrun.py: older text-based prototype for reboot testing (sample output: TESTRUN.log)

Utils/
* reboot_test.py: instruments reboot of remote system under test
* ex_channel.py: paramiko ssh example
* rcv_exit_status.py: illustrates blocking with paramiko exec cmds

## Sample output

    [root@acer BootCode]# python3 reboot_test.py 
    testssh: verifying SSH to 192.168.0.111. Timeout: 300s
    testssh: Connected to 192.168.0.111. SSH elapsed time = 0s
    SUT rebooted at: 2021-12-17 16:26:44.073650
    testssh: verifying SSH to 192.168.0.111. Timeout: 300s
    [Errno None] Unable to connect to port 22 on 192.168.0.111timed outtimed outtimed outtimed outtimed outtimed outtimed outtestssh:   Connected to 192.168.0.111. SSH elapsed time = 8s
    rebootsut: SUT 192.168.0.111, waiting for reboot to complete...
    SUT 192.168.0.111 reboot elapsed time: 0:01:35.722243
    * sleep calculated interval times:
      > SSH elapsed time 8s
      > SYSTEMCTL elapsed time 54s
      > TOTAL elapsed time 62s

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



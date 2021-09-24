# BootTime
Collection of scripts useful to investigate linux boot-time 

* sa_time.py : produces data.json from 'systemd-analyze time'
* sa_blame : produces data.json from 'systemd-analyze blame'


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



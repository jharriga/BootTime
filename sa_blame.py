# SA_BLAME.py                EDITS: Sept 22
# test script to produce bmark-wrapper json input
# Executes and parses 'systemd-analyze blame' cmd
# USAGE: python3.6 sa_blame.py

import datetime
import subprocess
import re
import platform
import json
import io
to_unicode = str

# Test configuration lists
tc_list = ["kversion", "cpumodel", "numcores", "maxMHz", "systemtgt"]
tc_values = []
# Test data lists
td_list = []
td_values = []

# Current date timestamp
curtime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

##########################
# Get test_config values
#
# kernel version
#kversion_out = platform.release()
kversion_out = subprocess.run(['uname', '-r'], stdout=subprocess.PIPE)
kversion_out = kversion_out.stdout.decode('utf-8')
tc_values.insert(0, kversion_out.strip())

# cpu test config values
##cpuinfo_out = subprocess.run(['cat', '/proc/cpuinfo'], stdout=subprocess.PIPE)
cpuinfo_out = subprocess.run(['lscpu'], stdout=subprocess.PIPE)
cpuinfo_out = cpuinfo_out.stdout.decode('utf-8')
# cpu model
for line in cpuinfo_out.split("\n"):
    if "Model name:" in line:
        model = re.search('Model name.*:(.*)', cpuinfo_out).group(1)
##        print(model.strip())          # DEBUG
# Check for value
if not model:
    tc_values.insert(1, 'NULL')
else:
    tc_values.insert(1, model.lstrip())

# number of cores
for line in cpuinfo_out.split("\n"):
    if "CPU(s):" in line:
        numcores = re.search('CPU\(s\):(.*)', cpuinfo_out).group(1)
##        print(numcores.strip())           # DEBUG
# Check for value
if not numcores:
    tc_values.insert(2, 'NULL')
else:
    tc_values.insert(2, numcores.strip())

# CPU max MHz
for line in cpuinfo_out.split("\n"):
    if "CPU max MHz:" in line:
        maxmhz = re.search('CPU max MHz:(.*)', cpuinfo_out).group(1)
##        print(maxmhz.strip())           # DEBUG
# Check for value
if not maxmhz:
    tc_values.insert(3, 'NULL')
else:
    tc_values.insert(3, maxmhz.strip())

# systemctl target
sysctl_out = subprocess.run(['systemctl', 'get-default'], stdout=subprocess.PIPE)
sysctl_out = sysctl_out.stdout.decode('utf-8')
# Check for value
if not sysctl_out:
    tc_values.insert(4, 'NULL')
else:
    tc_values.insert(4, sysctl_out.strip())

####################################
# define json struct for data points
data_point = {
        'date': curtime,
        'test_config': {
             tc_list[0]: tc_values[0],
             tc_list[1]: tc_values[1],
             tc_list[2]: tc_values[2],
             tc_list[3]: tc_values[3],
             tc_list[4]: tc_values[4]},
        'test_data': { }
        }

##########################
# Exec systemd-analyze cmd
sysd_out = subprocess.run(['systemd-analyze', 'blame'], stdout=subprocess.PIPE)
sysd_out = sysd_out.stdout.decode('utf-8')

# Parse cmd output and populate json dict
for line in sysd_out.split("\n"):
    words = re.split(r'\s', line)
    service = words[-1]
    minutes = re.search('(\d+)min', line)
    seconds = re.search('(\d+\.\d+)s', line)
    millisec = re.search('(\d+)ms', line)
    if (minutes and seconds):
        min = minutes[0].strip("min")
        sec = seconds[0].strip("s")
        etime = (int(min) * 60) + float(sec)
    elif (seconds and not minutes):
        etime = seconds[0].strip("s")
    elif millisec:
        ms = millisec[0].strip("ms")
        etime = (int(ms)/1000)%60

    if (service and etime):
        print(f'{service}: {etime}')            # DEBUG
        data_point['test_data'][service] = etime


# Write JSON file
with io.open('data.json', 'w', encoding='utf8') as outfile:
    str_ = json.dumps(data_point,
                      indent=4, sort_keys=False,
                      separators=(',', ': '), ensure_ascii=False)
    outfile.write(to_unicode(str_))
    outfile.write(to_unicode("\n"))

[root@acer JSON]# cat sa_Jan24.py 
# SA_BOTH.py
# test script to produce bmark-wrapper json input
# Executes then parses into dictionary:
#    'systemd-analyze time' & 'systemd-analyze blame'
# USAGE: python3 sa_both.py
# Writes out new file 'testrun.json'

import sys
import datetime
import subprocess
import re
import json
import io
import distro
to_unicode = str

# Dictionaries
testrun_dict = {}          # complete run results (final dict)
cfg_dict = {}              # test configuration
data_dict = {}             # test data/results (nested)
satime_dict = {}           # systemd-analyze time results
sablame_dict = {}          # systemd-analyze blame results
####################################
## Dictionary structure
# testrun_dict = {
#    ' date': curtime,
#     'test_config': {
#         cfg_dict{}
#     } 
#     'test_data': {
#         'satime':
#             satime_dict{}
#         'sablame':
#             sablame_dict{}
#     }
# }
##########################

# Test configuration
tc_list = ["kversion", "distro", "cpumodel", "numcores", "maxMHz", "systemtgt"]

# 'systemd-analyze time' key metrics and key names
satime_list = ["kernel", "initrd", "userspace"]

# Add current date timestamp to test_dict{}
curtime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
testrun_dict['curtime'] = str(curtime.strip())

##########################
# Get test_config values
#
# kernel version
kversion_out = subprocess.run(['uname', '-r'], stdout=subprocess.PIPE)
kversion_out = kversion_out.stdout.decode('utf-8')
cfg_dict['kernel'] = str(kversion_out.strip())

# Linux Distro
cfg_dict['distro'] = str(distro.name(pretty=True))

# cpu test config values
lscpu_out = subprocess.run(['lscpu'], stdout=subprocess.PIPE)
lscpu_out = lscpu_out.stdout.decode('utf-8')
# cpu model
for line in lscpu_out.split("\n"):
    if "Model name:" in line:
        model = re.search('Model name.*:(.*)', lscpu_out).group(1)
# Check for value
if not model:
    cfg_dict['model'] = str(" ")
else:
    cfg_dict['model'] = str(model.lstrip())

# number of cores
for line in lscpu_out.split("\n"):
    if "CPU(s):" in line:
        numcores = re.search('CPU\(s\):(.*)', lscpu_out).group(1)
# Check for value
if not numcores:
    cfg_dict['numcores'] = str(" ")
else:
    cfg_dict['numcores'] = str(numcores.lstrip())

# CPU max MHz
for line in lscpu_out.split("\n"):
    if "CPU max MHz:" in line:
        maxmhz = re.search('CPU max MHz:(.*)', lscpu_out).group(1)
# Check for value
if not maxmhz:
    cfg_dict['maxmhz'] = str(" ")
else:
    cfg_dict['maxmhz'] = str(maxmhz.lstrip())

# systemctl target
sysctl_out = subprocess.run(['systemctl', 'get-default'],
    stdout=subprocess.PIPE)
sysctl_out = sysctl_out.stdout.decode('utf-8')
# Check for value
if not sysctl_out:
    cfg_dict['target'] = str(" ")
else:
    cfg_dict['target'] = str(sysctl_out.lstrip())

# cfg_dict{} populated, insert it into testrun_dict{}
testrun_dict["test_config"] = cfg_dict

##########################
# Execute CMDS and populate per-command dictionaries:
#    satime_dict{} and sablame_dict{}
# insert into them into test_dict{}
# then insert that into results_dict{}  <-- final testrun summary
#
# 'systemd-analyze time' cmd
satime_out = subprocess.run(['systemd-analyze', 'time'],
    stdout=subprocess.PIPE)
satime_out = satime_out.stdout.decode('utf-8')

# Parse cmd output and populate json dict
for i, regex in enumerate(satime_list):
    result = re.findall('(\d+\.\d+)s\s\('+regex+'\)', satime_out)
    if not result:
        satime_dict[regex] = str("")
    else:
        satime_dict[regex] = str(result[0].lstrip())

# 'systemd-analyze blame' cmd
sablame_out = subprocess.run(['systemd-analyze', 'blame'],
    stdout=subprocess.PIPE)
sablame_out = sablame_out.stdout.decode('utf-8')

# Parse cmd output, calc time in seconds and populate dict
num_blames = 5 
cntr = 1
for line in sablame_out.split("\n"):
    if cntr <= num_blames:
        words = re.split(r'\s', line)
        service = words[-1]
        minutes = re.search('(\d+)min', line)
        seconds = re.search('(\d+\.\d+)s', line)
        millisec = re.search('(\d+)ms', line)
        if (minutes and seconds):
            min = minutes[0].strip("min")
            sec = seconds[0].strip("s")
            etime = str((int(min) * 60) + float(sec))
        elif (seconds and not minutes):
            etime = seconds[0].strip("s")
        elif millisec:
            ms = millisec[0].strip("ms")
            etime = str((int(ms)/1000)%60)

        if (service and etime):
            cntr += 1
            sablame_dict[service] = str(etime)
    else:
        break

# Insert test result dictionaries into data_dict{}
data_dict['sa_time'] = satime_dict
data_dict['sa_blame'] = sablame_dict

##print(satime_dict)      # DEBUG
##print(sablame_dict)     # DEBUG

# Insert data_dict{} into testrun_dict (final dictionary)
testrun_dict['test_data'] = data_dict
print("**TESTRUN DICT**")
print(testrun_dict)

# Write JSON file
with io.open('testrun.json', 'w', encoding='utf8') as outfile:
    str_ = json.dumps(testrun_dict,
                      indent=4, sort_keys=False,
                      separators=(',', ': '), ensure_ascii=False)
    outfile.write(to_unicode(str_))
    outfile.write(to_unicode("\n"))
    
print("Wrote file: testrun.json")


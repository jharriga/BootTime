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

##########################
# DICTIONARY STRUCTURE
#
# testrun_dict = {
#    ' date': curtime,
#     'test_config': {
#         testcfg_dict{}
#     } 
#     'test_results': {
#         'satime':
#             satime_dict{}
#         'sablame':
#             sablame_dict{}
#     }
#     'system_config': {
#         syscfg_dict{}
#     } 
# }


####################
# FUNCTIONS
#
def parse_lscpu(cmd_out, the_dict):
    # cpu model
    for line in cmd_out.split("\n"):
        if "Model name:" in line:
            model = re.search('Model name.*:(.*)', cmd_out).group(1)
    the_dict['model'] = verify_trim(model)

    # number of cores
    for line in cmd_out.split("\n"):
        if "CPU(s):" in line:
            numcores = re.search('CPU\(s\):(.*)', cmd_out).group(1)
    the_dict['numcores'] = verify_trim(numcores)

    # CPU max MHz
    for line in cmd_out.split("\n"):
        if "CPU max MHz:" in line:
            maxmhz = re.search('CPU max MHz:(.*)', cmd_out).group(1)
    the_dict['maxmhz'] = verify_trim(maxmhz)

    return the_dict

def parse_satime(cmd_out, the_dict):
    # 'systemd-analyze time' key metrics and key names
    satime_list = ["kernel", "initrd", "userspace"]

    for i, regex in enumerate(satime_list):
        result = re.findall('(\d+\.\d+)s\s\('+regex+'\)', cmd_out)
        the_dict[regex] = float(verify_trim(result[0]))

    return the_dict

def parse_sablame(cmd_out, the_dict):
    # Parse cmd output, calc time in seconds and populate dict
    num_blames = 5 
    cntr = 1

    for line in cmd_out.split("\n"):
        if cntr <= num_blames:
            words = re.split(r'\s', line)
            service = words[-1]
            minutes = re.search('(\d+)min', line)
            seconds = re.search('(\d+\.\d+)s', line)
            millisec = re.search('(\d+)ms', line)
            if (minutes and seconds):
                min = minutes[0].strip("min")
                sec = seconds[0].strip("s")
                total_sec = str((int(min) * 60) + float(sec))
            elif (seconds and not minutes):
                total_sec = seconds[0].strip("s")
            elif millisec:
                ms = millisec[0].strip("ms")
                total_sec = str((int(ms)/1000)%60)

            if (service and total_sec):
                cntr += 1
                the_dict[service] = float(total_sec)
        else:
            break

    return the_dict

def verify_trim(value):
    # Check for value
    if not value:
        ret_val = str("")
    else:
        ret_val = str(value.strip())

    return ret_val

####################
# MAIN()
#
def main():
    # Dictionaries
    testrun_dict = {}          # complete run results (final dict)
    testcfg_dict = {}          # test configuration
    syscfg_dict = {}           # test configuration
    data_dict = {}             # test data/results (nested)
    satime_dict = {}           # systemd-analyze time results
    sablame_dict = {}          # systemd-analyze blame results
    # Vars
    to_unicode = str

    # Add current date timestamp to testrun_dict{}
    curtime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    testrun_dict['curtime'] = str(curtime.strip())

    ##########################
    # Get 'test_config' values
    #
    # systemctl target
    sysctl_out = subprocess.run(['systemctl', 'get-default'],
        stdout=subprocess.PIPE)
    testcfg_dict['target'] =\
        str(verify_trim(sysctl_out.stdout.decode('utf-8')))

    # testcfg_dict{} populated, insert it into testrun_dict{}
    testrun_dict["test_config"] = testcfg_dict

    ##########################
    # Get 'system_config' values
    #
    # kernel version
    kversion_out = subprocess.run(['uname', '-r'], stdout=subprocess.PIPE)
    syscfg_dict['kernel'] =\
        str(verify_trim(kversion_out.stdout.decode('utf-8')))

    # Linux Distro
    syscfg_dict['distro'] = str(verify_trim(distro.name(pretty=True)))

    # cpu test config values
    lscpu_out = subprocess.run(['lscpu'], stdout=subprocess.PIPE)
    lscpu_out = lscpu_out.stdout.decode('utf-8')
    # Parse results from 'lscpu' command
    syscfg_dict = parse_lscpu(lscpu_out, syscfg_dict)

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
    # Parse cmd output and populate dict
    satime_dict = parse_satime(satime_out, satime_dict)

    # 'systemd-analyze blame' cmd
    sablame_out = subprocess.run(['systemd-analyze', 'blame'],
        stdout=subprocess.PIPE)
    sablame_out = sablame_out.stdout.decode('utf-8')
    # Parse cmd output and populate dict
    sablame_dict = parse_sablame(sablame_out, sablame_dict)

    # Insert test result dictionaries into data_dict{}
    data_dict['sa_time'] = satime_dict
    data_dict['sa_blame'] = sablame_dict

    # Insert data_dict{} into testrun_dict (final dictionary)
    testrun_dict['test_results'] = data_dict

    # Insert syscfg_dict{} into testrun_dict{}
    testrun_dict["system_config"] = syscfg_dict
    print("**TESTRUN DICT**")        # DEBUG
    print(testrun_dict)              # DEBUG

    # Write JSON file
    with io.open('testrun.json', 'w', encoding='utf8') as outfile:
        str_ = json.dumps(testrun_dict,
                          indent=4, sort_keys=False,
                          separators=(',', ': '), ensure_ascii=False)
        outfile.write(to_unicode(str_))
        outfile.write(to_unicode("\n"))

    print("Wrote file: testrun.json")


if __name__ == "__main__":
    main()

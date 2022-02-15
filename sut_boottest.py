#!/usr/bin/env python3
# Reboots remote systems (SUTs) and captures boot timing results
# Writes JSON file in format ready for ingest in ElasticSearch
#
# Tested on CentOS Stream 8 - Python 3.6.8.
# DEPENDENCIES: # python3 -m pip install paramiko
#
# Edit SUT VARS section for your test environment systems
#

#####################################
# SUT VARS
#      >> EDIT THIS LIST FOR YOUR ENVIRONMENT <<
#
#      "hostname" , "ipAddr" , "user", "password"
sut_list = [
    ("testrpi4", "192.168.0.108", "root", "password"),
    ("rpi4",     "192.168.0.111", "root", "100yard-"),
    ("johnagx",  "192.168.0.120", "root", "100yard-")
]

#####################################
# DICTIONARY Format - dicts initialized in main()
#
# testrun_dict = {
#     "cluster_name": hostname,
#     "date": curtime,
#     "test_type": "boot-time",
#     "sample": 1,
#     "test_config": {
#         testcfg_dict{}
#     }, 
#     "test_results": {
#         "reboot":
#             reboot_dict{}
#         "satime":
#             sa_dict{}
#         "sablame":
#             sa_dict{}
#         "neptuneui":
#             neptuneui_dict{}
#     },
#     "system_config": {
#         syscfg_dict{}
#     } 
# }
#

import sys
import time
import paramiko
import re
import datetime
import json
import io

#####################################
# CLASSES
class TimerError(Exception):
    # A custom exception used to report errors in use of Timer class
    # use built-in class for error handling
    pass

class Timer: 
    def __init__(self, text="Elapsed time: {:0.2f} seconds", logger=print):
        self._start_time = None
        self.text = text
        self.logger = logger

    def start(self):
        # Start a new timer
        if self._start_time is not None:
            raise TimerError(f"Timer is running. Use .stop() to stop it")
        self._start_time = time.perf_counter()

    def stop(self):
        # Stop the timer, and report the elapsed time in seconds
        if self._start_time is None:
            raise TimerError(f"Timer is not running. Use .start() to start it")
        elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None
        if self.logger:
            self.logger(self.text.format(elapsed_time))
        return elapsed_time

#####################################
# FUNCTIONS
def write_json(thedict, thefile):
    to_unicode = str
   # Write JSON file
    with io.open(thefile, 'w', encoding='utf8') as outfile:
        str_ = json.dumps(thedict,
                          indent=4, sort_keys=False,
                          separators=(',', ': '), ensure_ascii=False)
        outfile.write(to_unicode(str_))
        outfile.write(to_unicode("\n"))

    print(f"Wrote file: {thefile}")

def init_dict(hname, ip, reboot, ssh, boot_tgt, bl_cnt):
    # Initialize new dict{} for the test config for this workload
    the_dict = {}             # new empty dict

    the_dict["hostname"] = str(hname)
    the_dict["IPaddr"] = str(ip)
    the_dict["reboot_timeout"] = str(reboot_timeout)
    the_dict["ssh_timeout"] = str(ssh_timeout)
    the_dict["boot_tgt"] = str(boot_tgt)
    the_dict["blame_cnt"] = str(bl_cnt)

    return the_dict

##################################
# PARSER Functions
def parse_osrelease(cmd_out, the_dict):
    # PRETTY NAME value
    for line in cmd_out.split("\n"):
        if "PRETTY_NAME=" in line:
            raw_str = re.search('PRETTY_NAME=(.*)', cmd_out).group(1)
            pname = raw_str.replace('"', "")   # remove surrounding quotes
    the_dict['osrelease'] = verify_trim(pname)

    return the_dict

def parse_lscpu(cmd_out, the_dict):
    # cpu architecture
    for line in cmd_out.split("\n"):
        if "Architecture:" in line:
            arch = re.search('Architecture:(.*)', cmd_out).group(1)
    the_dict['architecture'] = verify_trim(arch)

    # cpu model
    for line in cmd_out.split("\n"):
        if "Model name:" in line:
            model = re.search('Model name.*:(.*)', cmd_out).group(1)
    the_dict['model'] = verify_trim(model)

    # Number of cores
    for line in cmd_out.split("\n"):
        if "CPU(s):" in line:
            numcores = re.search('CPU\(s\):(.*)', cmd_out).group(1)
    the_dict['numcores'] = verify_trim(numcores)

    # BogoMIPS
    for line in cmd_out.split("\n"):
        if "BogoMIPS:" in line:
            bogo = re.search('BogoMIPS:(.*)', cmd_out).group(1)
    the_dict['bogomips'] = verify_trim(bogo)

    return the_dict

def parse_satime(cmd_out, the_dict):
    # 'systemd-analyze time' key metrics and key names
    satime_list = ["kernel", "initrd", "userspace"]

##    for i, regex in enumerate(satime_list):
    for regex in satime_list:
        matches = re.findall('(\d+\.\d+)s\s\('+regex+'\)', cmd_out)
##        result = re.search('(\d+\.\d+)s\s\('+regex+'\)', cmd_out)
        if matches:
            the_dict[regex] = float(matches[0])
        else:
            the_dict[regex] = float(0.0)

    return the_dict

def parse_sablame(cmd_out, the_dict, blame_cnt):
    # Parse cmd output, calc time in seconds and populate dict
    cntr = 1
    for line in cmd_out.split("\n"):
        if (cntr <= int(blame_cnt)):
            ##words = re.split(r'\s', line)
            words = line.split()
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

def parse_neptuneui(cmd_out, the_dict, km_list):
    # Parse neptune-ui timing stats and populate dict
    for line in cmd_out.split("\n"):
        for x, (km_label, search_str) in enumerate (km_list):
            if search_str in line:
                # key metric found, extract key/value
                rstrip1 = line.rstrip('#')
                rstrip2 = rstrip1.rstrip()
                splitted = rstrip2.split(':')
                result = splitted[3].lstrip()
##                keymsg = re.search(key_metric, result)
                raw_value = result.split(' ')
                # cleanup raw_value: 3'975.381  --> 3.975381
                tmp1 = raw_value[0].replace(".", "")
                tmp2 = tmp1.replace("'", ".") 
                the_dict[km_label] = float(tmp2) 

    return the_dict

def verify_trim(value):  # Extend to handle str(), float(), int()
    # Verify value. Return value or None if invalid
    if not value:
##        ret_val = str("")
        ret_val = None
    else:
        ret_val = str(value.strip())

    return ret_val

def openclient(ssh_ip, ssh_user, ssh_passwd, tout):
    # Initiate SSH connection
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    result = None       # returned when w/exception OR timeout exceeded

    # Start timeout timer and calc end timer
    timeout_exceeded = time.time() + tout

    while time.time() < timeout_exceeded:
        try:
            client.connect(ssh_ip, username=ssh_user, password=ssh_passwd,
                port=22, look_for_keys=False, allow_agent=False)

        except paramiko.ssh_exception.SSHException as e:
            # socket is open, but no SSH service responded
            if e.message == 'Error reading SSH protocol banner':
                print(e)
                continue
            print('SSH transport is available but exception occured')
            break

        except paramiko.ssh_exception.NoValidConnectionsError as e:
##            print('SSH transport is not ready...')
            continue

        else:
##            print('SSH responded!')
            result = client
            break

        time.sleep(retry_int)         # pause between retries (GLOBAL)

    return result

def testssh(ip, usr, pswd, retry_timeout):
    ssh_status = False         # return value

    # Verify SUT can be ssh'd to
    print(f'> testssh: verifying SSH to {ip}. Timeout: {retry_timeout}s')

    # STOPWATCH returns elapsed time in seconds
##    et_ssh = Timer(text="testssh: SUT ssh active in {:.2f} seconds",\
##                      logger=print)
    et_ssh = Timer(text="", logger=None)    # Be silent
    et_ssh.start()

    ssh = openclient(ip, usr, pswd, retry_timeout)
    if ssh == None:
        # Error condition - no connection to close
        print(f'testssh: Could not connect to {ip}. Timed out')
        ssh_status = False     # continue on to next SUT
    else: 
        # Stop the stopwatch and report on elapsed time
        et_ssh.stop()

        # Close SSH connection
        ssh.close()
        ssh_status = True     # connection success
    return ssh_status

########## per Phase functions
# Phase 1 - gather sysfacts and populate dict{}
def phase1(sship, sshuser, sshpasswd):
    ph1_dict = {}         # empty dict{} for us in this phase function
    #              KEY        COMMAND
    cmd_list = [("kernel", "uname -r"),
                ("osrelease", "cat /etc/os-release | grep PRETTY_NAME"),
                ("various", "lscpu")
    ]

    # Initiate SSH connection - ssh_timeout (GLOBAL)
    client = openclient(sship, sshuser, sshpasswd, ssh_timeout)

    for x, (key, cmd) in enumerate (cmd_list):
##        print(f'COMMAND: {cmd}')
        # redirect stderr to stdout
        cmd_str = cmd + " 2> \&1"
        stdin, stdout, stderr = client.exec_command(cmd_str, get_pty=True)
        # Block on completion of exec_command
        exit_status = stdout.channel.recv_exit_status()
        # Single string contains entire cmd result
        cmd_result = stdout.read().decode('utf8').rstrip('\n')

        # Populate dict{}, format varies with command type
        if "lscpu" in cmd:
            # Parse results from 'lscpu' command
            ph1_dict = parse_lscpu(cmd_result, ph1_dict)
        elif "os-release" in cmd:
            # Parse results from 'cat' command
            ph1_dict = parse_osrelease(cmd_result, ph1_dict)
        else:
            ph1_dict[key] = str(verify_trim(cmd_result))

    # Close SSH connection
    client.close()

    return ph1_dict

# Phase 2 - configure SUT for (consistent) reboot
def phase2(sship, sshuser, sshpasswd, boot_target):
    # Initiate SSH connection - ssh_timeout (GLOBAL)
    client = openclient(sship, sshuser, sshpasswd, ssh_timeout)

    # Set target boot mode

    # If neptune-ui running, then enable Neptune UI startup timings
    neptuneui_enabled = False
    # check for neptune pids

    # Verify target boot mode

    # Close SSH connection
    client.close()

    return neptuneui_enabled

# Phase 3 - reboot and wait for system readiness
def phase3(ip, usr, passwd):
    ph3_dict = {}         # empty dict{} for use in this phase function
    # Initiate SSH connection - ssh_timeout (GLOBAL)
    ssh_reboot = openclient(ip, usr, passwd, ssh_timeout)

    # Issue reboot cmd
    try:
        ssh_reboot.exec_command("uptime >/dev/null 2>&1")  # DEBUG
        ssh_reboot.close()                                 # DEBUG
##        ssh_reboot.exec_command("reboot >/dev/null 2>&1")
    except:
        # Error, suggested to explictly close
        ssh_reboot.close()
        print('reboot issue failed')
        sys.exit(1)

    ######################
    # START the clock on total shutdown and reboot time
    et_reboot = Timer(
        text="phase3: SUT shutdown and reboot required {:.2f} seconds",
        logger=print)           ## SILENCE THIS 'logger=none'
    et_reboot.start()

    # Need to stall/pause while shutdown completes
    delay = 5           # just a guess, pause for reboot to complete
    time.sleep(delay)   # just a guess...

    # Start ssh timer
    ssh_start = time.time()

    # Verify SSH responds. Wait upto 'reboot_timeout' (GLOBAL) 
    ping_ssh = testssh(ip, usr, passwd, reboot_timeout)
    if ping_ssh is False:
        print('phase3: Aborting test run') 
        sys.exit(1)

    # Reboot closed existing SSH client, open new as SUT boots
    # Verify SSH responds. Wait upto 'ssh_timeout' (GLOBAL) 
    ssh_new = openclient(ip, usr, passwd, ssh_timeout)

    # Stop ssh timer and calc elapsed time
    ssh_et = time.time() - ssh_start

    # SSH is active, now wait for system up condition:
    #     'systemctl list-jobs == No jobs running'
    sysctl_start = time.time()
    rebooted = False
    pause = 1         # NOTE: timer granularity NEEDS WORK 

    print(f'phase3: SUT {ip}, ', 
          f'waiting {reboot_timeout}s for reboot to complete...''')
    while rebooted == False:
        # if cmd==True, then SUT has completed boot process
        cmd = "systemctl list-jobs | grep -q 'No jobs running'"
        cmd_str = cmd + " 2> \&1"
        stdin, stdout, stderr = ssh_new.exec_command(
                cmd_str, get_pty=True)
        # Block on completion of exec_command
        exit_status = stdout.channel.recv_exit_status()
        # Test for completed boot
        if exit_status == 0:
            rebooted = True          # Triggers break out of loop
        else:
            time.sleep(pause)

        # Test if exceeded time limit
        sysctl_et = time.time() - sysctl_start
        total_et = ssh_et + sysctl_et
        if total_et >= reboot_timeout:
            # Error, suggested to explictly close
            ssh_new.close()
            print(f'rebootsut: SUT {ip} reboot Timed out')
            sys.exit(1)

    # SUCCESS
    # Stop timer and Populate reboot_dict{} with results
    reboot_et = et_reboot.stop()
    ph3_dict['reboot_et'] = float(reboot_et)
    ph3_dict['ssh_et'] = float(ssh_et)
    ph3_dict['sysctl_et'] = float(sysctl_et)
    ph3_dict['total_et'] = float(total_et)
    
    # Record boot target
    cmd_bt = "systemctl get-default 2> \&1"
    stdin, stdout, stderr = ssh_new.exec_command(cmd_bt, get_pty=True)
    # Block on completion of exec_command
    exit_status = stdout.channel.recv_exit_status()
    cmdres_bt = stdout.read().decode('utf8').rstrip('\n')
    ph3_dict['boot_tgt'] = str(verify_trim(cmdres_bt))

    ssh_new.close()

    return ph3_dict

# Phase 4
# - executes instr_list cmds, builds dict from cmd result and returns dict
def phase4(ip, usr, passwd, num_blames):
    satime_dict = {}           # systemd-analyze time results
    sablame_dict = {}          # systemd-analyze blame results
    ph4_dict = {}              # systemd-analyze complete results
    #                 KEY        COMMAND
    instr_list = [("sa_time",  "systemd-analyze time"),
                  ("sa_blame", "systemd-analyze blame --no-pager")
    ]

    # Initiate SSH connection - ssh_timeout (GLOBAL)
    client = openclient(ip, usr, passwd, ssh_timeout)

    for x, (key, cmd) in enumerate (instr_list):
        # redirect stderr to stdout
        cmd_str = cmd + " 2> \&1"
        stdin, stdout, stderr = client.exec_command(cmd_str, get_pty=True)
        # Block on completion of exec_command
        exit_status = stdout.channel.recv_exit_status()

        # single string contains entire cmd result
        cmd_result = stdout.read().decode('utf8').rstrip('\n')

        # populate dictionaries, format varies with command type
        if "sa_time" in key:
            satime_dict = parse_satime(cmd_result, satime_dict)
            ph4_dict[key] = satime_dict

        if "sa_blame" in key:
            sablame_dict = parse_sablame(cmd_result, sablame_dict, num_blames)
            ph4_dict[key] = sablame_dict

    return ph4_dict

def phase5(ip, usr, passwd):
    # VARS
    ph5_dict = {}          # neptune-ui startup timings
    # List of key metric search strings and dict keys
    #                 KEY        SEARCH STRING
    km_list = [("logging", "after logging setup"),
               ("D-Bus",   "after starting session D-Bus"),
               ("first-frame", "after first frame drawn")
    ]

    # Initiate SSH connection - ssh_timeout (GLOBAL)
    client = openclient(ip, usr, passwd, ssh_timeout)

    cmd = "journalctl | grep -m1 -A20 'STARTUP TIMING REPORT: System UI'"

    # redirect stderr to stdout
    cmd_str = cmd + " 2> \&1"
    stdin, stdout, stderr = client.exec_command(cmd_str, get_pty=True)
    # Block on completion of exec_command
    exit_status = stdout.channel.recv_exit_status()

    # Check if CMD suceeded, perhaps neptune-ui isn't running
    if exit_status != 0:
        print("neptune_stats:"\
              " neptune-ui startup timing stats unavailable on SUT,"\
              " skipping")
        return ph5_dict           # return empty dict{}

    # single string contains entire cmd result
    cmd_result = stdout.read().decode('utf8').rstrip('\n')

    # Parse neptune stats from cmd_out and populate dict
    ph5_dict = parse_neptuneui(cmd_result, ph5_dict, km_list) 

    return ph5_dict

#####################################
# GLOBAL VARS
target = "multi-user.target"  # graphical.target
reboot_timeout = 300          # max. number of seconds: rebootsut()
ssh_timeout = 20              # max. number of seconds: testssh()
retry_int = 2                 # client.connect retry interval (in sec)

##############################################################
# MAIN

def main():
    blame_cnt = 5            # number of sablame services to record
    outfilename = str(
        datetime.datetime.now().strftime('%m_%d_%Y_%H_%M_%S') + ".json")

    # List of Dictionaries
    results_list = []          # comprehensive results (all SUTs)

    ##########################
    # OUTER LOOP - For each SUT
    for i, (sut_host, sut_ip, sut_usr, sut_pswd) in enumerate(sut_list):
        print(f'\n***SUT: {sut_ip}  {sut_host}***')
        # Dictionaries
        testrun_dict = {}        # complete testrun results (per SUT)
        testcfg_dict = {}        # test configuration
        syscfg_dict = {}         # system configuration
        data_dict = {}           # testdata results (nested)

        # Verify connectivity to SUT
        ping_ssh1 = testssh(sut_ip, sut_usr, sut_pswd, ssh_timeout)
        if ping_ssh1 is False:
            continue            # skip this SUT

        # Add to dict{} for this SUT
        testrun_dict["cluster_name"] = str(sut_host) 
        curtime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        testrun_dict["date"] = str(curtime.strip())
        testrun_dict["test_type"] = "boot-time"   # hardcoded
        testrun_dict["sample"] = int(1)           # hardcoded

        # Initialize testcfg dict{} for this SUT
        testcfg_dict = init_dict(
            sut_host, sut_ip, reboot_timeout, ssh_timeout, target, blame_cnt)
        testrun_dict["test_config"] = testcfg_dict

        ############
        # INNER LOOP
        # Proceed through testing phases
        #----------
        # Phase 1: gather system facts
        print(f'*Phase 1 - gather facts')
        syscfg_dict = phase1(sut_ip, sut_usr, sut_pswd)

        #----------
        # Phase 2: configure SUT for reboot
        # returns if neptuneui (boolean) is running
        print(f'*Phase 2 - configure SUT for reboot')
        neptuneui = phase2(sut_ip, sut_usr, sut_pswd, target)

        #----------
        # Phase 3: initiate reboot, wait for system readiness
        #          and record timing results into reboot_dict{}
        print(f'*Phase 3 - initiate reboot and wait for system readiness')
        reboot_dict = phase3(sut_ip, sut_usr, sut_pswd)
        # Verify connectivity to freshly rebooted SUT
        ping_ssh2 = testssh(sut_ip, sut_usr, sut_pswd, ssh_timeout)
        if ping_ssh2 is False:
            continue           # reboot failed, abort this SUT test

        #----------
        # Phase 4: instrument SUT reboot w/systemd-analyze commands
        # NOTE: sa_dict is nested with "sa_time" and "sa_blame" keys
        print(f'*Phase 4 - record systemd-analyze reboot stats')
        sa_dict = phase4(sut_ip, sut_usr, sut_pswd, blame_cnt)

        #----------
        # Phase 5: neptune UI startup timings
        print(f'*Phase 5 - neptune timing stats (if available)')
        neptuneui_dict = phase5(sut_ip, sut_usr, sut_pswd)

        ######################
        # All PHASEs for this SUT completed
        # Insert existing test results into 'test_results' section
        data_dict["reboot"] = reboot_dict
        data_dict["satime"] = sa_dict["sa_time"]
        data_dict["sablame"] = sa_dict["sa_blame"]
        data_dict["neptuneui"] = neptuneui_dict

        # Insert complete data_dict{} into testrun_dict (final dictionary)
        testrun_dict["test_results"] = data_dict

        # Insert syscfg_dict{} into testrun_dict{}
        testrun_dict["system_config"] = syscfg_dict
        
        # Insert test results for this SUT into results_list[]
        results_list.append(testrun_dict)

    print(f'+++TESTING COMPLETED+++')

    write_json(results_list, outfilename)

    # END MAIN

if __name__ == "__main__":
    main()

##############################################################

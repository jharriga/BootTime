#!/usr/bin/env python3
#
# Tested on CentOS Stream 8 - Python 3.6.8.
# DEPENDENCIES: # python3 -m pip install paramiko
#
# Define SUT VARS section for your test environment systems
#

import sys
import time
import paramiko

#####################################
# SUT VARS
#        >> CONFIGURE THESE FOR YOUR ENVIRONMENT <<
#
ipaddr_list = ["192.168.0.108","192.168.0.111","192.168.0.120"]
##ipaddr_list = ["192.168.0.108"]
host_list = ["testrpi4","rpi4","johnagx"]
user_list = ["root","root","root"]
passwd_list = ["password","100yard-","100yard-"]

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
    # Verify SUT can be ssh'd to
    print(f'testssh: verifying SSH to {ip}. Timeout: {retry_timeout}s')

    # STOPWATCH returns elapsed time in seconds
    et_ssh = Timer(text="testssh: SUT ssh active in {:.2f} seconds",\
                      logger=print)
    et_ssh.start()

    ssh = openclient(ip, usr, pswd, retry_timeout)
    if ssh == None:
        # Error condition - no connection to close
        print(f'\ntestssh: Could not connect to {ip}. Timed out')
        sys.exit(1)
        
    # Stop the stopwatch and report on elapsed time
    et_ssh.stop()

    # Close SSH connection
    ssh.close()
    return

########## per Phase functions
# Phase 1 and Phase 4
# - executes SSHcmd and prints command result
def ssh_print(client, cmd):
    # redirect stderr to stdout
    cmd_str = cmd + " 2> \&1"
    stdin, stdout, stderr = client.exec_command(cmd_str, get_pty=True)
    # Block on completion of exec_command
    exit_status = stdout.channel.recv_exit_status()
    print(stdout.read().decode('utf8').rstrip('\n'))

    return

# Phase 2 - configure SUT for (consistent) reboot
def cfg4reboot(ssh_client, boot_target):
    pass
    # Set target boot mode
    # If neptune running, then enable Neptune UI startup timings
    # Verify target boot mode

    return

# Phase 3 - reboot and wait for system readiness
def rebootsut(ssh_reboot, ip, usr, passwd):
    # Issue reboot cmd. Don't test or capture return code
    try:
##        ssh_reboot.exec_command("uptime >/dev/null 2>&1")
##        ssh_reboot.close()
        ssh_reboot.exec_command("reboot >/dev/null 2>&1")
    except:
        # Error, suggested to explictly close
        ssh_reboot.close()
        print('reboot issue failed')
        sys.exit(1)

    ######################
    # START the clock on total shutdown and reboot time
    et_reboot = Timer(
        text="rebootsut: SUT shutdown and reboot required {:.2f} seconds",
        logger=print)
    et_reboot.start()

    # Need to stall/pause while shutdown completes
    delay = 5           # just a guess, pause for reboot to complete
    time.sleep(delay)   # just a guess...

    # Start ssh timer
    ssh_start = time.time()

    # Verify SSH responds. Wait upto 'reboot_timeout' (GLOBAL) 
    testssh(ip, usr, passwd, reboot_timeout)

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

    print(f'rebootsut: SUT {ip}, ', 
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

    # SUCCESS - Print results
    et_reboot.stop()
    print('rebootsut: * state-change timers:')
    print(f'  > SSH active: {ssh_et:0.2f}s')
    print(f'  > SYSTEMCTL complete: {sysctl_et:0.2f}s')
    print(f'  > TOTAL reboot elapsed time: {total_et:0.2f}s')

    ssh_new.close()

    return

########## Main Worker Function
def sutcmd(sship, sshuser, sshpasswd, sshcmd, phase):
    # Initiate SSH connection - ssh_timeout (GLOBAL)
    client = openclient(sship, sshuser, sshpasswd, ssh_timeout)

    if phase == 'phase1' or phase == 'phase4':
        ssh_print(client, sshcmd)

    elif phase == 'phase2':
        # EMPTY 
        cfg4reboot(client, target)

    elif phase == 'phase3':
        # Requires multiple SSH clients
        rebootsut(client, sship, sshuser, sshpasswd)

    else:
        print(f'sutcmd: unrecognized phase {phase}, exiting')
        client.close()                        # cleanup
        sys.exit(1)

    # We're done, explicitly close the connection
    client.close()
    return

#####################################
# GATHER SYSTEM FACTS
# remove leading whitespace from second field
rmwhitesp1 = "awk -F ':' '{gsub(/^[ \\t]+/, \"\", $2); print $2}'"
stripquotes = "awk -F '=' '{gsub(/\"/, \"\", $2); print $2}'"
kversion = "uname -r"
osrelease = "cat /etc/os-release | grep PRETTY_NAME | " + stripquotes
cpumodel = "lscpu | grep -m1 'Model name:' | " + rmwhitesp1 
numcores = "lscpu | grep -m1 'CPU(s):' | " + rmwhitesp1
facts_list = [kversion, osrelease, cpumodel, numcores]

# SYSTEMD-ANALYZE
# remove leading whitespace from command output
rmwhitesp2 = "awk '{gsub(/^[ \\t]+/, \"\", $0); print $0}'"
numblames = "5"
satime = "systemd-analyze time"
sablame = "systemd-analyze blame | head -n " + numblames + " | " + rmwhitesp2
##instr_list = ["systemd-analyze time","systemd-analyze blame | head -n 5"]
instr_list = [satime, sablame]

# OTHER VARS
target = "multi-user.target"  # graphical.target
reboot_timeout = 300          # max. number of seconds: rebootsut()
ssh_timeout = 20              # max. number of seconds: testssh()
retry_int = 2                 # client.connect retry interval (in sec)

##############################################################
# MAIN

def main():
    # OUTER LOOP - For each SUT
    for i, sutip in enumerate(ipaddr_list):
        print(f'\n***NEXT SUT: {sutip}  {host_list[i]}***')

        # Verify connectivity to SUT
        testssh(sutip, user_list[i], passwd_list[i], ssh_timeout)

        ############
        # INNER LOOP
        # Proceed through testing phases
        # Phase 1: gather system facts = facts_list[]
        print(f'*Phase 1 - gather facts')
        for cmd in facts_list:
##            print(f'COMMAND: {cmd}')
            sutcmd(sutip, user_list[i], passwd_list[i], cmd, "phase1")

        # Phase 2: configure SUT for reboot
        print(f'*Phase 2 - configure SUT for reboot')
        sutcmd(sutip, user_list[i], passwd_list[i], "null", "phase2")

        # Phase 3: initiate reboot and wait for system readiness
        print(f'*Phase 3 - initiate reboot and wait for system readiness')
        sutcmd(sutip, user_list[i], passwd_list[i], "null", "phase3")
        # Verify connectivity to freshly rebooted SUT
        testssh(sutip, user_list[i], passwd_list[i], ssh_timeout)

        # Phase 4: instrument SUT reboot = instr_list[]
        print(f'*Phase 4 - instrument reboot stats')
        for cmd in instr_list:
##            print(f'COMMAND: {cmd}')
            sutcmd(sutip, user_list[i], passwd_list[i], cmd, "phase4")

    print(f'+++TESTING COMPLETED+++')

    # END MAIN

if __name__ == "__main__":
    main()

##############################################################

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
host_list = ["testrpi4","rpi4","johnagx"]
user_list = ["root","root","root"]
passwd_list = ["password","100yard-","100yard-"]

#####################################
# FUNCTIONS

def openclient(ssh_ip, ssh_user, ssh_passwd):
    # Initiate SSH connection
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(ssh_ip, username=ssh_user, password=ssh_passwd,
                port=22, timeout=2)
    except Exception as _e:
        sys.stdout.write(str(_e))
        sys.exit(1)
    return client

def testssh(ip, usr, pswd, retry_time):
    # Verify SUT can be ssh'd to
    interval = 2                     # adjust as needed
    cntr = 0

##
## ADD STOPWATCH AND PRINT ELAPSED-time
##
    print(f"testssh: verifying SSH to {ip}. Timeout: {retry_time}s")
    while True:
        try:
            ssh = openclient(ip, usr, pswd)
            break
        except:
            print(f"Could not SSH to {ip}, waiting {interval}s...")
            cntr += interval
            time.sleep(interval)

        # Could not connect within time limit
        if cntr >= retry_time:
            print(f"Could not connect to {ip}. Timed out")
            sys.exit(1)

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
def rebootsut(ssh_client, ip, usr, passwd, timeout):
    # open new channel
##    ch_reboot = openchannel(ssh_client)

    # Issue reboot cmd. Don't test or capture return code
    try:
##    ch_reboot.exec_command("reboot") 
        ssh_client.exec_command("uptime >/dev/null 2>&1")
    except:
        print("reboot issue failed")
        sys.exit(1)

##
## ADD STOPWATCH AND PRINT ELAPSED-time
##
    # Wait for system up: 'systemctl list-jobs == No jobs running” 
    interval = 5           # adjust as needed
    cntr = 0
    while True:
        try:
            # if cmd==True, then SUT has completed boot process
            cmd = "systemctl list-jobs | grep -q 'No jobs running'"
            cmd_str = cmd + " 2> \&1"
            stdin, stdout, stderr = ssh_client.exec_command(
                cmd_str, get_pty=True)
            # Block on completion of exec_command
            exit_status = stdout.channel.recv_exit_status()
            break
        except:
            print(f"rebootsut: SUT {ip}, waiting {timeout}s for reboot...")
            cntr += interval
            time.sleep(interval)

        # Test if exceeded time limit
        if cntr >= timeout:
            print(f"rebootsut: SUT {ip} reboot Timed out")
            ch_wait.shutdown_write()
            sys.exit(1)

    print(f"rebootsut: SUT {ip} has rebooted") 
##    ch_wait.shutdown_write()

    return

########## Main Worker Function
def sutcmd(sship, sshuser, sshpasswd, sshcmd, phase):
    # Initiate SSH connection
    client = openclient(sship, sshuser, sshpasswd)

    if phase == 'phase1' or phase == 'phase4':
        ssh_print(client, sshcmd)

    elif phase == 'phase2':
        # Requires multiple SSH channels
        cfg4reboot(client, target)

    elif phase == 'phase3':
        # Requires multiple SSH channels
        rebootsut(client, sship, sshuser, sshpasswd, reboot_timeout)

    else:
        print(f"sutcmd: unrecognized phase {phase}, exiting")
        client.close()                        # cleanup
        sys.exit(1)

    # We're done, explicitly close the connection
    client.close()
    return

#####################################
# SUT VARS
ipaddr_list = ["192.168.0.108","192.168.0.111","192.168.0.120"]
host_list = ["testrpi4","rpi4","johnagx"]
user_list = ["root","root","root"]
passwd_list = ["password","100yard-","100yard-"]

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
target = "multi-user.target"    # graphical.target
reboot_timeout = 100            # number of seconds: rebootsut()
ssh_timeout = 20                # number of seconds: testssh()

##############################################################
# MAIN
# OUTER LOOP - For each SUT
for i, sutip in enumerate(ipaddr_list):
    print(f"\n***NEXT SUT: {sutip}  {host_list[i]}***")

# Verify connectivity to SUT
    testssh(sutip, user_list[i], passwd_list[i], ssh_timeout)

    ############
    # INNER LOOP
    # Proceed through testing phases
    # Phase 1: gather system facts = facts_list[]
    print(f"*Phase 1 - gather facts")
    for cmd in facts_list:
        print(f"COMMAND: {cmd}")
        sutcmd(sutip, user_list[i], passwd_list[i], cmd, "phase1")

    # Phase 2: configure SUT for reboot
    print(f"*Phase 2 - configure SUT for reboot")
    sutcmd(sutip, user_list[i], passwd_list[i], "null", "phase2")

    # Phase 3: initiate reboot and wait for system readiness
    print(f"*Phase 3 - initiate reboot and wait for system readiness")
    sutcmd(sutip, user_list[i], passwd_list[i], "null", "phase3")
    # Verify connectivity to rebooted SUT
    testssh(sutip, user_list[i], passwd_list[i], ssh_timeout)

    # Phase 4: instrument SUT reboot = instr_list[]
    print(f"*Phase 4 - instrument reboot stats")
    for cmd in instr_list:
        print(f"COMMAND: {cmd}")
        sutcmd(sutip, user_list[i], passwd_list[i], cmd, "phase4")

print(f"+++TESTING COMPLETED+++")

# END
##############################################################

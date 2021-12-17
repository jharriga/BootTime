#!/usr/bin/env python3
#
# Tested on CentOS Stream 8 - Python 3.6.8.
# DEPENDENCIES: # python3 -m pip install paramiko
#

import sys
import paramiko

def responseGen(channel):
    # Small outputs (i.e. 'whoami') can end up running too quickly
    # so we yield channel.recv in both scenarios
    while True:
        if channel.recv_ready():
            yield channel.recv(4096).decode('utf-8')

        if channel.exit_status_ready():
            yield channel.recv(4096).decode('utf-8')
            break

# VARS
ipaddr_list = ["192.168.0.108","192.168.0.111"]
passwd_list = ["password","100yard-"]
cmds_list = ["uname -r","cat /etc/os-release | grep PRETTY_NAME",
             "systemd-analyze time","systemd-analyze blame | head -n 5"]

# OUTER LOOP
# For each SUT
for i, sutip in enumerate(ipaddr_list):
    print(f"SUT: {sutip}")

# INNER LOOP - gather system facts, then instrument boot
# for each cmd to executed on SUT
    for j, cmd in enumerate(cmds_list):
        print(f"COMMAND: {cmd}")

# MAIN WORKFLOW
# Initiate SSH connection
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            client.connect(sutip, username='root', password=passwd_list[i],
                port=22, timeout=2)
        except Exception as _e:
            sys.stdout.write(str(_e))

# is_active can be a false positive, so further test
        transport = client.get_transport()
        if transport.is_active():
            try:
                transport.send_ignore()
            except Exception as _e:
                sys.stdout.write(_e)
                sys.exit(1)
        else:
           sys.exit(1)

        channel = transport.open_session()

# We're not handling stdout & stderr separately
        channel.set_combine_stderr(1)
        channel.exec_command(cmd)

# Command was sent, no longer need stdin
        channel.shutdown_write()

# iterate over each yield as it is given 
        for response in responseGen(channel):
            sys.stdout.write(response)

# Command was sent, no longer need stdin
        channel.shutdown_write()

# We're done, explicitly close the conenction
        client.close()

# Done with this CMD : write completed marker
    print(f"***COMMAND**********************")

# Done with this SUT : write completed marker
print(f"+++++++SUT++++++++++++++++++++++++++++")

# Next SUT...

# END


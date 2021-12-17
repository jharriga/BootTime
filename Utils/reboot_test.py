####################################### 

import sys
import time
import datetime
import paramiko

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
    interval = 1
    ssh_elapsed = 0

    print(f"testssh: verifying SSH to {ip}. Timeout: {retry_time}s")
    while True:
        try:
            ssh = openclient(ip, usr, pswd)
            break
        except:
##            print(f"testssh: Could not SSH to {ip}, waiting {interval}s...")
            ssh_elapsed += interval
            time.sleep(interval)

        # Could not connect within time limit
        if ssh_elapsed >= retry_time:
            print(f"testssh: Could not connect to {ip}. Timed out")
            sys.exit(1)

    # report on elapsed time 
    print(f"testssh: Connected to {ip}. SSH elapsed time = {ssh_elapsed}s")

    # Close SSH connection
    ssh.close()
    return ssh_elapsed

# VARS
ip = "192.168.0.111"
usr = "root"
pswd = "100yard-"
timeout = 300

#####################################
# MAIN
# ?is an elapsed timer needed around this call
ssh_et = testssh(ip, usr, pswd, timeout)

ssh_client = openclient(ip, usr, pswd)

# Issue reboot cmd. Closes ssh_client
# Don't test or capture return code
try:
    ssh_client.exec_command("reboot >/dev/null 2>&1")
except:
    print("reboot issue failed")
    sys.exit(1)

######################
# START the clock on total shutdown and reboot time
#
delay = 5
start_time = datetime.datetime.now()
print(f"SUT rebooted at: {start_time}")

# Need to block until shutdown is completed
time.sleep(delay)    # just a guess...

ssh_et = testssh(ip, usr, pswd, timeout)

# Reboot closed SSH client, so reopen as SUT boots
ssh_client = openclient(ip, usr, pswd)

# SSH is active, now wait for system up condition:
#     'systemctl list-jobs == No jobs running”
interval = 1     
sysctl_et = 0
rebooted = False

print(f"rebootsut: SUT {ip}, waiting for reboot to complete...")
while rebooted == False:
    # if cmd==True, then SUT has completed boot process
    cmd = "systemctl list-jobs | grep -q 'No jobs running'"
    cmd_str = cmd + " 2> \&1"
    stdin, stdout, stderr = ssh_client.exec_command(
            cmd_str, get_pty=True)
    # Block on completion of exec_command
    exit_status = stdout.channel.recv_exit_status()
    # Test for completed boot
    if exit_status == 0:
        rebooted = True
        continue
    else:
##        print(f"rebootsut: SUT {ip}, waiting {timeout}s for reboot...")
        sysctl_et += interval
        time.sleep(interval)

    # Test if exceeded time limit
    total_et = ssh_et + sysctl_et
    if total_et >= timeout:
        print(f"rebootsut: SUT {ip} reboot Timed out")
        ssh_client.close()
        sys.exit(1)

ssh_client.close()

# Print results
elapsed_time = datetime.datetime.now() - start_time
print(f"SUT {ip} reboot elapsed time: {elapsed_time}")
print("* sleep calculated interval times:")
print(f"  > SSH elapsed time {ssh_et}s")
print(f"  > SYSTEMCTL elapsed time {sysctl_et}s")
print(f"  > TOTAL elapsed time {total_et}s")
# END

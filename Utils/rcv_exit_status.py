# REPRODUCER for (suspected) Paramiko limitation:
# The largest output Paramiko can handle when recv_exit_status() is 
# called first is 2097152 bytes, which is exactly 2 MiB. Any larger
# than that and it hangs. 
# If I move recv_exit_status() to after the read(), Paramiko sails
# past that limit without issue.
# NOTE: with these version this issue is not observed
# 3.6.8 (default, Oct 19 2021, 05:14:06) 
# [GCC 8.5.0 20210514 (Red Hat 8.5.0-3)]
# 2.8.1   <-- paramiko version
##############################################################

import sys
import paramiko

print(sys.version)
print(paramiko.__version__)

client = paramiko.client.SSHClient()
##client.load_system_host_keys()
##client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(hostname='127.0.0.1', username="root", password="100yard-",
                port=22, timeout=2)
except Exception as _e:
    sys.stdout.write(str(_e))
    sys.exit(1)

output_len = 2097150

while True:
    stdin, stdout, stderr = client.exec_command(
        'printf %{}s'.format(output_len),
        get_pty=True)

    exit_status = stdout.channel.recv_exit_status()
    stdout_output = stdout.read().decode('utf8').rstrip('\n')

    print(len(stdout_output))
    output_len += 1


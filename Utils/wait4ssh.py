# function illustrates method to wait for SSH, using stopwatch
import paramiko
import time

def wait_for_ssh_to_be_ready(host, port, timeout, retry_interval):
    # cast vars
    timeout = int(timeout)
    retry_interval = float(retry_interval)

    # init paramiko
    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Start stopwatch
    timeout_start = time.time()

    while time.time() < timeout_start + timeout:
        try:
##            client.connect(host, int(port), allow_agent=False,
##                look_for_keys=False)
            client.connect(host, int(port))

        except paramiko.ssh_exception.SSHException as e:
            # socket is open, but not SSH service responded
            if e.message == 'Error reading SSH protocol banner':
                print(e)
                continue
            print('SSH transport is available!')
            break

        except paramiko.ssh_exception.NoValidConnectionsError as e:
            print('SSH transport is not ready...')
            continue
        # sleep
        time.sleep(retry_interval)

# MAIN
wait_for_ssh_to_be_ready('192.168.0.108', '22', '30', '2')

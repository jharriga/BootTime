# extract key/value pairs from Neptune Startup Timings

import re

stats = """Jan 13 16:29:11 localhost.localdomain neptune3-ui.desktop[1049]: == STARTUP TIMING REPORT: System UI ==
Jan 13 16:29:11 localhost.localdomain neptune3-ui.desktop[1049]: 2'761.715 after application constructor             #########################
Jan 13 16:29:11 localhost.localdomain neptune3-ui.desktop[1049]: 2'952.041 after logging setup                       ###########################
Jan 13 16:29:11 localhost.localdomain neptune3-ui.desktop[1049]: 3'412.278 after startup-plugin load                 ###############################
Jan 13 16:29:11 localhost.localdomain neptune3-ui.desktop[1049]: 3'452.572 after runtime registration                ###############################
Jan 13 16:29:11 localhost.localdomain neptune3-ui.desktop[1049]: 3'712.037 after package database loading            ##################################
Jan 13 16:29:11 localhost.localdomain neptune3-ui.desktop[1049]: 3'717.459 after ApplicationManager instantiation    ##################################
Jan 13 16:29:11 localhost.localdomain neptune3-ui.desktop[1049]: 3'717.525 after NotificationManager instantiation   ##################################
Jan 13 16:29:11 localhost.localdomain neptune3-ui.desktop[1049]: 3'717.601 after ApplicationIPCManager instantiation ##################################
Jan 13 16:29:11 localhost.localdomain neptune3-ui.desktop[1049]: 3'742.183 after IntentServer instantiation          ##################################
Jan 13 16:29:11 localhost.localdomain neptune3-ui.desktop[1049]: 3'757.432 after package registration                ##################################
Jan 13 16:29:11 localhost.localdomain neptune3-ui.desktop[1049]: 3'757.967 after installer setup checks              ##################################
Jan 13 16:29:11 localhost.localdomain neptune3-ui.desktop[1049]: 3'770.254 after installer setup                     ##################################
Jan 13 16:29:11 localhost.localdomain neptune3-ui.desktop[1049]: 3'770.593 after QML registrations                   ##################################
Jan 13 16:29:11 localhost.localdomain neptune3-ui.desktop[1049]: 3'780.145 after QML engine instantiation            ##################################
Jan 13 16:29:11 localhost.localdomain neptune3-ui.desktop[1049]: 4'137.034 after starting session D-Bus              ######################################
Jan 13 16:29:11 localhost.localdomain neptune3-ui.desktop[1049]: 6'323.408 after loading main QML file               #########################################################
Jan 13 16:29:11 localhost.localdomain neptune3-ui.desktop[1049]: 6'323.434 after Window instantiation/setup          #########################################################
Jan 13 16:29:11 localhost.localdomain neptune3-ui.desktop[1049]: 6'323.451 after window show                         #########################################################
Jan 13 16:29:11 localhost.localdomain neptune3-ui.desktop[1049]: 6'696.031 after first frame drawn                   #############################################################
Jan 13 16:29:13 localhost.localdomain dbus-broker-lau[1293]: Ready
"""

# VARS
# list of key metric search strings = dict keys
km_list = [
    "after logging setup",
    "after starting session D-Bus",
    "after first frame drawn"
]
#-----------------------------------------
# MAIN

#    stats = "journalctl | grep -m1 -A20 'STARTUP TIMING REPORT: System UI'"
#    # redirect stderr to stdout
#    cmd_str = cmd + " 2> \&1"
#    stdin, stdout, stderr = client.exec_command(cmd_str, get_pty=True)
#    # Block on completion of exec_command
#    exit_status = stdout.channel.recv_exit_status()

# For this testcode, 'stdout' contents are in var 'stats'

# Parse neptune stats and create dict
dict = {}
stat_lines = stats.splitlines()

# Now add values to the dict
for str in (stat_lines):
    for key_metric in km_list:
        if key_metric in str:    
            # key_metric found in str, extract key/value
            rstrip1 = str.rstrip('#')
            rstrip2 = rstrip1.rstrip()
            splitted = rstrip2.split(':')
            result = splitted[3].lstrip()
            keymsg = re.search(key_metric, result)
            value = result.split(' ')
##            print("key: ", keymsg.group(), "  value: ", value[0])
            dict[keymsg.group()] = value[0]

print("Neptune Startup Timing Stats:")
print(dict)
# END

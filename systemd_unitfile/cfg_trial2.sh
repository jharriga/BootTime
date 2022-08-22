#!/bin/bash
# TRIAL2

###---
MYAPP=/bin/myapp

if [ -f "$MYAPP" ]; then
    echo "$MYAPP already exists. Exiting"
    echo "Please run cfg_reset.sh"
    exit 1
fi

# Create MYAPP executable
cat <<EOF1 > "$MYAPP"
#!/bin/sh

echo "myapp -  $(date +%s.%N)" | tee /dev/kmsg /dev/console
EOF1

###---
UNITFILE=/etc/systemd/system/myapp.service

if [ -f "$UNITFILE" ]; then
    echo "Unit file already exists. Exiting"
    echo "Please run cfg_reset.sh"
    exit 1
fi

# Create unitfile
cat <<EOF2 > "$UNITFILE"
[Unit]
Description=my application
DefaultDependencies=no

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/bin/myapp

[Install]
WantedBy=application.target
EOF2

# Verify
ls -l /bin/myapp
systemctl daemon-reload
systemctl cat myapp.service

echo "To see the impact: manually reboot SUT, then run tar_results.sh"

exit 0

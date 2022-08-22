#!/bin/bash
# TRIAL1

###---
MYAPP=/bin/myapp

if [ -f "$MYAPP" ]; then
    echo "$MYAPP already exists. Exiting"
    echo "Please run cfg_reset.sh"
    exit 1
fi

# Create MYAPP executable
# NOTE: specify 'EOF1' to suppress param substitution
cat <<'EOF1' > "$MYAPP"
#!/bin/sh

echo "myapp -  $(date +%s.%N)" | tee /dev/kmsg /dev/console
EOF1

chmod 755 /bin/myapp

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

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/bin/myapp

[Install]
WantedBy=application.target
EOF2

###---
TGTFILE=/etc/systemd/system/application.target

if [ -f "$TGTFILE" ]; then
    echo "Target file already exists. Exiting"
    echo "Please run cfg_reset.sh"
    exit 1
fi

# Create targetfile
cat <<EOF3 > "$TGTFILE"
[Unit]
Description=Main Application Suite

[Install]
WantedBy=default.target
EOF3

###----
# Enable
systemctl enable myapp
systemctl enable application.target

# Verify
ls -l /bin/myapp
systemctl daemon-reload
systemctl cat myapp.service

echo "To see the impact: manually reboot SUT, then run tar_results.sh"

exit 0

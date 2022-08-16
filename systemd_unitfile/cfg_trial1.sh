#!/bin/bash
# TRIAL1

UNITFILE=/etc/systemd/system/myapp.service

if [ -f "$UNITFILE" ]; then
    echo "Unit file already exists. Exiting"
    echo "Please remove ${UNITFILE} and ${UNITFILE}.d/"
    exit 1
fi

# Create unitfile
cat <<EOF > "$UNITFILE"
[Unit]
Description=my application

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/bin/myapp

[Install]
WantedBy=application.target
EOF

# Verify
systemctl daemon-reload
systemctl cat myapp.service

echo "now manually reboot SUT, then run tar_results.sh"

exit 0

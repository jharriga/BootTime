#!/bin/bash
# RESET

UNITFILE=/etc/systemd/system/myapp.service
UNITDIR=/etc/systemd/system/myapp.service.d

if [ -f "$UNITFILE" ] || [ -d "$UNITDIR" ]; then
    echo "Unit file already exists."
    while true; do
        read -p "Remove (y/n): " response
	case $response in
	    [Yy]* ) rm -f $UNITFILE; rm -rf $UNITDIR; break;;
	    [Nn]* ) echo "exiting"; exit;;
	    * ) echo "Please answer yes or no";;
        esac
    done
else
    echo "Unit file not found, exiting"
    exit 1
fi

# Verify
systemctl daemon-reload
systemctl cat myapp.service
echo "Previous cmd should have returned: No files found for myapp.service"

echo "To see the impact: manually reboot SUT, then run tar_results.sh"

exit 0

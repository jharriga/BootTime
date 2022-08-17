#!/bin/bash
# Produces boot timing artifacts for most recent boot

# Prompt user for (prepended) filename label
echo "Enter the test results label name: "
read label

if ls "$label"* 1> /dev/null 2>&1; then
    echo "Please choose a unique label - exiting"
    exit 1
fi

# Get current date-time
curr_ts=$(date "+%Y.%m.%d-%H.%M.%S")

# Create list of results filenames
DMESG="${label}.dmesg"
TIME="${label}.satime"
DOT="${label}.sadot"
PLOT="${label}-saplot.svg"
ALLRESULTS="$DMESG $TIME $DOT $PLOT"
TARBALL="${label}.${curr_ts}.tar"

# Record 'dmesg' results
dmesg | grep -m1 -i "myapp" > "$DMESG"

# Record ‘systemd-analyze time’ results
systemd-analyze time > "$TIME"

# Create ‘systemd-analyze dot’ graph
echo "producing DOT"
systemd-analyze dot myapp.service > "$DOT"

# Create ‘systemd-analyze plot’ results
echo "producing PLOT"
systemd-analyze plot > "$PLOT"

# Package results into tarball (verbosely)
echo "creating TARBALL with results files"
tar -cvf $TARBALL $ALLRESULTS

if [ -f $TARBALL ]; then
	echo "SUCCESS: Created $TARBALL"
	echo "Cleaning up results files"
	rm -f $ALLRESULTS
else
	echo "FAILURE: $TARBALL not created"
	echo "Did not cleanup results files"
fi

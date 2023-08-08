Contains script related to initramfs boot timings
* initramfs.py - modified version of sut_boottest.py   Executes 'initramfsResults.sh' on SUT
* stats.py - reads JSON results and provides variances across multiple run results
* initramfsResults.sh - queries kernel msg buffer for 'markers' and records to logfile
* clktickResults.sh - extends initramfsResults.sh to incorporate clkTick markers 
* awkLogfiles.sh - reads logfiles, parses time values an echos to stdout for pasting into spreadsheet


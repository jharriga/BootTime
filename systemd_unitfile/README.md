
# Scripts to assist with automating systemd-unitfile impact on custom boot service timings

# USAGE	← suggest performing three runs

Reset the SUT and gather results
* sut# ./cfg_reset.sh
* REBOOT
* sut# ./tar_results.sh

Run trial1 - adds ‘/bin/myapp’ and ‘myapp’ unit file
* sut# ./cfg_trial1.sh
* REBOOT
* sut# ./tar_results.sh
* sut# ./cfg_reset.sh

Run trial2 -  adds ‘/bin/myapp’ and ‘myapp’ unit file with ‘DefaultDependencies=no’ 
* sut# ./cfg_trial2.sh
* REBOOT
* sut# ./tar_results.sh
* sut# ./cfg_reset.sh

Then copy the three tarballs back to your system and analyze results
* $ scp root@<sut-ip>:/home/BootTime/systemd_unitfile/*.tar .

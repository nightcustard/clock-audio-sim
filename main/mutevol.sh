#!/bin/bash
# Used with i2c audio interface
service clocksim stop || echo 'clocksim service is not running'
killall -9 aplay || 'aplay was not running'
amixer -M sset PCM,0 0%,0% # mute
/usr/sbin/alsactl store 
service clocksim start || echo 'error starting clocksim service'  # restart clocksim service


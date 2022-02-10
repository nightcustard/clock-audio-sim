#!/bin/bash
# volume level parameters passed from crontab.  aplay has to be killed as 'amixer' won't run if it's still active.
# Used with i2c audio interface
service clocksim stop || echo 'clocksim service is not running'
killall -9 aplay || 'aplay was not running'
amixer -M sset PCM,0 $1%,$2%  # unmute
/usr/sbin/alsactl store 
service clocksim start || echo 'error starting clocksim service'




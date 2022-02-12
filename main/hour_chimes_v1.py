#!/usr/bin/python3
# hour_chimes_v1.py
# March 2021 Nightcustard Enterprises

# This code is called by user crontab on the hour and plays a recordings of hour chimes, selecting the correct recording using datetime

import subprocess, os
from datetime import datetime
# import pytz # timezone awareness - not currently used in this programme.

# chimes tuple (index 0 to 11)
chimes = ('/home/pi/audio/1.mp3', '/home/pi/audio/2.mp3', '/home/pi/audio/3.mp3', '/home/pi/audio/4.mp3', '/home/pi/audio/5.mp3', '/home/pi/audio/6.mp3', '/home/pi/audio/7.mp3', '/home/pi/audio/8.mp3', '/home/pi/audio/9.mp3', '/home/pi/audio/10.mp3', '/home/pi/audio/11.mp3', '/home/pi/audio/12.mp3')

master, slave = os.openpty() #  used to open a new pseudo-terminal pair. This method returns a pair of file descriptor (master and slave) for the pty and the tty
time = datetime.now()
hour = time.hour
if hour == 0: # chimes correspond to a 12hr cycle - these lines convert 24hr time to 12hr time
	hour = 12
if hour > 12:
	hour = hour-12
print (chimes[hour-1]) # the tuple above is indexed 0 to 11 rather than 1 to 12, so you have to subtract 1 from the hour.
p = subprocess.Popen(['mpg123', chimes[hour-1]], stdin=master) # play the appropriate audio file for the hour
exit()

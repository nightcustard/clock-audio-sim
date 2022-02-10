#!/usr/bin/python3
# quarter_chimes_v1.py
# March 2021 Nightcustard Enterprises

# This code is called by user crontab on the quarter hour and plays a recordings of quarter chimes, selecting the correct recording using datetime

import subprocess, os
from datetime import datetime
import pytz # timezone awareness

# chimes tuple (indexed 0 to 2)
chimes = ('/home/pi/audio/15.mp3', '/home/pi/audio/30.mp3', '/home/pi/audio/45.mp3')

master, slave = os.openpty() #  used to open a new pseudo-terminal pair. This method returns a pair of file descriptor (master and slave) for the pty and the tty
time = datetime.now()
minute = time.minute
if minute == 15: # Select correct audio file from the tuple above for the appropriate quarter hour
	quarter = 0
elif minute == 30:
	quarter = 1
elif minute == 45:
	quarter = 2

else:
	quarter = 9
	print(minute, quarter)
	exit()
	
print (chimes[quarter])
p = subprocess.Popen(['mpg123', chimes[quarter]], stdin=master) # play appropriate audio file
exit()

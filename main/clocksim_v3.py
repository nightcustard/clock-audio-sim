#!/usr/bin/python3
# clocksim_v3.py
# March 2021 Nightcustard Enterprises

# This code waits for a switch to be made on GPIO 17 to start grandfather clock ticks.  It keeps on playing until the switch contact is broken.   
# A switch on GPIO 23 turns quarterly chimes on & off and one on GPIO 24 does likewise for hour chimes. Both these are run from cron and activated/deactivated via python-crontab. 
# The programme is run as a service ('clocksim_v3').
# Volume is muted in the evening and set to 50% in the morning via crontab -e 
#(ie)
# Unmutes Adafruit i2s sound card: a bash script is required as 'amixer' run in cron writes the wrong volume values (for some reason)
# 59 6 * * * /bin/bash /home/pi/software/setvol.sh && sudo /bin/bash alsactl store
# Mutes sound card
#  1 23 * * * /bin/bash /home/pi/software/mutevol.sh && sudo /bin/bash alsactl store
#
# Reboot pi daily to reduce chances of wifi-connected pi 'disappearing' from the network
# 50 1 * * * sudo reboot # reboot pi daily at 01:50
#
# 
# Edit 7/3/21: Added GPIO 25 monitoring to perform Pi shutdown via push button.
# The Pi is set up to show a 'heartbeat' when normally operating to make it easier to see when it's been shut down (or has failed in some way) - added 'dtparam=act_led_trigger=heartbeat' to /boot/config.txt
# The audio is output via and Adafruit i2s stereo decoder UDA1334A.  This uses GPIO pins 12 (GPIO 18), 35 (GPIO 19) & 40 (GPIO 21) plus power
# Edit 21/03/21: Added 'Going for shutdown' and 'Rebooting' audio prompts

import RPi.GPIO as GPIO
from crontab import CronTab
import os, pty, subprocess, time, sys, datetime

GPIO.setmode(GPIO.BCM)  # channel numbers, not pins
GPIO.setwarnings(False)
GPIO.setup(17, GPIO.IN, pull_up_down = GPIO.PUD_UP) # Tick switch input pin 11
GPIO.setup(23,GPIO.IN, pull_up_down = GPIO.PUD_UP)  # Quarterly chime switch input pin 16
GPIO.setup(24,GPIO.IN, pull_up_down = GPIO.PUD_UP)  # Hourly chime switch input on pin 18
GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP)   # Shutdown push button on pin 22
GPIO.add_event_detect(17,GPIO.FALLING) # Add falling edge event detection. Used with 'GPIO.event.detected(channel)'
GPIO.add_event_detect(23,GPIO.FALLING)
GPIO.add_event_detect(24,GPIO.FALLING)
GPIO.add_event_detect(25,GPIO.FALLING)

cron = CronTab(user='pi')

def cronwrite(chimeH, chimeQ):  # edits cron to enable or disable quarterly and/or hourly chimes
	if chimeH != 3: cron.remove_all(comment='hour_chimes') #deletes jobs with matching comments to prevent multiple lines being generated
	if chimeQ != 3: cron.remove_all(comment='quarter_chimes') #deletes jobs with matching comments to prevent multiple lines being generated
	#cron.write()
	if chimeH == 0:
		job = cron.new(command='/usr/bin/python3 /home/pi/software/hour_chimes_v1.py', comment='hour_chimes')
		#job.hour.on(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23)  # Uncomment this line to omit hours as required.
		job.minute.on(0)
	if chimeQ == 0:
		job = cron.new(command='/usr/bin/python3 /home/pi/software/quarter_chimes_v1.py', comment='quarter_chimes')
		#job.hour.on (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23) # Uncomment this line to specify hours for quarter chimes.
		job.minute.on(15, 30, 45)
	#print('Writing cron', 'chimeH = ', chimeH, 'chimeQ = ', chimeQ)
	for item in cron:
		print (item)
	cron.write()  #writes new user crontab
	return

def shut_down(N):
	GPIO.cleanup() # Cleanup all GPIO
	if N == 0: 
		playmusic('reboot')
		os.system('sudo reboot') # Reboot the Pi
	if N == 1:
		playmusic('shutdown')
		os.system('sudo shutdown -h now') # Shut down the Pi
	exit()

def main():
	if sys.stdout.isatty(): os.system('clear') # only carried out if script launched from a terminal
	global master, slave 
	player_status = 0 # '0' if ticks not active, '1' if they are
	if sys.stdout.isatty(): print('Running main prog')
	master, slave = os.openpty() #  used to open a new pseudo-terminal pair. This method returns a pair of file descriptor (master and slave) for the pty and the tty
	# Detect programme start-up switch positions (GPIO input is high if switch is open, low when closed):
	if GPIO.input(23): chimeQ = 1  #cronwrite('hourly', 'off') # Quarterly chimes switch 'off'
	if not GPIO.input(23): chimeQ = 0  #cronwrite('hourly', 'on') # Quarterly chimes switch 'on'
	if GPIO.input(24): chimeH = 1 #cronwrite('quarterly', 'off') # Hourly chimes switch 'off'
	if not GPIO.input(24): chimeH = 0 #cronwrite('quarterly', 'on') # Hourly chimes switch 'on'
	ChimeQ = chimeQ # ChimeH & ChimeQ are status
	ChimeH = chimeH
	cronwrite(chimeH, chimeQ)
	
	if not GPIO.input(17): # Ticks switch 'on'
		player_status = 1
		print('Beginning ticks')
		playmusic('play')
	try:
		while True:
			#print('in loop')
			#print('\nGPIO input = ', GPIO.input(17), 'player_status = ', player_status, end='\033[F', flush=True)
			#print('GPIO 17 input = ', not GPIO.input(17), 'player_status = ', player_status, 'GPIO 23 input (Q) = ', not GPIO.input(23), 'GPIO 24 input (H) = ', not GPIO.input(24), flush=True)
			if GPIO.event_detected(17) and player_status == 0: # Ticks are switched on and player isn't playing
				player_status = 1
				print('Starting ticks')
				playmusic('play')
				time.sleep(5)
			elif GPIO.input(17) and player_status == 1: # ie HIGH - Tick switch is open and the player is playing
				time.sleep(1)
				player_status = 0
				print('Stopping ticks')
				playmusic('stop')
			if ChimeQ != GPIO.input(23):
				if GPIO.input(23): cronwrite (3, 1) # Quarterly chimes switch 'off'
				if not GPIO.input(23): cronwrite (3, 0) # Quarterly chimes switch 'on'
				ChimeQ = GPIO.input(23)
				print('ChimeQ = ', ChimeQ)
			if ChimeH != GPIO.input(24):
				if GPIO.input(24): cronwrite (1, 3) # Hourly chimes switch 'off'
				if not GPIO.input(24): cronwrite (0, 3) # Hourly chimes switch 'on'
				ChimeH = GPIO.input(24)
				print('ChimeH = ', ChimeH)
			if GPIO.event_detected(25):  # Shutdown button has been pressed
				print('shutdown/reboot button press detected, checking for short (reboot) or long (shutdown) press')
				time.sleep(1)
				if GPIO.input(25): shut_down(0) # Input is now HIGH, button is no longer pressed (or a glitch): interpet as reboot command
				else: shut_down(1) # input is still LOW (ie) button still pressed (or not a glitch): shut the pi down
			time.sleep(3)
	except KeyboardInterrupt:
		shut_down(2) # tidy up GPIO and exit to shell	

def playmusic(cmd): # https://stackoverflow.com/questions/42877375/pausing-mpg123-through-subprocess-in-python
	if cmd == 'play':
		print('Ticks active')
		p = subprocess.Popen(['mpg123', '--loop', '-1', '/home/pi/audio/GrandfatherClockTick_32mins.mp3'], stdin=master) # plays 'GrandfatherClockTick_32mins.mp3' in a loop until stopped by switch change or shutdown.
	elif cmd == 'reboot':
		p = subprocess.Popen(['mpg123', '--loop', '-1', '/home/pi/audio/Rebooting.mp3'], stdin=master)
		time.sleep(5) # Allow time for the file to play
	elif cmd == 'shutdown':
		p = subprocess.Popen(['mpg123', '--loop', '-1', '/home/pi/audio/GoingForShutdown.mp3'], stdin=master)
		time.sleep(5)
	elif cmd == 'stop':
		print('Ticks deactivated, switch open')
		os.write(slave, b'q') # quit playback
	return()

if __name__=="__main__":
	main()

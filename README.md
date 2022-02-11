# clock-audio-sim

Uses mpg123 to play recordings of grandfather clock ticks (as a service)
and uses user crontab to play recordings of chimes on the hours and at the quarter hours.

The clocksim service starts automatically on boot.
To check its status: 'sudo service clocksim status' (no apostrophes)
To restart the clocksim service (after an edit, for example): 'sudo service clocksim restart' (ditto)

Type: 'alsamixer' (without the apostrophes) at the command prompt and use the keyboard up/down arrow keys to raise or lower the volume.
This volume setting only temporary as the automatic muting mentioned below resets the values.  Once you're happy with the sound
level, follow the steps below to bake the changes in.

Sound is automatically muted at 23:01 and set to 50% at 06:59 using user crontab - use 'crontab -e' (no apostrophes)
to edit times; Edit using  'nano /home/pi/software/setvol.sh' to change the volume level from 50%.

The pi is rebooted every morning at 01:55 to attempt to mitigate loss of response on WiFi, also via crontab.  This should
be completely transparent to the user.  This is a problem local to the author and probably won't be necessary elsewhere.

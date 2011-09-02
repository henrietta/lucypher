#! /usr/bin/python
# coding=UTF-8
# (c) by Piotr Maślanka 2011, all rights reserved

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

CONF_LOG_FILE = 'C:\ups.txt'
CONF_SERIAL_PORT = 0
CONF_TIME_TO_SHUTDOWN = 10*60		# 10 minutes

CONF_QUERY_SECONDS = 1		# will query each x seconds
							# modify only if you know what you're doing
import sys
import os
import serial		# needs pySerial
from time import sleep
from datetime import datetime, timedelta

IS_WINDOWS = (sys.platform[:3] == 'win')

if not IS_WINDOWS:		# Daemonize the process, do not do it if we are running under Windows
	try:
		pid = os.fork()
		if pid > 0: sys.exit(0)
	except OSError: sys.exit(1)

	os.chdir("/")
	os.setsid()
	os.umask(0)

	try:
		pid = os.fork()
		if pid > 0: sys.exit(0)
	except OSError: sys.exit(1)

def log(s):
	with open(CONF_LOG_FILE, 'ab') as f:
		f.write(str(datetime.now())+": "+s)
		if IS_WINDOWS:
			f.write('\r\n')
		else:
			f.write('\n')
	
try:	
	ser = serial.Serial(CONF_SERIAL_PORT)
except:
	log('Cannot open serial port '+str(CONF_SERIAL_PORT)+', quitting');
	sys.exit(1)
	
power_went_down_on = None	
while True:
	supply_on = ser.getCTS()
	
	if (not supply_on) and (power_went_down_on == None):
		power_went_down_on = datetime.now()
		log('Power went down')
	elif not supply_on:
		if datetime.now() >= (power_went_down_on + timedelta(0, CONF_TIME_TO_SHUTDOWN)):
			log('Shutting down')
			if IS_WINDOWS:
				os.system('shutdown -s -t 1')
			else:
				os.system('shutdown -h now')
	elif (supply_on) and (power_went_down_on != None):
		log('Power restored')
		power_went_down_on = None
		
	sleep(CONF_QUERY_SECONDS)
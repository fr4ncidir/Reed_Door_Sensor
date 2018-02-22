#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  reed_monitor.py
#  
#  Copyright 2018 Francesco Antoniazzi <francesco.antoniazzi1991@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

import sys,serial,logging
import smtplib
from datetime import datetime
from email.message import EmailMessage

logging.basicConfig(format="%(levelname)s %(asctime)-15s %(message)s",level=logging.DEBUG)
identifier = "123456789"

TS_format = "{:%Y-%m-%d %H:%M:%S.%f}"

def handle_open_door(timestamp):
	msg = EmailMessage()
	msg.set_content("""
{} - Door opened at {} -

auto-generated mail: do not reply
	""".format(identifier,timestamp))
	msg["Subject"] = "Door monitoring system - Door opening"
	msg["From"] = "origin@gmail.com"
	msg["To"] = "sgsi-alarms@lists.infn.it"
	s = smtplib.SMTP("postino.cnaf.infn.it")
	s.send_message(msg)
	s.quit()
	
def handle_closed_door(timestamp):
	msg = EmailMessage()
	msg.set_content("""
{} - Door closed at {} -

auto-generated mail: do not reply
	""".format(identifier,timestamp))
	msg["Subject"] = "Door monitoring system - Door closing"
	msg["From"] = "origin@gmail.com"
	msg["To"] = "destination@gmail.com"
	s = smtplib.SMTP("smtp.server.address.com")
	s.send_message(msg)
	s.quit()
	
def handle_system_failure(timestamp,error_str):
	msg = EmailMessage()
	msg.set_content("""
{} - Door monitoring system failure at {} -
{}

auto-generated mail: do not reply
	""".format(identifier,timestamp,error_str))
	msg["Subject"] = "Door monitoring system failure"
	msg["From"] = "origin@gmail.com"
	msg["To"] = "destination@gmail.com"
	s = smtplib.SMTP("smtp.server.address.com")
	s.send_message(msg)
	s.quit()

def main(args):
	try:
		ser = serial.Serial(port="COM13",baudrate=9600,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=4)
		while True:
			line = ser.read(4).decode("cp1252")
			if len(line)<4:
				print("Timeout Reached")
			else:
				str_timestamp = TS_format.format(datetime.now())
				if line=="-CO-":
					logging.warning("{} --- THE DOOR WAS OPENED".format(str_timestamp))
					handle_open_door(str_timestamp)
				elif line=="+OC+":
					logging.warning("{} --- THE DOOR WAS CLOSED".format(str_timestamp))
					handle_closed_door(str_timestamp)
				elif line=="*UP*":
					logging.info("Device is up and running")
				else:
					raise serial.SerialException("Unknown packet {}".format(line))
	except Exception:
		error_str = "Exception: {}".format(sys.exc_info()[1])
		logging.error(error_str)
		handle_system_failure(TS_format.format(datetime.utcnow()),error_str)
	return 0

if __name__ == '__main__':
	sys.exit(main(sys.argv))

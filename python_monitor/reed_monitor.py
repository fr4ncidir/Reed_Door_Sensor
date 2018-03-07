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
from hashlib import md5
from datetime import datetime
from logging import handlers,Formatter
from uuid import getnode

logging.basicConfig(format="%(levelname)s %(asctime)-15s %(message)s",level=logging.DEBUG)

monitorLog = logging.getLogger("monitorLog")
handle_monitorLog = logging.handlers.SysLogHandler(address="/dev/log")
handle_monitorLog.setFormatter(logging.Formatter())
monitorLog.addHandler(handle_monitorLog)

plainLog = logging.getLogger("plainLog")
identifier = md5(hex(getnode()).encode()).hexdigest()

TS_format = "{:%Y-%m-%d %H:%M:%S.%f}"

e_msg = {
    "From":"",
    "To":""
    }

def handle_open_door(timestamp):
    e_msg["email"] = """
{} - Door opened at {} -

auto-generated mail: do not reply
""".format(identifier,timestamp)
    e_msg["Subject"] = "Door monitoring system - Door opening"
    plainLog.warning(e_msg["email"])
    monitorLog.warning("HANDLER: {} {}".format(e_msg["Subject"],identifier))
    #msg["From"] = "origin@gmail.com"
    #msg["To"] = "sgsi-alarms@lists.infn.it"
    #s = smtplib.SMTP("postino.cnaf.infn.it")
    #s.send_message(msg)
    #s.quit()

def handle_closed_door(timestamp):
    e_msg["email"] = """
{} - Door closed at {} -

auto-generated mail: do not reply
    """.format(identifier,timestamp)
    e_msg["Subject"] = "Door monitoring system - Door closing"
    plainLog.warning(e_msg["email"])
    monitorLog.warning("HANDLER: {} {}".format(e_msg["Subject"],identifier))
    #msg["From"] = "origin@gmail.com"
    #msg["To"] = "destination@gmail.com"
    #s = smtplib.SMTP("smtp.server.address.com")
    #s.send_message(msg)
    #s.quit()
	
def handle_system_failure(timestamp,error_str):
    e_msg["email"] = """
{} - Door monitoring system failure at {} -
{}

auto-generated mail: do not reply
    """.format(identifier,timestamp,error_str)
    e_msg["Subject"] = "Door monitoring system failure"
    plainLog.warning(e_msg["email"])
    monitorLog.warning("HANDLER: {} {}".format(e_msg["Subject"],identifier))
    #msg["From"] = "origin@gmail.com"
    #msg["To"] = "destination@gmail.com"
    #s = smtplib.SMTP("smtp.server.address.com")
    #s.send_message(msg)
    #s.quit()

def main(args):
    plainLog.warning("{} reed_monitor.py successfully started".format(identifier))
    monitorLog.warning("{} reed_monitor.py successfully started".format(identifier))
    try:
        ser = serial.Serial(port="/dev/ttyUSB0",baudrate=9600,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=4)
        while True:
            line = ser.read(4).decode("cp1252")
            str_timestamp = TS_format.format(datetime.now())
            if len(line)<4:
                plainLog.critical("{} Timeout Reached".format(identifier))
                monitorLog.critical("{} Timeout Reached".format(identifier))
                handle_system_failure(str_timestamp,"Reading timeout Reached")
                raise serial.SerialException("Reading timeout Reached")
            else:
                if line=="-CO-":
                    plainLog.warning("{} {}--- THE DOOR WAS OPENED".format(str_timestamp,identifier))
                    monitorLog.warning("{} {}--- THE DOOR WAS OPENED".format(str_timestamp,identifier))
                    handle_open_door(str_timestamp)
                elif line=="+OC+":
                    plainLog.warning("{} {}--- THE DOOR WAS CLOSED".format(str_timestamp,identifier))
                    monitorLog.warning("{} {}--- THE DOOR WAS CLOSED".format(str_timestamp,identifier))
                    handle_closed_door(str_timestamp)
                elif line=="*UP*":
                    plainLog.info("{} Device is up and running".format(identifier))
                    monitorLog.info("{} Device is up and running".format(identifier))
                else:
                    handle_system_failure(str_timestamp,"{} Unknown packet {}".format(identifier,line))
                    raise serial.SerialException("{} Unknown packet {}".format(identifier,line))
    except Exception:
        error_str = "{} EXCEPTION: {}".format(identifier,sys.exc_info()[1])
        plainLog.error(error_str)
        monitorLog.error(error_str)
        handle_system_failure(TS_format.format(datetime.utcnow()),error_str)
    plainLog.warning("{} reed_monitor.py stopped working".format(identifier))
    monitorLog.warning("{} reed_monitor.py stopped working".format(identifier))
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))

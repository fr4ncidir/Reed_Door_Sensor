#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  reed_monitor_debian.py
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

import sys
import logging
import serial
from datetime import datetime
from hashlib import md5
from uuid import getnode

logging.basicConfig(format="%(levelname)s %(asctime)-15s %(message)s", level=logging.DEBUG)
doorLog = logging.getLogger("DoorLog")

TS_format = "{:%Y-%m-%d %H:%M:%S.%f}"
identifier = md5(hex(getnode()).encode()).hexdigest()


def handle_door_event(notification):
    doorLog.message(notification)
    # TODO creazione delle e-mail


def main_service(serial_port):
    import sdnotify
    from logging import handlers, Formatter

    n = sdnotify.SystemdNotifier()
    n.notify("READY=1")

    handle_doorLog = logging.handlers.SysLogHandler(address="/dev/log")
    handle_doorLog.setFormatter(logging.Formatter())
    doorLog.addHandler(handle_doorLog)

    try:
        ser = serial.Serial(port=serial_port, baudrate=9600,
                            parity=serial.PARITY_NONE,
                            stopbits=serial.STOPBITS_ONE,
                            bytesize=serial.EIGHTBITS, timeout=4)
    except:
        doorLog.critical("id={} - exception={}".format(identifier, sys.exc_info()[1]))
        n.notify("STATUS=exception while opening serial port")
        n.notify("STOPPING=1")
        return 1

    n.notify("STATUS=successfully opened serial port")
    previous = "S"
    exception_counter = 0
    while True:
        timestamp = TS_format.format(datetime.now())

        try:
            character = ser.read(1).decode("utf-8")
        except:
            doorLog.critical("id={} - exception={}".format(identifier, sys.exc_info()[1]))
            exception_counter += 1
            if exception_counter <= 5:
                n.notify("STATUS={} #{}".format(sys.exc_info()[1], exception_counter))
                continue
            else:
                n.notify("STATUS=exception while reading serial port")
                n.notify("STOPPING=1")
                ser.close()
                return 1

        exception_counter = 0
        if character == "U":
            n.notify("STATUS=up and running")
            if previous != character:
                doorLog.info("Reed door monitor on device {} is up and running".format(identifier))
        elif character == "O":
            notification = "Door opened at {}".format(timestamp)
            n.notify("STATUS={}".format(notification))
            if previous != character:
                doorLog.warning(notification)
                handle_door_event(notification)
        elif character == "C":
            notification = "Door closed at {}".format(timestamp)
            n.notify("STATUS={}".format(notification))
            if previous != character:
                doorLog.warning(notification)
                handle_door_event(notification)
        else:
            doorLog.error("Read unknown '{}' from serial port".format(character))
            n.notify("STATUS=Read unknown '{}' from serial port".format(character))
        previous = character

    n.notify("STOPPING=1")
    ser.close()
    return 0


def main_on_request(serial_port):
    try:
        ser = serial.Serial(port=serial_port, baudrate=9600,
                            parity=serial.PARITY_NONE,
                            stopbits=serial.STOPBITS_ONE,
                            bytesize=serial.EIGHTBITS, timeout=4)
    except:
        doorLog.critical("id={} - exception={}".format(identifier, sys.exc_info()[1]))
        return 1

    previous = "S"
    while True:
        timestamp = TS_format.format(datetime.now())

        try:
            character = ser.read(1).decode("utf-8")
        except KeyboardInterrupt:
            doorLog.info("Keyboard interrupt!")
            ser.close()
            return 0
        except:
            doorLog.critical("id={} - exception={}".format(identifier, sys.exc_info()[1]))
            ser.close()
            return 1

        if character == "U":
            if previous != character:
                doorLog.info("Reed door monitor on device {} is up and running".format(identifier))
        elif character == "O":
            notification = "Door opened at {}".format(timestamp)
            doorLog.warning(notification)
        elif character == "C":
            notification = "Door closed at {}".format(timestamp)
            doorLog.warning(notification)
        else:
            doorLog.error("Read unknown '{}' from serial port".format(character))
        previous = character

    ser.close()
    return 0


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Debian reed door sensor monitor")
    parser.add_argument("run-mode", choices=["service", "on-request"],
                        help="identifies if the script runs as standalone or systemd service")
    parser.add_argument("--sp", nargs="?", default="/dev/ttyACM0",
                        const="/dev/ttyACM0",
                        help="address in /dev of the device port")
    args = vars(parser.parse_args())

    if args["run-mode"] == "service":
        sys.exit(main_service(args["sp"]))
    else:
        sys.exit(main_on_request(args["sp"]))

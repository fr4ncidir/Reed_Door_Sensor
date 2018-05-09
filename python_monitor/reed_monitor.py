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

import sys
import logging
import serial
from datetime import datetime

# Setup main logging format and timestamp format
logging.basicConfig(format="%(levelname)s %(asctime)-15s %(message)s",
                    level=logging.DEBUG)
doorLog = logging.getLogger("DoorLog")

TS_format = "{:%Y-%m-%d %H:%M:%S.%f}"


def handle_door_event(notification):
    doorLog.message(notification)
    # TODO creazione delle e-mail


def main_service(serial_port, device_id):
    # Method called by systemd start of service
    import sdnotify
    from logging import handlers, Formatter

    n = sdnotify.SystemdNotifier()
    n.notify("READY=1")

    # log is redirected to syslog
    handle_doorLog = logging.handlers.SysLogHandler(address="/dev/log")
    handle_doorLog.setFormatter(logging.Formatter())
    doorLog.addHandler(handle_doorLog)

    reopen = True
    last_time_up = None
    while reopen:
        try:
            # opening serial port
            ser = serial.Serial(port=serial_port, baudrate=9600,
                                parity=serial.PARITY_NONE,
                                stopbits=serial.STOPBITS_ONE,
                                bytesize=serial.EIGHTBITS, timeout=4)
        except:
            # exiting in case of exception
            doorLog.critical("id={} - exception={}".format(device_id,
                             sys.exc_info()[1]))
            n.notify("STATUS=exception while opening serial port")
            n.notify("STOPPING=1")
            return 1

        # reopen flag in case of reading mistakes
        reopen = False
        n.notify("STATUS=successfully opened serial port")
        previous = b'S'
        exception_counter = 0
        while True:
            timestamp = TS_format.format(datetime.now())

            try:
                # read a char from serial
                character = ser.read(1)
            except:
                doorLog.critical("id={} - exception={}"
                                 .format(device_id, sys.exc_info()[1]))
                exception_counter += 1
                if exception_counter <= 5:
                    # retry to read 5 times
                    n.notify("STATUS={} #{}".format(sys.exc_info()[1],
                                                    exception_counter))
                    continue
                else:
                    # if after 5 attempts read is impossible, exits
                    n.notify("STATUS=exception while reading serial port")
                    n.notify("STOPPING=1")
                    ser.close()
                    return 1

            if len(character) >= 1:
                exception_counter = 0
                if character == b'U':
                    n.notify("STATUS=up and running")
                    last_time_up = datetime.now()
                    if previous != character:
                        doorLog.info("RDM on device {} is up and running".format(device_id))
                elif character == b'O':
                    notification = "Door opened at {}".format(timestamp)
                    n.notify("STATUS={}".format(notification))
                    if previous != character:
                        doorLog.warning(notification)
                        handle_door_event(notification)
                elif character == b'C':
                    notification = "Door closed at {}".format(timestamp)
                    n.notify("STATUS={}".format(notification))
                    if previous != character:
                        doorLog.warning(notification)
                        handle_door_event(notification)
                else:
                    if previous != b'E':
                        n.notify("STATUS=Read unknown '{}' from serial port".format(character))
                        doorLog.warning("Read unknown '{}'(len={}) from serial port".format(character,
                                        len(character)))
                    else:
                        # if we have two mistakes in reading, try close
                        # and reopen the serial port
                        reopen = True
                        break
                    character = b'E'
                previous = character
        # when closing and reopening because of mistakes, we check that
        # not too much time has passed. In case, we exit and call
        # the event handler
        last_time_up_delta_seconds = (datetime.now()-last_time_up).total_seconds()
        if ((last_time_up is not None) and (last_time_up_delta_seconds > 180)):
            notification = "Timeout in Up-And-Running communication reached: {} seconds".format(last_time_up_delta_seconds)
            handle_door_event(notification)
            doorLog.critical(notification)
            n.notify("STOPPING=1")
            ser.close()
            return 1
        elif last_time_up_delta_seconds > 0:
            n.notify("STATUS=Up-and-running silence interval: {} seconds".format(last_time_up_delta_seconds))
        ser.close()
    n.notify("STOPPING=1")
    return 0


def main_on_request(serial_port, device_id):
    reopen = True
    last_time_up = None
    while reopen:
        try:
            # opening serial port
            ser = serial.Serial(port=serial_port, baudrate=9600,
                                parity=serial.PARITY_NONE,
                                stopbits=serial.STOPBITS_ONE,
                                bytesize=serial.EIGHTBITS, timeout=4)
        except:
            # exiting in case of exception
            doorLog.critical("id={} - exception={}".format(device_id,
                             sys.exc_info()[1]))
            return 1

        # reopen flag in case of reading mistakes
        reopen = False
        previous = b'S'
        while True:
            timestamp = TS_format.format(datetime.now())

            try:
                character = ser.read(size=1)
            except KeyboardInterrupt:
                # in the on-request case, Ctrl-C is to be considered
                # as a legitimate stop request
                doorLog.info("Keyboard interrupt!")
                ser.close()
                return 0
            except:
                # exits immediately if reading is impossible
                doorLog.critical("id={} - exception={}".format(device_id,
                                 sys.exc_info()[1]))
                ser.close()
                return 1

            if len(character) >= 1:
                if character == b'U':
                    if previous != character:
                        doorLog.info("RDM on device {} is up and running".format(device_id))
                    last_time_up = datetime.now()
                elif character == b'O':
                    notification = "Door opened at {}".format(timestamp)
                    doorLog.warning(notification)
                elif character == b'C':
                    notification = "Door closed at {}".format(timestamp)
                    doorLog.warning(notification)
                else:
                    if previous != b'E':
                        doorLog.warning("Read unknown {}(len={}) from serial port".format(character,
                                        len(character)))
                    else:
                        reopen = True
                        break
                    character = b'E'
                previous = character
        last_time_up_delta_seconds = (datetime.now()-last_time_up).total_seconds()
        if ((last_time_up is not None) and (last_time_up_delta_seconds > 180)):
            doorLog.critical("Timeout in Up-And-Running communication reached: {} seconds".format(last_time_up_delta_seconds))
            ser.close()
            return 1
        elif last_time_up_delta_seconds > 0:
            doorLog.info("Up-and-running silence interval: {} seconds".format(last_time_up_delta_seconds))
        ser.close()
    return 0


if __name__ == '__main__':
    import argparse
    import subprocess
    import platform
    # parsing of command line arguments
    parser = argparse.ArgumentParser(description="Debian reed door sensor monitor")
    parser.add_argument("run-mode", choices=["service", "on-request"],
                        help="identifies if the script runs as standalone or systemd service")
    parser.add_argument("--sp", nargs="?", default="/dev/ttyACM0",
                        const="/dev/ttyACM0",
                        help="address in /dev of the device port")
    args = vars(parser.parse_args())

    if platform.system() != "Windows":
        # retrieving constructor serial id of device
        bashCommand = "udevadm info -q all -n {}".format(args["sp"])
        process1 = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        process2 = subprocess.Popen(["grep", "ID_SERIAL_SHORT=*"],
                                    stdin=process1.stdout,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        process1.stdout.close()
        output, error = process2.communicate()
        device_id = output.split("=")[1].replace("\n","")
    else:
        device_id = args["sp"]

    # calling main procedure
    if args["run-mode"] == "service":
        sys.exit(main_service(args["sp"], device_id))
    else:
        sys.exit(main_on_request(args["sp"], device_id))

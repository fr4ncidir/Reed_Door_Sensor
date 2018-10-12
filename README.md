## Hardware
ESP8266 Huzzah, programmed by Arduino IDE
ST Nucleo32, programmed by [mbed](https://www.mbed.com/en/) online compiler.
The software is available in the `./reed_door_sensor/reed_door_sensor.ino` file.

## Install
Requirements: `git`

To install the services and all the needed software, *_as root_*, call the following:
```
$ git clone "this repository"
$ cd "this repository folder"
$ bash install.sh /dev/ttyXYZ
```

Will install:
#### a) pyserial
Python package for serial communication
#### b) sdnotify
Python package available on github, to setup systemd services.
#### c) ModemManager
Read the issue opened [here](https://bugs.launchpad.net/modemmanager/+bug/700261). ModemManager occupies the serial port *before* the reed_door.service. This creates some issues when later opening the port properly. It should be removed.
#### udev rule
#### systemd service 
calling
```
python ./python_monitor/reed_monitor.py service --sp /dev/ttyUSB0
```
python script.

## Working
Plug the Huzzah, or the STM Nucleo32, then the service should run and start to log events in `/var/log/messages`.
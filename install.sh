#! /bin/bash

# Centos7 setup script for all the necessary to get the Reed door sensor
# working. The script requires high privileges because it installs
# pyserial from yum repositories, sdnotify from github.
# It removes ModemManager (which gives a lot of problems with preemption on
# tty USB devices. 
# It installs a systemd service and a UDEV rule based on the connected Reed
# microcontroller.

# exits if command returns nonzero
set -e

# check for high privileges
if [ "$EUID" -ne 0 ] ; then
    echo Please run as root
    exit
fi

# check for the tty device existence
if [ -e "$1" ] ; then
    echo "Serial port <$1> was found"
else
    echo "Serial port <$1> not found, aborting"
    exit
fi

# check that this script is ran from outside parent directory
if [ -e "./install.sh" ] ; then
	cd ..
fi
if [ ! -d "./Reed_Door_Sensor" ] ; then
	echo Wrong folder! Check README
	exit
fi

WD=$(pwd)

# installs pyserial
echo Installing packet dependencies...
yum install pyserial

# removes ModemManager
echo Removing ModemManager...
yum remove ModemManager

# clones and installs sdnotify repo from GitHub
echo Cloning sdnotify repository...
git clone https://github.com/bb4242/sdnotify.git
cd ./sdnotify
echo Installing sdnotify...
python setup.py install

# creates the systemd service
echo Creating systemd service....q
cd ../Reed_Door_Sensor/python_monitor
sed "s@__WORKING_DIRECTORY__@`pwd`@g" reed_door_daemon.service > temp.service
sed -i "s@__PYTHON_PATH__@`which python`@g" temp.service
sed -i "s@__TTY_PATH__@$1@g" temp.service
# puts the service file in systemd folder
sed "s@__FULL_SCRIPT_PATH__@`realpath reed_monitor.py`@g" temp.service > /etc/systemd/system/reed_daemon.service
ln --symbolic /etc/systemd/system/reed_daemon.service .
rm temp.service

# creates the udev rule
echo Creating udev rule...
# gets the device serial number
SNUMBER=`udevadm info -q all -n $1 | grep -o "ID_SERIAL_SHORT=.*" | cut -d "=" -f2`
if [ -e /etc/udev/rules.d/10-local.rules ] ; then
    ls -la /etc/udev/rules.d
    echo Rule name exists, aborting
    exit
fi
sed "s@__SERIAL_NUMBER__@$SNUMBER@g" udev_rule.rules > /etc/udev/rules.d/10-local.rules
ln --symbolic /etc/udev/rules.d/10-local.rules .

cd $WD
echo Installed. Reboot and try...

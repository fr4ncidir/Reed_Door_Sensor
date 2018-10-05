#! /bin/bash

if [ "$EUID" -ne 0 ] 
    then 
    echo Please run as root
    exit
fi

WD=`pwd`
if [ -b "$1" ]
    then
    echo "Serial port <$1> was found"
else
    echo "Serial port <$1> not found"
    exit
fi

echo Installing packet dependencies...
yum install git pyserial

echo Removing ModemManager...
yum remove ModemManager

echo Cloning repositories...
git clone https://github.com/fr4ncidir/Reed_Door_Sensor.git
git clone https://github.com/bb4242/sdnotify.git

cd ./sdnotify
echo Installing sdnotify...
python setup.py install

echo Creating systemd service....
cd ../Reed_Door_Sensor/python_monitor
sed "s@__WORKING_DIRECTORY__@`pwd`@g" reed_door_daemon.service > temp.service
sed -i "s@__PYTHON__PATH@`which python`@g" temp.service
sed "s@__FULL_SCRIPT_PATH__@`realpath reed_monitor.py`@g" temp.service > /etc/systemd/system/reed_daemon.service

echo Creating udev rule...
#SNUMBER=`udevadm info -q all -n $1 | grep `
cd /etc/udev/rules.d
if [ -e 10-local.rules ]
    then
    echo Rule name exists, aborting
    exit
fi
#sed "s@__SERIAL_NUMBER__@$SNUMBER@g" udev_rule.rules > /etc/udev/rules.d/10-local.rules

cd $WD
echo Installed.

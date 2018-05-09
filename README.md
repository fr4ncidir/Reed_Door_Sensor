## ModemManager issue

Read the issue opened [here](https://bugs.launchpad.net/modemmanager/+bug/700261).

ModemManager occupies the serial port *before* the reed_door.service. This creates some issues when later opening the port properly.

```
yum remove ModemManager
```
is not always possible.

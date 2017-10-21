#!/bin/sh
#
# Usage:
#  sudo ./set_servo.sh SERVO_ENABLE

# if [ "$USER" != "root" ]; then
#   echo "Error: set_servo.sh must be run as superuser"
#   exit
# fi

SERVO_ENABLE=$1

if [ "$SERVO_ENABLE" = "" ]; then SERVO_ENABLE=0; fi

/bin/echo $SERVO_ENABLE >/sys/class/gpio/gpio80/value

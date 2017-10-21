#!/bin/sh
#
# Usage
# ~~~~~
# - sudo ~debian/autonomous_vehicle/bbb_scripts/ardurover.sh
# - sudo ~debian/autonomous_vehicle/bbb_scripts/set_servo.sh 1

HOST_NAME=nomad.local
HOST_IP=127.0.0.1
LOG_FILE=~debian/log/ardurover.log

mkdir -p ~debian/log

# if [ "$USER" != "root" ]; then
#   echo "Error: ardurover.sh must be run as superuser"
#   exit
# fi

rm -rf /var/APM/logs/*

if [ "$1" != "" ]; then HOST_NAME=$1; fi

WAIT_FOR_WIFI=true

while $WAIT_FOR_WIFI; do
  iwconfig wlan0 >/dev/null 2>&1
  if [ $? = 0 ]; then WAIT_FOR_WIFI=false; fi
done

iwconfig wlan0   power off >/dev/null 2>&1
# iwconfig SoftAp0 power off >/dev/null 2>&1
# ifconfig SoftAp0 down      >/dev/null 2>&1

HOST_ENT=`getent hosts $HOST_NAME`

if [ $? = 0 ]; then
  HOST_IP=`echo $HOST_ENT | cut -d' ' -f1`
else
  echo "Error: couldn't resolve ground control host name:" $HOST_NAME
fi

echo "Using ground control host IP:" $HOST_IP

set_servo() {
  servo_enable=$1
  if [ "$SERVO_ENABLE" = "" ]; then SERVO_ENABLE=0; fi
  /bin/echo $SERVO_ENABLE >/sys/class/gpio/gpio80/value
}

sigint_handler() {
  echo
  echo "Disabling servo power rail"
  set_servo 0
  exit
}

trap sigint_handler 2

# Avoid ArduRover driving servo hard left :(
echo "Disabling servo power rail"
set_servo 0
( sleep 5;
  echo "Enabling servo power rail"
  /home/debian/autonomous_vehicle/bbb_scripts/set_servo.sh 1
) &

/bin/echo uart >/sys/devices/platform/ocp/ocp\:P9_21_pinmux/state
/bin/echo uart >/sys/devices/platform/ocp/ocp\:P9_22_pinmux/state

echo "ArduRover running"
/usr/bin/ardupilot/blue-ardurover -C udp:$HOST_IP:14550 >$LOG_FILE &

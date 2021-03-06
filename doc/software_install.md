# Autonomous Vehicle: Software installation

This documentation is for a set-up using a BeagleBone Blue on the scale model
RC car and a laptop communicating over a wireless network.

BeagleBone Blue ...
- ArduRover (flight controller): vehicle control and telemetry
- GStreamer: video capture and streaming

Laptop ...
- DroneKit: Interaction with ArduRover via MAVLink messages
- Neural Network for Machine Learning of video stream

## BeagleBone Blue software installation

### Configure Wi-Fi

```
  connmanctl
    scan wifi
    services
    agent on
    connect wifi_????????????_??????????????????_managed_psk
      Passphrase? ????????
      Connected wifi_????????????_??????????????????_managed_psk
    exit
  ping google.com
```

```
  service hostapd stop
  service hostapd disable
  service hostapd status
  apt-get remove hostapd 
```

```
  vi /etc/hostname  # beaglebone -> UNIQUE_HOST_NAME
  vi /etc/hosts     # beaglebone -> UNIQUE_HOST_NAME
  reboot
  iwconfig wlan0 power off
```

### Debian (Linux operating system)
```
  apt-get update
  apt-get upgrade -y
    Configuring roboticscape
    Which program to run on boot ?  existing
```

### Remove superfluous packages to save space
```
# List installed packages in reverse size order
  dpkg-query -Wf '${Installed-Size}\t${Package}\n' | sort -n
# Recover 183Mb
  dpkg --list |grep "^rc" | cut -d " " -f 3 | xargs sudo dpkg --purge
  apt-get remove bone101 bonescript nodejs bb-node-red-installer apache2
  apt-get clean
  apt-get purge
  apt-get autoclean
  apt-get autoremove
```

### Install ArduRover

```
  apt-get install -y ardupilot-rover-blue
  cd bbb_scripts
  cp ardurover.service /lib/systemd/system
  systemctl enable ardurover.service
  systemctl start  ardurover.service
  systemctl status ardurover.service
  # systemctl stop  ardurover.service
```

### Install GStreamer and video scripts

```
  apt-get install gstreamer-1.0 gstreamer1.0-tools
  apt-get install gstreamer1.0-plugins-base gstreamer1.0-plugins-good
  apt-get install gstreamer1.0-plugins-bad  gstreamer1.0-plugins-ugly

  v4l2-ctl --list-devices
    USB 2.0 Camera (usb-musb-hdrc.1.auto-1):
      /dev/video0
```

```
  cd bbb_scripts
  vi gstreamer_webcam.sh
    REMOTE_HOST=CHANGE_ME.local
  ./gstreamer_webcam.sh
```

```
  cd bbb_scripts
  cp gstreamer_webcam.service /lib/systemd/system
  systemctl enable gstreamer_webcam.service
  systemctl start  gstreamer_webcam.service
  systemctl status gstreamer_webcam.service
  # systemctl stop  gstreamer_webcam.service
```

## Laptop software installation

### Install GStreamer and video scripts

```
  brew install gstreamer gst-plugins-base gst-plugins-good gst-plugins-bad gst-plugins-ugly gst-libav
  brew install gst-plugins-bad
```

```
  cd src
  ./video_display.sh
```

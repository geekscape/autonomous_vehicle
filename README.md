# Self-driving (scale model) car project

## Project team

## Hardware

### Bill Of Materials

## Software

- ArduRover (flight controller)
- DroneKit (or similar)
- Video streaming

### BeagleBone Blue software installation

#### Configure Wi-Fi

#### Debian (Linux operating system)
```
  apt-get update
  apt-get upgrade -y
    Configuring roboticscape
    Which program to run on boot ?  existing
```

#### Remove superfluous packages to save space
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

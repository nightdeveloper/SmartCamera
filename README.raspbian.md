# Raspbian OS configuration

## install new packages
```
sudo apt update
sudo apt full-upgrade

wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.58.tar.gz
sudo tar zxvf bcm2835-1.58.tar.gz

cd bcm2835-1.58
sudo ./configure
sudo make check
sudo make install
cd ..

sudo apt-get install git python3-pip

sudo pip3 install picamera "picamera[array]" flask RPi.GPIO spidev Adafruit-GPIO Adafruit-PureIO opencv-python
```

## Clean up packages (only for camera-only standalone systems)
```
sudo apt-get remove --purge triggerhappy logrotate dphys-swapfile
sudo apt-get autoremove --purge

sudo apt-get install busybox-syslogd
sudo apt-get remove --purge rsyslog
```

## Read logs 
```
sudo logread
```

## Add users and ssh keys (optional)

[[https://nightdeveloper.github.io/tech-particles/ssh-keys]]

## Enable I2C

[[https://nightdeveloper.github.io/tech-particles/i2c]]

## Deploying
```
cd /opt
sudo git clone https://github.com/nightdeveloper/SmartCamera
sudo chown -R pi:pi /opt/SmartCamera
```

## Enable camera
``` 
sudo raspi-config
# interface options -> camera -> yes
```

## Setting service
```
sudo cp ./ptz_camera.service /etc/systemd/system/ptz_camera.service
sudo systemctl daemon-reload
sudo systemctl enable ptz_camera
sudo systemctl start ptz_camera
```

## Service tools
```
sudo systemctl start ptz_camera
sudo systemctl stop ptz_camera
sudo systemctl status ptz_camera
journalctl -u ptz_camera -b
```

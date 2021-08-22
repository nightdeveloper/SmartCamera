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

sudo pip3 install picamera "picamera[array]" RPi.GPIO spidev Adafruit-GPIO Adafruit-PureIO
sudo pip3 install stomper websocket

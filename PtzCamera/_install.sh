wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.58.tar.gz
sudo tar zxvf bcm2835-1.58.tar.gz

cd bcm2835-1.58
sudo ./configure
sudo make check
sudo make install
cd ..

sudo apt-get install git

sudo apt-get install python3-pip

sudo pip3 install RPi.GPIO
sudo pip3 install spidev

sudo pip3 install picamera
sudo pip3 install "picamera[array]"

sudo pip3 install Adafruit-GPIO
sudo pip3 install adafruit_platformdetect
sudo pip3 install Adafruit-PureIO

sudo pip3 install opencv-python
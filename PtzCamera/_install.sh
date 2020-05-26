wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.58.tar.gz
sudo tar zxvf bcm2835-1.xx.tar.gz
cd bcm2835-1.xx
sudo ./configure
sudo make check
sudo make install

sudo apt-get install git
sudo git clone git://git.drogon.net/wiringPi
cd wiringPi
sudo ./build

sudo apt-get install python-pip
sudo pip install RPi.GPIO
sudo pip install spidev
sudo apt-get install python-imaging
sudo apt-get install python-smbus

sudo pip install spidev

sudo pip install picamera
sudo pip install "picamera[array]"

sudo pip install opencv-python
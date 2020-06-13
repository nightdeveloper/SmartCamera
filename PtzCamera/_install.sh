wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.58.tar.gz
sudo tar zxvf bcm2835-1.58.tar.gz

cd bcm2835-1.58
sudo ./configure
sudo make check
sudo make install
cd ..

sudo apt-get install git
sudo apt-get install wiringpi
sudo apt-get install python-smbus

sudo apt-get install python-pip
sudo pip install RPi.GPIO
sudo pip install spidev

sudo pip install picamera
sudo pip install "picamera[array]"

sudo pip install opencv-python
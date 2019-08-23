#!/bin/sh
sudo apt-get -y update 
sudo apt-get -y upgrade 
sudo apt-get -y autoremobe
sudo apt-get install -y libasound2-dev git build-essential python3-dev libpython3.7-dev libjack-jackd2-dev cython3 python3-setuptools i2c-tools python3-smbus python3-rpi.gpio python3-pip timidity fluid-soundfont-gm python3-rpi.gpio python3-spidev python3-pip python3-numpy build-essential libjpeg-dev debhelper fonts-takao-gothic
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_spi 0 
sudo raspi-config nonint do_uart 0

sudo sed -i -e '$ a dtparam=i2s=on' /boot/config.txt
sudo sed -i -e '/#dtparam=i2s=on/d' /boot/config.txt
sudo sed -i -e '$ a dtoverlay=pi3-miniuart-bt' /boot/config.txt
sudo sed -i -e 'dtoverlay=midi-uart0' /boot/config.txt
sudo sed -i -e 's/console=serial0,115200//' /boot/cmdline.txt

cd /home/pi/ysynth4/
rm timidity_2.14.0.orig.tar.bz2*
wget http://deb.debian.org/debian/pool/main/t/timidity/timidity_2.14.0.orig.tar.bz2
tar jxf /home/pi/ysynth4/timidity_2.14.0.orig.tar.bz2
cd TiMidity++-2.14.0/
patch -p1 < /home/pi/ysynth4/timidity++-2.14.0-cfgforsf-src.patch
./configure --disable-audio --without-x
for dir in libarc utils; do make -C ${dir}; done
cd timidity/
make -j4 newton_table.c
for f in common controls instrum sbkconv sffile sfitem sndfont tables version mt19937ar quantity smplfile filter freq resample ../interface/dumb_c; do gcc -DCFG_FOR_SF -DHAVE_CONFIG_H -I. -I../ -I../utils -I../libarc -c ${f}.c; done
gcc -o cfgforsf common.o controls.o instrum.o sbkconv.o sffile.o sfitem.o sndfont.o tables.o version.o mt19937ar.o quantity.o smplfile.o filter.o freq.o resample.o dumb_c.o -L../libarc -L../utils -lm -larc -lutils
mv cfgforsf /home/pi/ysynth4
cd /home/pi
rm /home/pi/ysynth4/TiMidity++-2.14.0/ -fr
rm /home/pi/ysynth4/timidity_2.14.0.orig.tar.bz2

sudo apt-get install debhelper
git clone https://github.com/rbrito/usbmount.git
cd /home/pi/usbmount
sudo dpkg-buildpackage -us -uc -b
cd ..
sudo apt install -y ./usbmount_0.0.24_all.deb
git clone https://github.com/YoutechA320U/ttymidi
cd /home/pi/ttymidi
gcc ttymidi.c -o ttymidi -lasound -pthread
mv ttymidi /home/pi/ysynth4
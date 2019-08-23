#!/bin/sh
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
sudo apt install  ./usbmount_0.0.24_all.deb
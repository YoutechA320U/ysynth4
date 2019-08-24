#!/bin/sh
#必要なパッケージのインストール
sudo apt-get -y update 
sudo apt-get -y upgrade 
sudo apt-get -y autoremove
sudo apt-get install -y libasound2-dev git build-essential python3-dev libpython3.7-dev libjack-jackd2-dev cython3 python3-setuptools i2c-tools python3-smbus python3-rpi.gpio python3-pip timidity fluid-soundfont-gm python3-rpi.gpio python3-spidev python3-pip python3-numpy build-essential libjpeg-dev debhelper fonts-takao-gothic libopenjp2-7 libtiff5
#RaspberryPiの機能をON
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_spi 0 
sudo raspi-config nonint do_uart 0
sudo sed -i -e '/dtparam=i2s=on/d' /boot/config.txt
sudo sed -i -e '$ a dtparam=i2s=on' /boot/config.txt
sudo sed -i -e '/#dtparam=i2s=on/d' /boot/config.txt
sudo sed -i -e '/core_freq=250/d' /boot/config.txt
sudo sed -i -e '$ a core_freq=250' /boot/config.txt
sudo sed -i -e '/dtoverlay=pi3-miniuart-bt/d' /boot/config.txt
sudo sed -i -e '/dtoverlay=midi-uart0/d' /boot/config.txt
sudo sed -i -e '$ a dtoverlay=pi3-miniuart-bt' /boot/config.txt
sudo sed -i -e '$ a dtoverlay=midi-uart0' /boot/config.txt
sudo sed -i -e 's/console=serial0,115200//' /boot/cmdline.txt
#cfgforsfのビルド&インストール
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
#usbmountのビルド&インストール
git clone https://github.com/rbrito/usbmount.git
cd /home/pi/usbmount
sudo dpkg-buildpackage -us -uc -b
cd ..
sudo apt install -y ./usbmount_0.0.24_all.deb
#ttymidiのビルド&インストール
git clone https://github.com/YoutechA320U/ttymidi
cd /home/pi/ttymidi
gcc ttymidi.c -o ttymidi -lasound -pthread
mv ttymidi /home/pi/ysynth4
#timidity設定ファイルの生成
sudo sh -c "echo 'opt iA\nopt Os\nopt --sequencer-ports=1\nopt --realtime-priority=90\nopt B3,8\nopt q0-0\nopt s32kHz\nopt -EFresamp=1\nopt -EFreverb=1\nopt -EFchorus=1\nopt p128a' > /etc/timidity/timidity.cfg"
#ysynth4のサービス生成&有効化
sudo sh -c "echo '[Unit]\nDescription = ysynth4\n[Service]\nExecStart = /usr/bin/python3.7 /home/pi/ysynth4/ysynth4.py\nRestart = always\nType = simple\n[Install]\nWantedBy = multi-user.target' > /etc/systemd/system/ysynth4.service"
sudo systemctl enable ysynth4.service
#USB-MIDI機器を自動接続するルールを追加
sudo mv /home/pi/ysynth4/90-usbmidiconnect.rules /etc/udev/rules.d/
#WiFi周りの設定を追加
sudo sed -i -e '/allow-hotplug wlan0/d' /etc/network/interfaces
sudo sed -i -e '/interfacesiface wlan0 inet manual/d' /etc/network/interfaces
sudo sed -i -e '/wpa_supplicant.conf/d' /etc/network/interfaces
sudo sed -i -e '/FS_MOUNTOPTIONS="-fstype=vfat,iocharset=utf8,codepage=932,uid=pi,gid=pi,dmask=000,fmask=011"/d' /etc/usbmount/usbmount.conf
sudo sed -i -e '$ a allow-hotplug wlan0\n /etc/network/interfacesiface wlan0 inet manual\n    wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf' /etc/network/interfaces
sudo sed -i -e '$ a FS_MOUNTOPTIONS="-fstype=vfat,iocharset=utf8,codepage=932,uid=pi,gid=pi,dmask=000,fmask=011"' /etc/usbmount/usbmount.conf
#pip3で必要なライブラリをインストール
sudo pip3 install pillow
sudo pip3 install st7735
sudo pip3 install python-rtmidi
#再起動
sudo reboot
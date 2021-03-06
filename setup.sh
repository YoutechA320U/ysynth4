#!/bin/sh

#オリジナルのソースコード/Original Source
# https://github.com/YoutechA320U/ysynth4
#ライセンス/Licence
# [MIT] https://github.com/YoutechA320U/ysynth4/blob/master/LICENSE

#必要なパッケージのインストール
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get -y autoremove
sudo apt-get install -y libasound2-dev git build-essential python3-dev libpython3.7-dev libjack-jackd2-dev cython3 python3-setuptools i2c-tools python3-smbus python3-rpi.gpio python3-pip fluid-soundfont-gm python3-rpi.gpio python3-spidev python3-numpy libjpeg-dev debhelper fonts-takao-gothic libopenjp2-7 libtiff5
#RaspberryPiの機能をON
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_spi 0 
#sudo sudo raspi-config nonint do_serial 2
sudo sed -i -e '/dtparam=i2s=on/d' /boot/config.txt
sudo sed -i -e '$ a dtparam=i2s=on' /boot/config.txt
sudo sed -i -e '/#dtparam=i2s=on/d' /boot/config.txt
sudo sed -i -e '/core_freq=250/d' /boot/config.txt
sudo sed -i -e '$ a core_freq=250' /boot/config.txt
sudo sed -i -e '/dtoverlay=dwc2/d' /boot/config.txt
sudo sed -i -e '/dtoverlay=pi3-miniuart-bt/d' /boot/config.txt
sudo sed -i -e '/dtoverlay=midi-uart0/d' /boot/config.txt
sudo sed -i -e '$ a dtoverlay=dwc2' /boot/config.txt
sudo sed -i -e '$ a dtoverlay=pi3-miniuart-bt' /boot/config.txt
sudo sed -i -e '$ a dtoverlay=midi-uart0' /boot/config.txt
sudo sed -i -e 's/console=serial0,115200 //' /boot/cmdline.txt
sudo sed -i -e 's/ modules-load=dwc2,g_midi//' /boot/cmdline.txt
sudo sed -i -e 's/$/ modules-load=dwc2,g_midi/' /boot/cmdline.txt
#cfgforsとTimidityのビルド&インストール
if [ `timidity -v |grep -m1 version |awk '{print $3}'| grep -v ^$` = "2.15.0" ]; then
  echo "Timidity++は最新のバージョンです"
else
  echo "Timidity++をバージョンアップします"
  cd /home/pi/ysynth4/
  rm *.patch
  rm *.tar.bz2
  wget https://raw.githubusercontent.com/YoutechA320U/ysynth4/master/timidity%2B%2B-2.15.0-cfgforsf-src.patch
  sudo apt-get remove -y timidity
  wget https://excellmedia.dl.sourceforge.net/project/timidity/TiMidity%2B%2B/TiMidity%2B%2B-2.15.0/TiMidity%2B%2B-2.15.0.tar.bz2
  tar jxf /home/pi/ysynth4/TiMidity++-2.15.0.tar.bz2
  cd TiMidity++-2.15.0/
  ./configure --without-x --enable-audio=alsa --enable-interface=alsaseq --enable-dynamic=alsaseq
  make -j4
  sudo make install
  patch -p1 < /home/pi/ysynth4/timidity++-2.15.0-cfgforsf-src.patch
  ./configure --disable-audio --without-x
  for dir in libarc utils; do make -C ${dir}; done
  cd timidity/
  make -j4 newton_table.c
  for f in common controls instrum sbkconv sffile sfitem sndfont tables version mt19937ar quantity smplfile filter freq resample ../interface/dumb_c; do gcc -DCFG_FOR_SF -DHAVE_CONFIG_H -I. -I../ -I../utils -I../libarc -c ${f}.c; done
  gcc -o cfgforsf common.o controls.o instrum.o sbkconv.o sffile.o sfitem.o sndfont.o tables.o version.o mt19937ar.o quantity.o smplfile.o filter.o freq.o resample.o dumb_c.o -L../libarc -L../utils -lm -larc -lutils
  mv cfgforsf /home/pi/ysynth4
  cd /home/pi/ysynth4/
  rm /home/pi/ysynth4/TiMidity++-2.15.0/ -fr
  rm *.tar.bz2
fi
cd /home/pi/
#ttymidiのビルド&インストール
if [ `/home/pi/ysynth4/ttymidi -V |grep -m1 ttymidi|awk '{print $2}'| grep -v ^$` = "0.60" ]; then
  echo "ttymidiは最新のバージョンです"
else
  echo "ttymidiをバージョンアップします" 
  sudo rm -rf /home/pi/ttymidi
  git clone https://github.com/YoutechA320U/ttymidi.git
  cd /home/pi/ttymidi
  gcc ttymidi.c -o ttymidi -lasound -pthread
  mv ttymidi /home/pi/ysynth4
  cd /home/pi/
fi
cd /home/pi/
#Timidity設定ファイルの生成
sudo mkdir /usr/local/share/timidity/
sudo sh -c "echo 'opt iA\nopt Os\nopt --sequencer-ports=1\nopt --realtime-priority=90\nopt B3,8\nopt q0-0\nopt s32kHz\nopt -EFresamp=1\nopt -EFreverb=1\nopt -EFchorus=1\nopt p128a' > /usr/local/share/timidity/timidity.cfg"
#ysynth4のサービス生成&有効化
sudo sh -c "echo '[Unit]\nDescription = ysynth4\n[Service]\nExecStart = /usr/bin/python3.7 /home/pi/ysynth4/ysynth4.py\nRestart = always\nType = simple\n[Install]\nWantedBy = multi-user.target' > /etc/systemd/system/ysynth4.service"
sudo systemctl enable ysynth4.service
#midiconnect更新
sudo sh -c "echo 'aconnect 128:0 131:0\naconnect 128:0 130:0\naconnect 129:0 128:1\naconnect 129:0 131:0\naconnect 129:0 16:0\naconnect 129:0 20:0\naconnect 129:0 24:0\naconnect 129:0 28:0\naconnect 16:0 130:0\naconnect 16:0 131:0\naconnect 20:0 130:0\naconnect 20:0 131:0\naconnect 24:0 130:0\naconnect 24:0 131:0\naconnect 28:0 130:0\naconnect 28:0 131:0\naconnect 14:0 128:1\naconnect 14:0 130:0\naconnect 14:0 131:0\naconnect 14:0 16:0\naconnect 14:0 20:0\naconnect 14:0 24:0\naconnect 14:0 28:0' > /home/pi/ysynth4/midiconnect.sh"
#デフォルトのサウンドカードを2に
sudo sh -c "echo 'defaults.pcm.card 1\ndefaults.ctl.card 1' >  /etc/asound.conf"
#USB-MIDI機器を自動接続するルールを追加
sudo cp /home/pi/ysynth4/90-usbmidiconnect.rules /etc/udev/rules.d/
#pip3で必要なライブラリをインストール
sudo pip3 install pillow
sudo pip3 install st7735
sudo pip3 install python-rtmidi
sudo sed -i -e 's/ST7735_INVOFF = 0x20/ST7735_INVOFF = 0x21/g' -e 's/ST7735_INVON = 0x21/ST7735_INVON = 0x20/g' -e 's/self.data(0xC8)/self.data(0xC0)/g' /usr/local/lib/python3.7/dist-packages/ST7735/__init__.py
#usbmountをインストール
git clone https://github.com/rbrito/usbmount.git
cd /home/pi/usbmount
sudo dpkg-buildpackage -us -uc -b
cd ..
sudo apt install -y ./usbmount_0.0.24_all.deb
sudo sed -i -e '/FS_MOUNTOPTIONS="-fstype=vfat,iocharset=utf8,codepage=932,uid=pi,gid=pi,dmask=000,fmask=011"/d' /etc/usbmount/usbmount.conf
sudo sed -i -e '$ a allow-hotplug wlan0\n /etc/network/interfacesiface wlan0 inet manual\n    wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf' /etc/network/interfaces
sudo sed -i -e '$ a FS_MOUNTOPTIONS="-fstype=vfat,iocharset=utf8,codepage=932,uid=pi,gid=pi,dmask=000,fmask=011"' /etc/usbmount/usbmount.conf

#再起動
#sudo reboot
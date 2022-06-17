# -*- coding: utf-8 -*-
#!/usr/bin/env python

#オリジナルのソースコード/Original Source
# https://github.com/YoutechA320U/ysynth4
#ライセンス/Licence
# [MIT] https://github.com/YoutechA320U/ysynth4/blob/master/LICENSE


##--リリースノート--##
#v1.75[2019/09/07]
#スクリーンキーボードを使ってスタンドアロンにWiFiの設定が出来る様になりました.
#これで有線LANを用意したり,キーボードとディスプレイを繋いで設定しなくてもオンラインアップデートが可能になりました。

#v1.8[2019/09/09]
#WiFiで設定したアクセスポイントを優先して接続するようになりました。
#他にもコマンドを見直してより安定するようになりました。

#v1.9 [2019/09/13]
#ディスプレイの描画がマルチスレッド化され外部MIDI入力とボタンMIDI入力が完全に同時かつ更にバックグラウンドでも常時反映されるようになりました。

#v1.91 [2019/09/14]
#万が一ディスプレイがフリーズした場合にMODEキーを押しながら他のキーを全て押すとディスプレイがリセットするようになりました。

#v1.92 [2019/09/16]
#一部変数の抜けを修正しました。

#v1.94 [2020/1/27]
#RaspbianbusterLiteに対応しています。
#セットアップ時に自前でTimidity++version2.15.0をビルドするようになりました。
#Ysynth4アップデート時にsetup.shを再実行し,システムやライブラリのアップデートも行うようになりました。
#それに伴いアップデート時のディスプレイの挙動も変更しました。

#v1.95 [2020/1/28]
#ピッチベンドの出力が正常でない不具合を修正しました。

#v1.96 [2020/4/11]
#RaspberryPi4のOTG_USB-MIDIに対応しました。
#v1.97 [2020/4/21]
#サウンドカード切り替えの処理が間違っていたので修正
##--##--##--##--##

import RPi.GPIO as GPIO
import time
import subprocess
import rtmidi
import sys

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import ST7735
import threading

width = 128
height = 160

disp = ST7735.ST7735(
    port=0,
    cs=0,
    dc=12,
    rst=25,          
    rotation=90,
    width=128,
    height=160,
    spi_speed_hz=31200000+15600000
)

# Initialize display.
disp.begin()

width = disp.width
height = disp.height

img = Image.new('RGB',(width,height),color=(0,0,0))

draw = ImageDraw.Draw(img)
draw.rectangle((0,0,160,160),(0,0,0))

#*#*#*#*#*#*#
version= 1.97
day="2020/04/21"
#*#*#*#*#*#*#*
volume = 70
mode = 0

midCH = 0
midPRG=  [0]*16
midCC7=  [100]*16
midCC11=  [127]*16
midCC10=  [64]*16
midCC1=  [0]*16
midCC91=  [40]*16
midCC93=  [0]*16
midCC94=  [0]*16
pb1 = [0x00]*16
pb2 = [0x40]*16
playflag = [0]
sf2used = [0]
pbcounter =[0]*16
midicounter = 0
sf2counter = 0
wificounter = 0
dialog_open=0
longpush=0

input_OK = 16
input_MODE = 17
input_LEFT = 6
input_RIGHT = 24
input_UP = 23
input_DOWN = 5
mode0_write= False
waitflag=0

GPIO.setmode(GPIO.BCM)
GPIO.setup(input_OK,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(input_MODE,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(input_RIGHT,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(input_LEFT,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(input_UP,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(input_DOWN,GPIO.IN,pull_up_down=GPIO.PUD_UP)
fontss = ImageFont.truetype('/usr/share/fonts/truetype/takao-gothic/TakaoGothic.ttf',12,encoding='unic')
fonts = ImageFont.truetype('/usr/share/fonts/truetype/takao-gothic/TakaoGothic.ttf',13,encoding='unic')
fontm = ImageFont.truetype('/usr/share/fonts/truetype/takao-gothic/TakaoGothic.ttf',14,encoding='unic')
fontl = ImageFont.truetype('/usr/share/fonts/truetype/takao-gothic/TakaoGothic.ttf',20,encoding='unic')
fontll = ImageFont.truetype('/usr/share/fonts/truetype/takao-gothic/TakaoGothic.ttf',24,encoding='unic')

subprocess.call('sudo mount -t vfat -o ,iocharset=utf8 /dev/sda1 /media/usb0' ,shell=True)
mountcheck=subprocess.check_output("mount|grep -m1 /dev/sda|awk '{print $3}'" ,shell=True).decode('utf-8').strip()

def boot_disp():
   global mountcheck
   for x in range(69):
    draw.rectangle((0,0,160,128),(0,0,0))
    if mountcheck == str("/media/usb0"):
       draw.text((35,1+x-32),"Ysynth4",font=fontll,fill=(55,255,255))
       #draw.text((35,1+x-32),"         ®",font=fontl,fill=(55,255,255))
    if mountcheck != str("/media/usb0"):
       draw.rectangle((40,1+x-32,120,1+x-10),outline=(100,100,100),fill=(55,255,255))
       #draw.text((35,1+x-32),"         ®",font=fontl,fill=(55,255,255))
    draw.text((35,100),"v{0}/{1}" .format(version,day),font=fontss,fill=(55,255,255))
    draw.text((40,110),"@YoutechA320U",font=fontss,fill=(55,255,255))
    time.sleep(0.01)
    disp.display(img)
boot_disp()
if mountcheck == str("/media/usb0"): 
   subprocess.call('sudo mkdir /media/usb0/midi' ,shell=True)
   subprocess.call('sudo mkdir /media/usb0/sf2' ,shell=True)
   subprocess.call('sudo mkdir /media/usb0/timidity_cfg' ,shell=True)
   fluidcheck=subprocess.check_output("find /media/usb0/sf2/ -name FluidR3_GM.sf2" ,shell=True).decode('utf-8').strip()
   if fluidcheck != str("/media/usb0/sf2/FluidR3_GM.sf2"): 
      subprocess.call('sudo cp /usr/share/sounds/sf2/FluidR3_GM.sf2 media/usb0/sf2/' ,shell=True)
subprocess.call('rename.ul .MID .mid /media/usb0/midi/*' ,shell=True)
subprocess.call('rename.ul .SF2 .sf2 /media/usb0/sf2/*' ,shell=True)
subprocess.call('rename.ul .CFG .cfg /media/usb0/timidity_cfg/*' ,shell=True)
midi = subprocess.check_output('find /media/usb0/midi/ -name \*.mid|sort' ,shell=True).decode('utf-8').strip().replace('/media/usb0/midi/','').replace('.mid','').split('\n')
playflag = [0]*len(midi)
if midi[0]=='':
   midi= ["midi_None"]
   midicounter=0
sf2 = subprocess.check_output('find /media/usb0/sf2/ -name \*.sf2|sort' ,shell=True).decode('utf-8').strip().replace('/media/usb0/sf2/','').replace('.sf2','').split('\n')
sf2used = [0]*len(sf2)
if sf2[0]=='':
   sf2 = ["sf2_None"]
   sf2counter = 0
cfg = subprocess.check_output('find /media/usb0/timidity_cfg/ -name \*.cfg|sort' ,shell=True).decode('utf-8').strip().replace('/media/usb0/timidity_cfg/','').replace('.cfg','').split('\n')
if (sf2 != cfg) and (sf2[0] != "sf2_None"):
 list_difference = list(set(cfg) - set(sf2))
 for x in range(len(list_difference)):
  subprocess.call('sudo rm "/media/usb0/timidity_cfg/{}.cfg"' .format(list_difference[x])  ,shell=True)
 list_difference = list(set(sf2) - set(cfg))
 for x in range(len(list_difference)):
  subprocess.call('''sudo /home/pi/ysynth4/cfgforsf -C "/media/usb0/sf2/{sf2name}.sf2" | sed -e 's/(null)//' -e 's/^[ ]*//g' -e '/(null)#/d'  -e /^#/d | grep -C 1 % | sed -e '/--/d' -e /^$/d > "/media/usb0/timidity_cfg/{sf2name}.cfg"''' .format(sf2name=list_difference[x])  ,shell=True)
if sf2[0] == "sf2_None":
   subprocess.call('sudo rm /media/usb0/sf2/*.cfg' ,shell=True)

draw.rectangle((0,0,160,128),(0,0,0))
time.sleep(2)
disp.display(img)

subprocess.call('sudo killall ttymidi',shell=True)
subprocess.call('sudo killall timidity',shell=True)
subprocess.Popen('sudo /home/pi/ysynth4/ttymidi -s /dev/ttyAMA0 -b 38400',shell=True)
time.sleep(1)
midiout = rtmidi.MidiOut()
midiout.open_virtual_port("Ysynth4_out") # 仮想MIDI出力ポートの名前
midiin = rtmidi.MidiIn()
midiin.open_virtual_port("Ysynth4_in") # 仮想MIDI入力ポートの名前
midiin.ignore_types(sysex=False)
def allnoteoff():
    a = 0xb0
    while (a < 0xbf ):
        midiout.send_message([a,0x78,0x00])
        a += 1
subprocess.call('amixer cset numid=1 {}% > /dev/null'.format(volume) ,shell=True)
wifi_connect=subprocess.check_output('''wpa_cli -i wlan0 status|grep -v bssid |grep ssid |sed -e 's/ssid=//g' ''' ,shell=True).decode('utf-8').strip()
if wifi_connect=="":
   wifi_connect="接続できません" 
#wifi_connect="**********"
audio_card = str(subprocess.check_output("aplay -l |grep -m1 'card 1'|awk '{print $4;}' " ,shell=True).decode('utf-8').strip().replace(']','').replace('[','').replace(',',''))
mountcheck=subprocess.check_output("mount|grep -m1 /dev/sda|awk '{print $3}'" ,shell=True).decode('utf-8').strip()
subprocess.call('sh /home/pi/ysynth4/midiconnect.sh',shell=True)

x = 3
y = 0
m_size="A" #1文字分
cur_size="▶"

tsx,tsy  = draw.textsize(m_size,fontss)
tmx,tmy  = draw.textsize(m_size,fontm)
tlx,tly  = draw.textsize(m_size,fontl)
csx,csy  = draw.textsize(m_size,fontss)

#txt_size_s_x,txt_size_s_y  = tsx,tsy
#txt_size_m_x,txt_size_m_y  = tmx,tmy
#txt_size_l_x,txt_size_l_y  = tlx,tly
#cur_size_x,cur_size_y  = csx,cxy
mode0_coordi=0
mode0_coordi_xl=[3,3,3,3,3,3,3,3,tmx*10,tmx*10]
mode0_coordi_yl=[tly/4,tly+tmy+1,\
   tly+tmy*2+1,tly+tmy*3+1,\
      tly+tmy*4+1,tly+tmy*5+1,\
         tly+tmy*6+1,tly+tmy*7+1,\
            tly+tmy+1,tly+tmy*2+1]

mode1_coordi=0
mode1_coordi_xl=[3,3]
mode1_coordi_yl=[tly+tmy+8,tly+tmy*3+8]

mode2_coordi=0
mode2_coordi_xl=[3,3,3,3,3,3,3]
mode2_coordi_yl=[tly+tmy+1,tly+tmy*2+1,\
   tly+tmy*3+1,tly+tmy*4+1,\
      tly+tmy*5+1,tly+tmy*6+1,tly+tmy*7+1]

dlog_zahyo=1
#dialog_coordi=dlog_zahyo
dlog_zahyo_xl=[12,82]
dlog_zahyo_yl=[90,90]

sk_zahyo=0

msg = None
def mididisp(): #MIDI入力をディスプレイに反映する処理
   global midPRG,midCC7,midCC11,midCC10,midCC10,midCC1,midCC91,midCC93,midCC94,pb1,pb2,mode0_write
   while True:
    time.sleep(0.0001)
    msg = midiin.get_message()
    if msg is None:
       message,deltatime = None,None 
    if msg is not None:
       message,deltatime = msg
       try:
        if message == ([240,65,16,66,18,64,0,127,0,65,247]) or message ==( [240,67,16,76,0,0,126,0,247]) or message == ([240,126,127,9,1,247]) or message == ([240,126,127,9,3,247]) :
           midPRG= [0]*16
           midCC7=  [100]*16
           midCC11=  [127]*16
           midCC10=  [64]*16
           midCC1=  [0]*16
           midCC91=  [40]*16
           midCC93=  [0]*16
           midCC94=  [0]*16
           pb1 = [0]*16
           pb2 = [0x40]*16
           if mode == 0:
              draw.rectangle((tmx*5,tly+tmy+1,65,128),(0,0,0))
              draw.text((tmx*5,tly+tmy+1),str("{0:03d}".format(midPRG[midCH] + 1)),font=fontm,fill=(255,255,55))
              draw.text((tmx*5,tly+tmy*2+1),str("{0:03d}".format(midCC7[midCH])),font=fontm,fill=(255,255,55))
              draw.text((tmx*5,tly+tmy*3+1),str("{0:03d}".format(midCC11[midCH])),font=fontm,fill=(255,255,55))
              draw.text((tmx*5,tly+tmy*4+1),str("{0:03d}".format(midCC10[midCH]-64)),font=fontm,fill=(255,255,55))
              draw.text((tmx*5,tly+tmy*5+1),str("{0:03d}".format(midCC1[midCH])),font=fontm,fill=(255,255,55))
              draw.text((tmx*5,tly+tmy*6+1),str("{0:03d}".format(midCC91[midCH])),font=fontm,fill=(255,255,55))
              draw.text((tmx*5,tly+tmy*7+1),str("{0:03d}".format(midCC93[midCH])),font=fontm,fill=(255,255,55))
              draw.rectangle((tmx*18,tly+tmy+1,160,128),(0,0,0))
              draw.text((tmx*18,tly+tmy+1),str("{0:03d}".format(midCC94[midCH])),font=fontm,fill=(255,255,55))
              draw.text((tmx*18,tly+tmy*2+1),str("{0:04d}".format(0x80*pb2[midCH]+pb1[midCH]-8192)),font=fontm,fill=(255,255,55))
              mode0_write= True
              
       except :
        pass
       for forlch in range(16):
        if message[0] == 192+forlch :
           if midPRG[forlch] != message[1]:
              midPRG[forlch] = message[1]
              if mode == 0 and forlch==midCH:
                 draw.rectangle((tmx*5,tly+tmy+1,65,tly+tmy*2),(0,0,0))
                 draw.text((tmx*5,tly+tmy+1),str("{0:03d}".format(midPRG[midCH] + 1)),font=fontm,fill=(255,255,55))
                 mode0_write= True
                 
        if message[0] == 176+forlch and message[1] ==7:
           if midCC7[forlch] != message[2]:
              midCC7[forlch] = message[2]
              if mode == 0 and forlch==midCH:
                 draw.rectangle((tmx*5,tly+tmy*2+1,65,tly+tmy*3),(0,0,0))
                 draw.text((tmx*5,tly+tmy*2+1),str("{0:03d}".format(midCC7[midCH])),font=fontm,fill=(255,255,55))
                 mode0_write= True
                 
        if message[0] == 176+forlch and message[1] ==11:
           if midCC11[forlch] != message[2]:
              midCC11[forlch] = message[2]
              if mode == 0 and forlch==midCH:
                 draw.rectangle((tmx*5,tly+tmy*3+1,65,tly+tmy*4),(0,0,0))
                 draw.text((tmx*5,tly+tmy*3+1),str("{0:03d}".format(midCC11[midCH])),font=fontm,fill=(255,255,55))
                 mode0_write= True
                 
        if message[0] == 176+forlch and message[1] ==10:
           if midCC10[forlch] != message[2]:
              midCC10[forlch] = message[2] 
              if mode == 0 and forlch==midCH:
                 draw.rectangle((tmx*5,tly+tmy*4+1,65,tly+tmy*5),(0,0,0))
                 draw.text((tmx*5,tly+tmy*4+1),str("{0:03d}".format(midCC10[midCH]-64)),font=fontm,fill=(255,255,55))
                 mode0_write= True
                 
        if message[0] == 176+forlch and message[1] ==1:
           if midCC1[forlch] != message[2]:
              midCC1[forlch] = message[2]
              if mode == 0 and forlch==midCH:
                 draw.rectangle((tmx*5,tly+tmy*5+1,65,tly+tmy*6),(0,0,0))
                 draw.text((tmx*5,tly+tmy*5+1),str("{0:03d}".format(midCC1[midCH])),font=fontm,fill=(255,255,55))
                 mode0_write= True
                 
        if message[0] == 176+forlch and message[1] ==91:
           if midCC91[forlch] != message[2]:
              midCC91[forlch] = message[2]
              if mode == 0 and forlch==midCH:
                 draw.rectangle((tmx*5,tly+tmy*6+1,65,tly+tmy*7),(0,0,0))
                 draw.text((tmx*5,tly+tmy*6+1),str("{0:03d}".format(midCC91[midCH])),font=fontm,fill=(255,255,55))
                 mode0_write= True
                 
        if message[0] == 176+forlch and message[1] ==93:
           if midCC93[forlch] != message[2]:
              midCC93[forlch] = message[2]
              if mode == 0 and forlch==midCH:
                 draw.rectangle((tmx*5,tly+tmy*7+1,65,128),(0,0,0))
                 draw.text((tmx*5,tly+tmy*7+1),str("{0:03d}".format(midCC93[midCH])),font=fontm,fill=(255,255,55))
                 mode0_write= True
                 
        if message[0] == 176+forlch and message[1] ==94:
           if midCC94[forlch] != message[2]:
              midCC94[forlch] = message[2]
              if mode == 0 and forlch==midCH:
                 draw.rectangle((tmx*18,tly+tmy+1,160,tly+tmy*2),(0,0,0))
                 draw.text((tmx*18,tly+tmy+1),str("{0:03d}".format(midCC94[midCH])),font=fontm,fill=(255,255,55))
                 mode0_write= True
                 
        if message[0] == 0xe0+forlch :
           if pb1[forlch] != message[1] or pb2[forlch] != message[2]:
              pb1[forlch] = message[1]
              pb2[forlch] = message[2]
              if mode == 0 and forlch==midCH:
                 draw.rectangle((tmx*18,tly+tmy*2+1,160,tly+tmy*3),(0,0,0))
                 draw.text((tmx*18,tly+tmy*2+1),str("{0:04d}".format(0x80*pb2[forlch]+pb1[forlch]-8192)),font=fontm,fill=(255,255,55))
                 mode0_write= True
                 
##MIDI入力をディスプレイに反映する処理ここまで
def waiting(): #待ち状態の処理
   global waitflag
   while True:
      time.sleep(0.0001)
      if waitflag==1:
         draw.rectangle((tmx*6,tly+tmy+1,160,tly+tmy+14),outline=(0,0,0),fill=(0,0,0))
         draw.text((tmx*6,tly+tmy+1),"お待ちください",font=fontm,fill=(255,255,55))
         disp.display(img)
         time.sleep(0.5)
         if waitflag==1:
            draw.rectangle((tmx*6,tly+tmy+1,160,tly+tmy+14),outline=(0,0,0),fill=(0,0,0))
            draw.text((tmx*6,tly+tmy+1),"お待ちください.",font=fontm,fill=(255,255,55))        
            disp.display(img)
            time.sleep(0.5)
         if waitflag==1:
            draw.rectangle((tmx*6,tly+tmy+1,160,tly+tmy+14),outline=(0,0,0),fill=(0,0,0))
            draw.text((tmx*6,tly+tmy+1),"お待ちください..",font=fontm,fill=(255,255,55))        
            disp.display(img)
            time.sleep(0.5)
         if waitflag==1:
            draw.rectangle((tmx*6,tly+tmy+1,160,tly+tmy+14),outline=(0,0,0),fill=(0,0,0))
            draw.text((tmx*6,tly+tmy+1),"お待ちください...",font=fontm,fill=(255,255,55))
            disp.display(img)
            time.sleep(0.5)
      if waitflag==2:
         draw.rectangle((9,tly+tmy+1,160,tly+tmy*2+2),(0,0,0))
         draw.text((9,tly+tmy+1),"SSID:検索中",font=fontm,fill=(55,255,255))
         disp.display(img)
         time.sleep(0.5)
         if waitflag==2:
            draw.rectangle((9,tly+tmy+1,160,tly+tmy*2+2),(0,0,0))
            draw.text((9,tly+tmy+1),"SSID:検索中.",font=fontm,fill=(55,255,255))
            disp.display(img)
            time.sleep(0.5)
         if waitflag==2:
            draw.rectangle((9,tly+tmy+1,160,tly+tmy*2+2),(0,0,0))
            draw.text((9,tly+tmy+1),"SSID:検索中..",font=fontm,fill=(55,255,255))
            disp.display(img)
            time.sleep(0.5)
         if waitflag==2:
            draw.rectangle((9,tly+tmy+1,160,tly+tmy*2+2),(0,0,0))
            draw.text((9,tly+tmy+1),"SSID:検索中...",font=fontm,fill=(55,255,255))
            disp.display(img)        
            time.sleep(0.5)
            
      if waitflag==3:
         draw.rectangle((9,tly+tmy*2+1,160,tly+tmy*3+2),(0,0,0))
         draw.text((9,tly+tmy*2+1),"お待ちください",font=fontm,fill=(255,255,55))
         disp.display(img)
         time.sleep(0.5)
         if waitflag==3:
            draw.rectangle((9,tly+tmy*2+1,160,tly+tmy*3+2),(0,0,0))
            draw.text((9,tly+tmy*2+1),"お待ちください.",font=fontm,fill=(255,255,55))
            disp.display(img)
            time.sleep(0.5)
         if waitflag==3:
            draw.rectangle((9,tly+tmy*2+1,160,tly+tmy*3+2),(0,0,0))
            draw.text((9,tly+tmy*2+1),"お待ちください..",font=fontm,fill=(255,255,55))
            disp.display(img)
            time.sleep(0.5)
         if waitflag==3:
            draw.rectangle((9,tly+tmy*2+1,160,tly+tmy*3+2),(0,0,0))
            draw.text((9,tly+tmy*2+1),"お待ちください...",font=fontm,fill=(255,255,55))
            disp.display(img)        
            time.sleep(0.5)

      if waitflag==4:
         draw.rectangle((0,0,160,128),(0,0,0)) 
         draw.text((3,60)," アップデートしています",font=fontss,fill=(0,255,0))
         disp.display(img)
         time.sleep(0.5)
         if waitflag==4:
            draw.rectangle((0,0,160,128),(0,0,0)) 
            draw.text((3,60)," アップデートしています.",font=fontss,fill=(0,255,0))
            disp.display(img)
            time.sleep(0.5)
         if waitflag==4:
            draw.rectangle((0,0,160,128),(0,0,0)) 
            draw.text((3,60)," アップデートしています..",font=fontss,fill=(0,255,0))
            disp.display(img)
            time.sleep(0.5)
         if waitflag==4:
            draw.rectangle((0,0,160,128),(0,0,0)) 
            draw.text((3,60)," アップデートしています...",font=fontss,fill=(0,255,0))
            disp.display(img)        
            time.sleep(0.5)            

thread1 = threading.Thread(target=waiting)
thread1.start()

def mode0_default_disp(): #モード1(MIDIコントローラ)の表示
   global mode0_write
   draw.rectangle((0,0,160,128),(0,0,0))
   draw.text((mode0_coordi_xl[mode0_coordi],mode0_coordi_yl[mode0_coordi]),cur_size,font=fontss,fill=(255,255,255))
   draw.text((9,0),"CH:",font=fontl,fill=(55,255,255))
   draw.text((9,tly+tmy+1),"PC :",font=fontm,fill=(55,255,255))
   draw.text((9,tly+tmy*2+1),"VOL:",font=fontm,fill=(55,255,255))
   draw.text((9,tly+tmy*3+1),"EXP:",font=fontm,fill=(55,255,255))
   draw.text((9,tly+tmy*4+1),"PAN:",font=fontm,fill=(55,255,255))
   draw.text((9,tly+tmy*5+1),"MOD:",font=fontm,fill=(55,255,255))
   draw.text((9,tly+tmy*6+1),"REV:",font=fontm,fill=(55,255,255))
   draw.text((9,tly+tmy*7+1),"CHO:",font=fontm,fill=(55,255,255))
   draw.text((tlx*4,0),str("{0:02}".format(midCH + 1)),font=fontl,fill=(255,255,55))
   draw.text((tmx*5,tly+tmy+1),str("{0:03d}".format(midPRG[midCH] + 1)),font=fontm,fill=(255,255,55))
   draw.text((tmx*5,tly+tmy*2+1),str("{0:03d}".format(midCC7[midCH])),font=fontm,fill=(255,255,55))
   draw.text((tmx*5,tly+tmy*3+1),str("{0:03d}".format(midCC11[midCH])),font=fontm,fill=(255,255,55))
   draw.text((tmx*5,tly+tmy*4+1),str("{0:03d}".format(midCC10[midCH]-64)),font=fontm,fill=(255,255,55))
   draw.text((tmx*5,tly+tmy*5+1),str("{0:03d}".format(midCC1[midCH])),font=fontm,fill=(255,255,55))
   draw.text((tmx*5,tly+tmy*6+1),str("{0:03d}".format(midCC91[midCH])),font=fontm,fill=(255,255,55))
   draw.text((tmx*5,tly+tmy*7+1),str("{0:03d}".format(midCC93[midCH])),font=fontm,fill=(255,255,55))
   draw.text((csx+tmx*10,tly+tmy+1),"DLY   :",font=fontm,fill=(55,255,255))
   draw.text((tmx*18,tly+tmy+1),str("{0:03d}".format(midCC94[midCH])),font=fontm,fill=(255,255,55))
   draw.text((csx+tmx*10,tly+tmy*2+1),"P.BEND:",font=fontm,fill=(55,255,255))
   draw.text((tmx*18,tly+tmy*2+1),str("{0:04d}".format(0x80*pb2[midCH]+pb1[midCH]-8192)),font=fontm,fill=(255,255,55))
   draw.text((tlx*8,0),"SysVol: "+str(volume),font=fontss,fill=(0,255,0))
   mode0_write= True

def mode1_default_disp(): #モード2(シーケンサー)の表示
   draw.rectangle((0,0,160,128),(0,0,0))
   draw.text((mode1_coordi_xl[mode1_coordi],mode1_coordi_yl[mode1_coordi]),cur_size,font=fontss,fill=(255,255,255))
   draw.text((9,0),"SMF",font=fontl,fill=(255,255,55))
   draw.text((9,tly+tmy+1),"SF2:{0:03d}/{1:03d}" .format(sf2counter + 1 ,len(sf2)),font=fontm,fill=(55,255,255))
   draw.text((9,tly+tmy*3+1),"SMF:{0:03d}/{1:03d}".format(midicounter + 1 ,len(midi) ),font=fontm,fill=(55,255,255))
   draw.text((9,tly+tmy*2+1),sf2[sf2counter],font=fontm,fill=(255,255,55))
   if sf2used[sf2counter]==1:
      draw.text((9,tly+tmy+1),"            ♪",font=fontm,fill=(55,255,255))
   if playflag[midicounter]==1:
      draw.text((9,tly+tmy*3+1),"            ▶",font=fontm,fill=(55,255,255))
   draw.text((9,tly+tmy*4+1),midi[midicounter],font=fontm,fill=(255,255,55))
   draw.text((tlx*8,0),"SysVol: "+str(volume),font=fontss,fill=(0,255,0))
   disp.display(img)

def mode2_default_disp(): #モード(設定)の表示
   global wifi_connect
   wifi_connect=subprocess.check_output('''wpa_cli -i wlan0 status|grep -v bssid |grep ssid |sed -e 's/ssid=//g' ''' ,shell=True).decode('utf-8').strip()
   if wifi_connect=="" and wifi_connect!="お待ちください...":
      wifi_connect="接続できません" 
   draw.rectangle((0,0,160,128),(0,0,0))
   draw.text((mode2_coordi_xl[mode2_coordi],mode2_coordi_yl[mode2_coordi]),cur_size,font=fontss,fill=(255,255,255))
   draw.text((9,0),"設定",font=fontl,fill=(255,255,55))
   draw.text((9,tly+tmy+1),"WiFi:",font=fontm,fill=(55,255,255))
   draw.text((9,tly+tmy*2+1),"Audio:",font=fontm,fill=(55,255,255))
   draw.text((9,tly+tmy*3+1),"USBメモリ",font=fontm,fill=(55,255,255))
   draw.text((9,tly+tmy*4+1),"Ysynth4アップデート",font=fontm,fill=(55,255,255))
   draw.text((9,tly+tmy*5+1),"再起動",font=fontm,fill=(55,255,255))
   draw.text((9,tly+tmy*6+1),"シャットダウン",font=fontm,fill=(55,255,255))
   draw.text((9,tly+tmy*7+1),"リロード",font=fontm,fill=(55,255,255))
   draw.text((tmx*6,tly+tmy+1),wifi_connect,font=fontm,fill=(255,255,55))
   draw.text((tmx*7,tly+tmy*2+1),audio_card,font=fontm,fill=(255,255,55))
   draw.text((tlx*8,0),"SysVol: "+str(volume),font=fontss,fill=(0,255,0))
   disp.display(img)
def mode3_default_disp(): #モード3(WiFi選択)の表示
   global wifi,wificounter,waitflag
   wificounter=0
   draw.rectangle((0,0,160,128),(0,0,0))
   draw.text((9,0),"WiFi",font=fontl,fill=(255,255,55))
   draw.text((tlx*8,0),"SysVol: "+str(volume),font=fontss,fill=(0,255,0))
   waitflag=2
   wifi=subprocess.check_output('''iwlist wlan0 scan| grep ESSID |sed -e 's/ESSID://g' -e 's/[ ]//g' -e 's/"//g'|sort ''' ,shell=True).decode('utf-8').strip().split('\n')
   if len(wifi)>1:
      wifi= [s for s in wifi if s != ""]
   if wifi[0]=="":
      wifi[0]="見つかりませんでした"
   waitflag=0
   draw.rectangle((9+tmx*5,tly+tmy+1,160,tly+tmy*2+2),(0,0,0))
   draw.text((9,tly+tmy+1),"     {0:03d}/{1:03d}" .format(wificounter + 1,len(wifi)),font=fontm,fill=(55,255,255))
   draw.text((mode2_coordi_xl[1],mode2_coordi_yl[1]),cur_size,font=fontss,fill=(255,255,255))
   draw.text((9,tly+tmy*2+1),wifi[wificounter],font=fontm,fill=(255,255,55))
   disp.display(img)

def dialog_window0(): #ダイアログのウィンドウを開く1種類目（※これ以外ないです）
   draw.rectangle((10,tly+tmy+1,150,110),outline=(255,255,255),fill=(217,207,201))
   draw.rectangle((10,tly+tmy+5,150,20),outline=(217,207,201),fill=(8,34,109))
   draw.text((12,22),"確認",font=fontss,fill=(255,255,255))
   draw.rectangle((20,90,70,90+tsy),outline=(100,100,100),fill=(217,207,201))
   draw.rectangle((90,90,140,90+tsy),outline=(100,100,100),fill=(217,207,201))
   draw.text((34,90),"はい",font=fontss,fill=(0,0,0))
   draw.text((98,90),"いいえ",font=fontss,fill=(0,0,0))
   disp.display(img)
   
def longpush_(button): #長押し
    global longpush
    while (GPIO.input(button) == 0 and longpush !=100): 
          time.sleep(0.01)
          longpush +=1
          if longpush==100:
             break
          else:
             continue

def dialog_loop0(txt,cmd): #ダイアログの選択待ち
    global dlog_zahyo,dlog_zahyo_xl,dlog_zahyo_yl,longpush
    while (GPIO.input(input_OK)) == 0: 
          continue 
    while True:
       time.sleep(0.0001)   
       if GPIO.input(input_RIGHT) == 0 :
          time.sleep(0.01)
          draw.rectangle((dlog_zahyo_xl[dlog_zahyo],dlog_zahyo_yl[dlog_zahyo],dlog_zahyo_xl[dlog_zahyo]+csx,dlog_zahyo_yl[dlog_zahyo]+csy),(217,207,201))
          dlog_zahyo +=1
          if dlog_zahyo >1:
             dlog_zahyo=0
          draw.text((dlog_zahyo_xl[dlog_zahyo],dlog_zahyo_yl[dlog_zahyo]),cur_size,font=fontss,fill=(0,0,0))
          disp.display(img)
          longpush_(input_RIGHT)
       if GPIO.input(input_LEFT) == 0 :
          time.sleep(0.01)
          draw.rectangle((dlog_zahyo_xl[dlog_zahyo],dlog_zahyo_yl[dlog_zahyo],dlog_zahyo_xl[dlog_zahyo]+csx,dlog_zahyo_yl[dlog_zahyo]+csy),(217,207,201))
          dlog_zahyo -=1
          if dlog_zahyo <0:
             dlog_zahyo=1
          draw.text((dlog_zahyo_xl[dlog_zahyo],dlog_zahyo_yl[dlog_zahyo]),cur_size,font=fontss,fill=(0,0,0))   
          disp.display(img)
          longpush_(input_LEFT)
       if GPIO.input(input_OK) == 0:
          time.sleep(0.05)
          if dlog_zahyo==0:
             subprocess.Popen(cmd ,shell=True)
             draw.rectangle((0,0,160,128),(0,0,0)) 
             draw.text((3,60),txt,font=fontss,fill=(0,255,0))
             disp.display(img)
             time.sleep(3)
             draw.rectangle((0,0,160,128),(0,0,0)) 
             time.sleep(1)
             break
          if dlog_zahyo==1:
             mode2_default_disp()
             while (GPIO.input(input_OK)) == 0: 
                   continue 
             break
       if (GPIO.input(input_LEFT) and GPIO.input(input_RIGHT))== 1 and longpush !=0:  
          longpush=0 
def sc_key(): #スクリーンキーボード
   global longpush,mode,dialog_open,wifi,wificounter,wifi_psk,wifi_conf,waitflag
   moji_in=[]
   wifi_psk=["",""]
   wifi_conf=subprocess.check_output('''grep ssid /etc/wpa_supplicant/wpa_supplicant.conf|sed -e 's/ssid=//g' -e 's/"//g' -e 's/psk=//g' -e 's/^[ \t]*//g' ''' ,shell=True).decode('utf-8').strip().split('\n')
   wifi_conf_check=wifi[wificounter] in wifi_conf
   if wifi_conf_check is True:
      wifi_psk=subprocess.check_output('''grep {} -m1 -A 1 /etc/wpa_supplicant/wpa_supplicant.conf|sed -e 's/ssid=//g' -e 's/"//g' -e 's/psk=//g' -e 's/^[ \t]*//g' ''' .format(wifi[wificounter]),shell=True).decode('utf-8').strip().split('\n')
      moji_in=wifi_psk[1]
   shift=0
   moji=["1","2","3","4","5","6","7","8","9","0","-","BS","q","w","e","r","t","y","u","i",\
   "o","p","","⏎","a","s","d","f","g","h","j","k","l",":","'","`","z","x","c","v","b","n",\
      "m",",",".","/","=","@"]
   draw.rectangle((0,61,160,76),outline=(0,0,0),fill=(255,255,255))
   for k in range(48):
    k_size_x,k_size_y  = draw.textsize(moji[k],fonts)
    moji_center_w=(13-k_size_x)/2+1
    draw.rectangle((13*(k-12*(k//12)),76+13*(k//12),13*(1+k-12*(k//12)),76+13*((k//12)+1)),outline=(0,0,0),fill=(217,207,201))
    draw.text((13*(k-12*(k//12))+moji_center_w,76+13*(k//12)),moji[k],font=fonts,fill=(0,0,0))
   draw.rectangle((0,76,13,76+13),outline=(217,207,201),fill=(8,34,109))
   draw.text((4,76),moji[0],font=fonts,fill=(255,255,255))
   moji_in=("".join(map(str,moji_in)))
   draw.text((1,61),moji_in,font=fonts,fill=(0,0,0))
   disp.display(img)
   moji_in=list(moji_in)
   sk_zahyo = 0
   #sckey_coordi = sk_zahyo

   while True:
      time.sleep(0.001)
      sk_zahyo_size_x,sk_zahyo_size_y  = draw.textsize(moji[sk_zahyo],fonts)
      moji_center_w=(13-sk_zahyo_size_x)/2+1
      if GPIO.input(input_LEFT) == 0:
         draw.rectangle((13*(sk_zahyo-12*(sk_zahyo//12)),76+13*(sk_zahyo//12),13*(1+sk_zahyo-12*(sk_zahyo//12)),76+13*((sk_zahyo//12)+1)),outline=(0,0,0),fill=(217,207,201))
         if moji[sk_zahyo]=="_":
            draw.text((13*(sk_zahyo-12*(sk_zahyo//12))+moji_center_w,76+13*(sk_zahyo//12)-2),moji[sk_zahyo],font=fonts,fill=(0,0,0))
         else:
            draw.text((13*(sk_zahyo-12*(sk_zahyo//12))+moji_center_w,76+13*(sk_zahyo//12)),moji[sk_zahyo],font=fonts,fill=(0,0,0))
         sk_zahyo -= 1
         if sk_zahyo==-1 or sk_zahyo==11 or sk_zahyo==23 or sk_zahyo==35:
            sk_zahyo += 12
         sk_zahyo_size_x,sk_zahyo_size_y  = draw.textsize(moji[sk_zahyo],fonts)
         moji_center_w=(13-sk_zahyo_size_x)/2+1
         draw.rectangle((13*(sk_zahyo-12*(sk_zahyo//12)),76+13*(sk_zahyo//12),13*(1+sk_zahyo-12*(sk_zahyo//12)),76+13*((sk_zahyo//12)+1)),outline=(217,207,201),fill=(8,34,109))
         if moji[sk_zahyo]=="_":
            draw.text((13*(sk_zahyo-12*(sk_zahyo//12))+moji_center_w,76+13*(sk_zahyo//12)-2),moji[sk_zahyo],font=fonts,fill=(255,255,255))
         else:
            draw.text((13*(sk_zahyo-12*(sk_zahyo//12))+moji_center_w,76+13*(sk_zahyo//12)),moji[sk_zahyo],font=fonts,fill=(255,255,255))
         disp.display(img) 
         longpush_(input_LEFT)
      if GPIO.input(input_RIGHT) == 0:  
         draw.rectangle((13*(sk_zahyo-12*(sk_zahyo//12)),76+13*(sk_zahyo//12),13*(1+sk_zahyo-12*(sk_zahyo//12)),76+13*((sk_zahyo//12)+1)),outline=(0,0,0),fill=(217,207,201))
         if moji[sk_zahyo]=="_":
            draw.text((13*(sk_zahyo-12*(sk_zahyo//12))+moji_center_w,76+13*(sk_zahyo//12)-2),moji[sk_zahyo],font=fonts,fill=(0,0,0))
         else:
            draw.text((13*(sk_zahyo-12*(sk_zahyo//12))+moji_center_w,76+13*(sk_zahyo//12)),moji[sk_zahyo],font=fonts,fill=(0,0,0))
         sk_zahyo += 1
         if sk_zahyo==12 or sk_zahyo==24 or sk_zahyo==36 or sk_zahyo==48:
            sk_zahyo -= 12
         sk_zahyo_size_x,sk_zahyo_size_y  = draw.textsize(moji[sk_zahyo],fonts)
         moji_center_w=(13-sk_zahyo_size_x)/2+1
         draw.rectangle((13*(sk_zahyo-12*(sk_zahyo//12)),76+13*(sk_zahyo//12),13*(1+sk_zahyo-12*(sk_zahyo//12)),76+13*((sk_zahyo//12)+1)),outline=(217,207,201),fill=(8,34,109))
         if moji[sk_zahyo]=="_":
            draw.text((13*(sk_zahyo-12*(sk_zahyo//12))+moji_center_w,76+13*(sk_zahyo//12)-2),moji[sk_zahyo],font=fonts,fill=(255,255,255))
         else:
            draw.text((13*(sk_zahyo-12*(sk_zahyo//12))+moji_center_w,76+13*(sk_zahyo//12)),moji[sk_zahyo],font=fonts,fill=(255,255,255))
         disp.display(img) 
         longpush_(input_RIGHT)
      if GPIO.input(input_UP) == 0:
         draw.rectangle((13*(sk_zahyo-12*(sk_zahyo//12)),76+13*(sk_zahyo//12),13*(1+sk_zahyo-12*(sk_zahyo//12)),76+13*((sk_zahyo//12)+1)),outline=(0,0,0),fill=(217,207,201))
         if moji[sk_zahyo]=="_":
            draw.text((13*(sk_zahyo-12*(sk_zahyo//12))+moji_center_w,76+13*(sk_zahyo//12)-2),moji[sk_zahyo],font=fonts,fill=(0,0,0))
         else:
            draw.text((13*(sk_zahyo-12*(sk_zahyo//12))+moji_center_w,76+13*(sk_zahyo//12)),moji[sk_zahyo],font=fonts,fill=(0,0,0))
         sk_zahyo -= 12
         if sk_zahyo <=-1:
            sk_zahyo += 48
         sk_zahyo_size_x,sk_zahyo_size_y  = draw.textsize(moji[sk_zahyo],fonts)
         moji_center_w=(13-sk_zahyo_size_x)/2+1
         draw.rectangle((13*(sk_zahyo-12*(sk_zahyo//12)),76+13*(sk_zahyo//12),13*(1+sk_zahyo-12*(sk_zahyo//12)),76+13*((sk_zahyo//12)+1)),outline=(217,207,201),fill=(8,34,109))
         if moji[sk_zahyo]=="_":
            draw.text((13*(sk_zahyo-12*(sk_zahyo//12))+moji_center_w,76+13*(sk_zahyo//12)-2),moji[sk_zahyo],font=fonts,fill=(255,255,255))
         else:
            draw.text((13*(sk_zahyo-12*(sk_zahyo//12))+moji_center_w,76+13*(sk_zahyo//12)),moji[sk_zahyo],font=fonts,fill=(255,255,255))
         disp.display(img) 
         longpush_(input_UP)
      if GPIO.input(input_DOWN) == 0:   
         draw.rectangle((13*(sk_zahyo-12*(sk_zahyo//12)),76+13*(sk_zahyo//12),13*(1+sk_zahyo-12*(sk_zahyo//12)),76+13*((sk_zahyo//12)+1)),outline=(0,0,0),fill=(217,207,201))
         if moji[sk_zahyo]=="_":
            draw.text((13*(sk_zahyo-12*(sk_zahyo//12))+moji_center_w,76+13*(sk_zahyo//12)-2),moji[sk_zahyo],font=fonts,fill=(0,0,0))
         else:
            draw.text((13*(sk_zahyo-12*(sk_zahyo//12))+moji_center_w,76+13*(sk_zahyo//12)),moji[sk_zahyo],font=fonts,fill=(0,0,0))
         sk_zahyo += 12  
         if sk_zahyo >=48:
            sk_zahyo -= 48
         sk_zahyo_size_x,sk_zahyo_size_y  = draw.textsize(moji[sk_zahyo],fonts)
         moji_center_w=(13-sk_zahyo_size_x)/2+1
         draw.rectangle((13*(sk_zahyo-12*(sk_zahyo//12)),76+13*(sk_zahyo//12),13*(1+sk_zahyo-12*(sk_zahyo//12)),76+13*((sk_zahyo//12)+1)),outline=(217,207,201),fill=(8,34,109))
         if moji[sk_zahyo]=="_":
            draw.text((13*(sk_zahyo-12*(sk_zahyo//12))+moji_center_w,76+13*(sk_zahyo//12)-2),moji[sk_zahyo],font=fonts,fill=(255,255,255))
         else:
            draw.text((13*(sk_zahyo-12*(sk_zahyo//12))+moji_center_w,76+13*(sk_zahyo//12)),moji[sk_zahyo],font=fonts,fill=(255,255,255))
         disp.display(img) 
         longpush_(input_DOWN)
      if GPIO.input(input_OK) == 0 : 
         if sk_zahyo !=11 and sk_zahyo !=23 and len(moji_in) < 22:
            draw.rectangle((0,61,160,76),outline=(0,0,0),fill=(255,255,255))
            moji_in.append(moji[sk_zahyo] )
            moji_in=("".join(map(str,moji_in)))
            draw.text((1,61),moji_in,font=fonts,fill=(0,0,0))
            disp.display(img)
            moji_in=list(moji_in)
         if sk_zahyo == 11 and moji_in !=[]:
            draw.rectangle((0,61,160,76),outline=(0,0,0),fill=(255,255,255))
            moji_in.pop()
            moji_in=("".join(map(str,moji_in)))
            draw.text((1,61),moji_in,font=fonts,fill=(0,0,0))
            disp.display(img)
            moji_in=list(moji_in)
         if sk_zahyo == 23 :
            moji_in=("".join(map(str,moji_in)))
            if wifi_psk[1]==moji_in and wifi_psk[1] !="" and moji_in !="":
               mode2_default_disp()
               waitflag=1
               wpa_list=subprocess.check_output('''grep ssid /etc/wpa_supplicant/wpa_supplicant.conf|sed -e 's/ssid=//g' -e 's/[ ]//g' -e 's/"//g' ''',shell=True).decode('utf=8').strip().split('\n')
               subprocess.call('''sudo ifconfig wlan0 down''',shell=True)
               subprocess.call('''sudo ifconfig wlan0 up''',shell=True)
               subprocess.call('''sudo wpa_cli -i wlan0 reconfigure''',shell=True)
               if wifi[wificounter] in wpa_list:
                  wpa_list_index=wpa_list.index(wifi[wificounter])
                  subprocess.check_output('''sudo wpa_cli -i wlan0 select_network {}'''.format(wpa_list_index) ,shell=True)
               else:
                  pass
               time.sleep(6)
               waitflag=0
               mode2_default_disp()
               mode=2
               dialog_open=0
               longpush_(input_OK)
               break
            if wifi_psk[1]==moji_in and wifi_psk[1] =="" and moji_in =="":
               mode2_default_disp()
               mode=2
               dialog_open=0
               longpush_(input_OK)
               break
            if wifi_psk[1] !="" and moji_in !="" and wifi_psk[1] !=moji_in:
               mode2_default_disp()
               waitflag=1
               delconf=subprocess.check_output('''grep -A 2 -B 1 {} -n /etc/wpa_supplicant/wpa_supplicant.conf| sed -e 's/:.*//g' -e 's/-.*//g' ''' .format(wifi[wificounter]) ,shell=True).decode('utf-8').strip().split('\n')
               subprocess.call('''sudo sed -i '{},{}d' /etc/wpa_supplicant/wpa_supplicant.conf ''' .format(delconf[0],delconf[len(delconf)-1]) ,shell=True)
               subprocess.call('''sudo sed -i -e '$ a network={' /etc/wpa_supplicant/wpa_supplicant.conf''' ,shell=True)
               subprocess.call('''sudo sed -i -e '$ a \        ssid="{}"' /etc/wpa_supplicant/wpa_supplicant.conf''' .format(wifi[wificounter]),shell=True)
               subprocess.call('''sudo sed -i -e '$ a \        psk="{}"' /etc/wpa_supplicant/wpa_supplicant.conf''' .format(moji_in),shell=True)
               subprocess.call('''sudo sed -i -e '$ a }' /etc/wpa_supplicant/wpa_supplicant.conf''' ,shell=True)
               subprocess.call('''sudo ifconfig wlan0 down''',shell=True)
               subprocess.call('''sudo ifconfig wlan0 up''',shell=True)
               wpa_reconfigure=subprocess.check_output('''sudo wpa_cli -i wlan0 reconfigure''',shell=True).strip().decode('utf-8')
               if wpa_reconfigure=="FAIL":
                  delconf=subprocess.check_output('''grep -A 2 -B 1 {} -n /etc/wpa_supplicant/wpa_supplicant.conf| sed -e 's/:.*//g' -e 's/-.*//g' ''' .format(wifi[wificounter]) ,shell=True).decode('utf-8').strip().split('\n')
                  subprocess.call('''sudo sed -i '{},{}d' /etc/wpa_supplicant/wpa_supplicant.conf ''' .format(delconf[0],delconf[len(delconf)-1]) ,shell=True)
                  subprocess.call('''sudo sed -i -e '$ a network={' /etc/wpa_supplicant/wpa_supplicant.conf''' ,shell=True)
                  subprocess.call('''sudo sed -i -e '$ a \        ssid="{}"' /etc/wpa_supplicant/wpa_supplicant.conf''' .format(wifi[wificounter]),shell=True)
                  subprocess.call('''sudo sed -i -e '$ a \        psk="{}"' /etc/wpa_supplicant/wpa_supplicant.conf''' .format(wifi_psk[1] ),shell=True)
                  subprocess.call('''sudo sed -i -e '$ a }' /etc/wpa_supplicant/wpa_supplicant.conf''' ,shell=True)
                  subprocess.call('''sudo ifconfig wlan0 down''',shell=True)
                  subprocess.call('''sudo ifconfig wlan0 up''',shell=True)
                  subprocess.call('''sudo wpa_cli -i wlan0 reconfigure''',shell=True)
               wpalist=subprocess.check_output('''grep ssid /etc/wpa_supplicant/wpa_supplicant.conf|sed -e 's/ssid=//g' -e 's/[ ]//g' -e 's/"//g' ''',shell=True).decode('utf=8').strip().split('\n')
               if wifi[wificounter] in wpalist:
                  wpa_list_index=wpalist.index(wifi[wificounter])
                  subprocess.check_output('''sudo wpa_cli -i wlan0 select_network {}'''.format(wpa_list_index) ,shell=True)
               else:
                  pass
               time.sleep(6)
               waitflag=0
               mode2_default_disp()
               mode=2
               dialog_open=0
               longpush_(input_OK)
               break
            if wifi_psk[1] =="":
               mode2_default_disp()
               waitflag=1
               subprocess.call('''sudo sed -i -e '$ a network={' /etc/wpa_supplicant/wpa_supplicant.conf''' ,shell=True)
               subprocess.call('''sudo sed -i -e '$ a \        ssid="{}"' /etc/wpa_supplicant/wpa_supplicant.conf''' .format(wifi[wificounter]),shell=True)
               subprocess.call('''sudo sed -i -e '$ a \        psk="{}"' /etc/wpa_supplicant/wpa_supplicant.conf''' .format(moji_in),shell=True)
               subprocess.call('''sudo sed -i -e '$ a }' /etc/wpa_supplicant/wpa_supplicant.conf''' ,shell=True)
               subprocess.call('''sudo ifconfig wlan0 down''',shell=True)
               subprocess.call('''sudo ifconfig wlan0 up''',shell=True)
               wpa_reconfigure=subprocess.check_output('''sudo wpa_cli -i wlan0 reconfigure''',shell=True).strip().decode('utf-8')
               if wpa_reconfigure=="FAIL":
                  delconf=subprocess.check_output('''grep -A 2 -B 1 {} -n /etc/wpa_supplicant/wpa_supplicant.conf| sed -e 's/:.*//g' -e 's/-.*//g' ''' .format(wifi[wificounter]) ,shell=True).decode('utf-8').strip().split('\n')
                  subprocess.call('''sudo sed -i '{},{}d' /etc/wpa_supplicant/wpa_supplicant.conf ''' .format(delconf[0],delconf[len(delconf)-1]) ,shell=True)
                  subprocess.call('''sudo ifconfig wlan0 down''',shell=True)
                  subprocess.call('''sudo ifconfig wlan0 up''',shell=True)
                  subprocess.call('''sudo wpa_cli -i wlan0 reconfigure''',shell=True)
               wpalist=subprocess.check_output('''grep ssid /etc/wpa_supplicant/wpa_supplicant.conf|sed -e 's/ssid=//g' -e 's/[ ]//g' -e 's/"//g' ''',shell=True).decode('utf=8').strip().split('\n')
               if wifi[wificounter] in wpalist:
                  wpa_list_index=wpalist.index(wifi[wificounter])
                  subprocess.check_output('''sudo wpa_cli -i wlan0 select_network {}'''.format(wpa_list_index) ,shell=True)
               else:
                  pass
               time.sleep(6)
               waitflag=0
               mode2_default_disp()
               mode=2
               dialog_open=0
               longpush_(input_OK)
               break
            if moji_in =="":
               mode2_default_disp()
               waitflag=1
               delconf=subprocess.check_output('''grep -A 2 -B 1 {} -n /etc/wpa_supplicant/wpa_supplicant.conf| sed -e 's/:.*//g' -e 's/-.*//g' ''' .format(wifi[wificounter]) ,shell=True).decode('utf-8').strip().split('\n')
               subprocess.call('''sudo sed -i '{},{}d' /etc/wpa_supplicant/wpa_supplicant.conf ''' .format(delconf[0],delconf[len(delconf)-1]) ,shell=True)
               subprocess.call('''sudo ifconfig wlan0 down''',shell=True)
               subprocess.call('''sudo ifconfig wlan0 up''',shell=True)
               subprocess.call('''sudo wpa_cli -i wlan0 reconfigure''',shell=True)
               time.sleep(6)
               waitflag=0
               mode2_default_disp()
               mode=2
               dialog_open=0
               longpush_(input_OK)               
               break
         longpush_(input_OK)
      if GPIO.input(input_MODE) == 0 and shift==0: 
         shift=1
         moji=["!","\\","#","＄","%","^","&","*","(",")","_","BS","Q","W","E","R","T","Y","U","I",\
         "O","P","","⏎","A","S","D","F","G","H","J","K","L",";",'"',"~","Z","X","C","V","B","N",\
            "M","<",">","?","+","|"]
         for k in range(48):
          k_size_x,k_size_y  = draw.textsize(moji[k],fonts)
          moji_center_w=(13-k_size_x)/2+1
          draw.rectangle((13*(k-12*(k//12)),76+13*(k//12),13*(1+k-12*(k//12)),76+13*((k//12)+1)),outline=(0,0,0),fill=(217,207,201))
          if moji[k]=="_":
             draw.text((13*(k-12*(k//12))+moji_center_w,76+13*(k//12)-2),moji[k],font=fonts,fill=(0,0,0))
          else:
            draw.text((13*(k-12*(k//12))+moji_center_w,76+13*(k//12)),moji[k],font=fonts,fill=(0,0,0))
         sk_zahyo_size_x,sk_zahyo_size_y  = draw.textsize(moji[sk_zahyo],fonts)
         moji_center_w=(13-sk_zahyo_size_x)/2+1
         draw.rectangle((13*(sk_zahyo-12*(sk_zahyo//12)),76+13*(sk_zahyo//12),13*(1+sk_zahyo-12*(sk_zahyo//12)),76+13*((sk_zahyo//12)+1)),outline=(217,207,201),fill=(8,34,109))
         if moji[sk_zahyo]=="_":
            draw.text((13*(sk_zahyo-12*(sk_zahyo//12))+moji_center_w,76+13*(sk_zahyo//12)-2),moji[sk_zahyo],font=fonts,fill=(255,255,255))
         else:
            draw.text((13*(sk_zahyo-12*(sk_zahyo//12))+moji_center_w,76+13*(sk_zahyo//12)),moji[sk_zahyo],font=fonts,fill=(255,255,255))
         disp.display(img)

      if GPIO.input(input_MODE) == 1 and shift==1:
         shift=0
         moji=["1","2","3","4","5","6","7","8","9","0","-","BS","q","w","e","r","t","y","u","i",\
            "o","p"," ","⏎","a","s","d","f","g","h","j","k","l",":","'","`","z","x","c","v","b","n",\
               "m",",",".","/","=","@"]
         for k in range(48):
          k_size_x,k_size_y  = draw.textsize(moji[k],fonts)
          moji_center_w=(13-k_size_x)/2+1
          draw.rectangle((13*(k-12*(k//12)),76+13*(k//12),13*(1+k-12*(k//12)),76+13*((k//12)+1)),outline=(0,0,0),fill=(217,207,201))
          draw.text((13*(k-12*(k//12))+moji_center_w,76+13*(k//12)),moji[k],font=fonts,fill=(0,0,0))
         sk_zahyo_size_x,sk_zahyo_size_y  = draw.textsize(moji[sk_zahyo],fonts)
         moji_center_w=(13-sk_zahyo_size_x)/2+1
         draw.rectangle((13*(sk_zahyo-12*(sk_zahyo//12)),76+13*(sk_zahyo//12),13*(1+sk_zahyo-12*(sk_zahyo//12)),76+13*((sk_zahyo//12)+1)),outline=(217,207,201),fill=(8,34,109))
         draw.text((13*(sk_zahyo-12*(sk_zahyo//12))+moji_center_w,76+13*(sk_zahyo//12)),moji[sk_zahyo],font=fonts,fill=(255,255,255))
         disp.display(img)
      if (GPIO.input(input_LEFT) and GPIO.input(input_RIGHT) and GPIO.input(input_UP) and GPIO.input(input_DOWN) and GPIO.input(input_OK))== 1:  
         longpush=0

##初期設定ここまで##
time.sleep(1)
msg = None
mode0_default_disp()
disp.display(img)


def ysynthmain():
 global longpush,volume,sf2,midi,mode0_coordi,mode1_coordi,mode2_coordi,mode3_coordi,mode0_coordi_xl,mode0_coordi_yl,\
    mode1_coordi_xl,mode1_coordi_yl,mode2_coordi_xl,mode2_coordi_yl,mode3_coordi_xl,mode3_coordi_yl,midicounter,\
       playflag,sf2counter,sf2used,mode,midCH,midPRG,midCC7,midCC11,midCC10,midCC10,midCC1,midCC91,\
          midCC93,midCC94,pb1,pb2,dlog_zahyo,wifi,wificounter,dialog_open,mode0_write,waitflag,mountcheck
 while True:
    time.sleep(0.01)
    try:
     if aplaymidi.poll() is not None:
        if mode == 1 and playflag[midicounter] == 1:
           draw.rectangle((tmx*13,tly+tmy*3+1,160,tly+tmy*4+2),(0,0,0))
           disp.display(img)
        playflag = [0]*len(midi)
    except:
     pass
    if GPIO.input(input_LEFT) == 0 and GPIO.input(input_MODE) != 0: 
       time.sleep(0.0001)
       if mode==0:
          if mode0_coordi ==0:
             midCH -=1
             if midCH<0:
                midCH=15 
             draw.rectangle((tlx*4,0,tlx*6,tly),(0,0,0))
             draw.text((tlx*4,0),str("{0:02}".format(midCH + 1)),font=fontl,fill=(255,255,55))
             draw.rectangle((tmx*5,tly+tmy+1,65,128),(0,0,0))
             draw.text((tmx*5,tly+tmy+1),str("{0:03d}".format(midPRG[midCH] + 1)),font=fontm,fill=(255,255,55))
             draw.text((tmx*5,tly+tmy*2+1),str("{0:03d}".format(midCC7[midCH])),font=fontm,fill=(255,255,55))
             draw.text((tmx*5,tly+tmy*3+1),str("{0:03d}".format(midCC11[midCH])),font=fontm,fill=(255,255,55))
             draw.text((tmx*5,tly+tmy*4+1),str("{0:03d}".format(midCC10[midCH]-64)),font=fontm,fill=(255,255,55))
             draw.text((tmx*5,tly+tmy*5+1),str("{0:03d}".format(midCC1[midCH])),font=fontm,fill=(255,255,55))
             draw.text((tmx*5,tly+tmy*6+1),str("{0:03d}".format(midCC91[midCH])),font=fontm,fill=(255,255,55))
             draw.text((tmx*5,tly+tmy*7+1),str("{0:03d}".format(midCC93[midCH])),font=fontm,fill=(255,255,55))
             draw.rectangle((tmx*18,tly+tmy+1,160,128),(0,0,0))
             draw.text((tmx*18,tly+tmy+1),str("{0:03d}".format(midCC94[midCH])),font=fontm,fill=(255,255,55))
             draw.text((tmx*18,tly+tmy*2+1),str("{0:04d}".format(0x80*pb2[midCH]+pb1[midCH]-8192)),font=fontm,fill=(255,255,55))       
             mode0_write= True
             
          if mode0_coordi ==1:
             midPRG[midCH] -=1
             if midPRG[midCH] <0:
                midPRG[midCH] =127
             draw.rectangle((tmx*5,tly+tmy+1,65,tly+tmy*2),(0,0,0))
             draw.text((tmx*5,tly+tmy+1),str("{0:03d}".format(midPRG[midCH] + 1)),font=fontm,fill=(255,255,55))
             mode0_write= True
             
             midiout.send_message([0xc0+midCH,midPRG[midCH]])
          if mode0_coordi ==2:
             midCC7[midCH] -=1
             if midCC7[midCH] <0:
                midCC7[midCH] =127
             draw.rectangle((tmx*5,tly+tmy*2+1,65,tly+tmy*3),(0,0,0))
             draw.text((tmx*5,tly+tmy*2+1),str("{0:03d}".format(midCC7[midCH])),font=fontm,fill=(255,255,55))
             mode0_write= True
             
             midiout.send_message([0xb0+midCH,7,midCC7[midCH]])
          if mode0_coordi ==3:
             midCC11[midCH] -=1
             if midCC11[midCH] <0:
                midCC11[midCH] =127
             draw.rectangle((tmx*5,tly+tmy*3+1,65,tly+tmy*4),(0,0,0))
             draw.text((tmx*5,tly+tmy*3+1),str("{0:03d}".format(midCC11[midCH])),font=fontm,fill=(255,255,55))
             mode0_write= True
              
             midiout.send_message([0xb0+midCH,11,midCC11[midCH]]) 
          if mode0_coordi ==4:
             midCC10[midCH] -=1
             if midCC10[midCH] <0:
                midCC10[midCH] =127
             draw.rectangle((tmx*5,tly+tmy*4+1,65,tly+tmy*5),(0,0,0))
             draw.text((tmx*5,tly+tmy*4+1),str("{0:03d}".format(midCC10[midCH]-64)),font=fontm,fill=(255,255,55))
             mode0_write= True
             
             midiout.send_message([0xb0+midCH,10,midCC10[midCH]])
          if mode0_coordi ==5:
             midCC1[midCH] -=1
             if midCC1[midCH] <0:
                midCC1[midCH] =127
             draw.rectangle((tmx*5,tly+tmy*5+1,65,tly+tmy*6),(0,0,0))
             draw.text((tmx*5,tly+tmy*5+1),str("{0:03d}".format(midCC1[midCH])),font=fontm,fill=(255,255,55))
             mode0_write= True
             
             midiout.send_message([0xb0+midCH,1,midCC1[midCH]])
          if mode0_coordi ==6:
             midCC91[midCH] -=1
             if midCC91[midCH] <0:
                midCC91[midCH] =127
             draw.rectangle((tmx*5,tly+tmy*6+1,65,tly+tmy*7),(0,0,0))
             draw.text((tmx*5,tly+tmy*6+1),str("{0:03d}".format(midCC91[midCH])),font=fontm,fill=(255,255,55))
             mode0_write= True
             
             midiout.send_message([0xb0+midCH,91,midCC91[midCH]])
          if mode0_coordi ==7:
             midCC93[midCH] -=1
             if midCC93[midCH] <0:
                midCC93[midCH] =127
             draw.rectangle((tmx*5,tly+tmy*7+1,65,128),(0,0,0))
             draw.text((tmx*5,tly+tmy*7+1),str("{0:03d}".format(midCC93[midCH])),font=fontm,fill=(255,255,55))
             midiout.send_message([0xb0+midCH,93,midCC93[midCH]])
             mode0_write= True
             
          if mode0_coordi ==8:
             midCC94[midCH] -=1
             if midCC94[midCH] <0:
                midCC94[midCH] =127
             draw.rectangle((tmx*18,tly+tmy+1,160,tly+tmy*2),(0,0,0))
             draw.text((tmx*18,tly+tmy+1),str("{0:03d}".format(midCC94[midCH])),font=fontm,fill=(255,255,55))
             midiout.send_message([0xb0+midCH,94,midCC94[midCH]])
             mode0_write= True
             
          if mode0_coordi ==9:
             if pb1[midCH] > 0x00:
                pb1[midCH] -= 0x01
             elif pb1[midCH] == 0x00 and pb2[midCH] > 0x00:
                pb2[midCH] -= 0x01
                pb1[midCH] = 0x7f
             elif pb1[midCH] == 0x00 and pb2[midCH] == 0x00:
                pb1[midCH] = 0x7f
                pb2[midCH] = 0x7f
             draw.rectangle((tmx*18,tly+tmy*2+1,160,tly+tmy*3),(0,0,0))
             draw.text((tmx*18,tly+tmy*2+1),str("{0:04d}".format(0x80*pb2[midCH]+pb1[midCH]-8192)),font=fontm,fill=(255,255,55))
             mode0_write= True
             
             midiout.send_message([0xe0+midCH,pb1[midCH],pb2[midCH]])

       if mode==1:
          if mode1_coordi ==0:
             sf2counter -= 1
             if sf2counter == -1:
                sf2counter =  len(sf2) -1
             draw.rectangle((tmx*5,tly+tmy+1,160,tly+tmy*2+2),(0,0,0))
             draw.rectangle((9,tly+tmy*2+1,160,tly+tmy*3+2),(0,0,0))
             draw.text((9+tmx*4,tly+tmy+1),"{0:03d}/{1:03d}" .format(sf2counter + 1 ,len(sf2)),font=fontm,fill=(55,255,255))
             draw.text((9,tly+tmy*2+1),sf2[sf2counter],font=fontm,fill=(255,255,55))
             if sf2used[sf2counter]==1:
                 draw.text((9,tly+tmy+1),"            ♪",font=fontm,fill=(55,255,255))
             disp.display(img)
          if mode1_coordi ==1:
             midicounter -= 1
             if midicounter == -1:
                midicounter =  len(midi)-1
             draw.rectangle((tmx*5,tly+tmy*3+3,160,tly+tmy*4+2),(0,0,0))
             draw.rectangle((9,tly+tmy*4+1,160,tly+tmy*5+2),(0,0,0))
             draw.text((9+tmx*4,tly+tmy*3+1),"{0:03d}/{1:03d}".format(midicounter + 1 ,len(midi) ),font=fontm,fill=(55,255,255))
             draw.text((9,tly+tmy*4+1),midi[midicounter],font=fontm,fill=(255,255,55))
             if playflag[midicounter]==1:
                draw.text((9,tly+tmy*3+1),"            ▶",font=fontm,fill=(55,255,255))
             disp.display(img)
       if mode==3:
          wificounter -=1
          if wificounter == -1:
             wificounter =  len(wifi) -1
          draw.rectangle((9+tmx*5,tly+tmy+1,9+tmx*8,tly+tmy*2+2),(0,0,0))
          draw.rectangle((9,tly+tmy*2+1,160,tly+tmy*3+2),(0,0,0))
          draw.text((9,tly+tmy+1),"     {0:03d}" .format(wificounter+1),font=fontm,fill=(55,255,255))
          draw.text((9,tly+tmy*2+1),wifi[wificounter],font=fontm,fill=(255,255,55))
          disp.display(img)
       longpush_(input_LEFT)

    if GPIO.input(input_RIGHT) == 0 and GPIO.input(input_MODE) != 0: 
       time.sleep(0.0001)
       if mode==0:
          if mode0_coordi ==0:
             midCH +=1
             if midCH>15:
                midCH=0 
             draw.rectangle((tlx*4,0,tlx*6,tly),(0,0,0))
             draw.text((tlx*4,0),str("{0:02}".format(midCH + 1)),font=fontl,fill=(255,255,55))
             draw.rectangle((tmx*5,tly+tmy+1,65,128),(0,0,0))
             draw.text((tmx*5,tly+tmy+1),str("{0:03d}".format(midPRG[midCH] + 1)),font=fontm,fill=(255,255,55))
             draw.text((tmx*5,tly+tmy*2+1),str("{0:03d}".format(midCC7[midCH])),font=fontm,fill=(255,255,55))
             draw.text((tmx*5,tly+tmy*3+1),str("{0:03d}".format(midCC11[midCH])),font=fontm,fill=(255,255,55))
             draw.text((tmx*5,tly+tmy*4+1),str("{0:03d}".format(midCC10[midCH]-64)),font=fontm,fill=(255,255,55))
             draw.text((tmx*5,tly+tmy*5+1),str("{0:03d}".format(midCC1[midCH])),font=fontm,fill=(255,255,55))
             draw.text((tmx*5,tly+tmy*6+1),str("{0:03d}".format(midCC91[midCH])),font=fontm,fill=(255,255,55))
             draw.text((tmx*5,tly+tmy*7+1),str("{0:03d}".format(midCC93[midCH])),font=fontm,fill=(255,255,55))
             draw.rectangle((tmx*18,tly+tmy+1,160,128),(0,0,0))
             draw.text((tmx*18,tly+tmy+1),str("{0:03d}".format(midCC94[midCH])),font=fontm,fill=(255,255,55))
             draw.text((tmx*18,tly+tmy*2+1),str("{0:04d}".format(0x80*pb2[midCH]+pb1[midCH]-8192)),font=fontm,fill=(255,255,55))
             mode0_write= True
          if mode0_coordi ==1:
             midPRG[midCH] +=1
             if midPRG[midCH] >127:
                midPRG[midCH] =0
             draw.rectangle((tmx*5,tly+tmy+1,65,tly+tmy*2),(0,0,0))
             draw.text((tmx*5,tly+tmy+1),str("{0:03d}".format(midPRG[midCH] + 1)),font=fontm,fill=(255,255,55))
             mode0_write= True
             midiout.send_message([0xc0+midCH,midPRG[midCH]])
          if mode0_coordi ==2:
             midCC7[midCH] +=1
             if midCC7[midCH] >127:
                midCC7[midCH] =0
             draw.rectangle((tmx*5,tly+tmy*2+1,65,tly+tmy*3),(0,0,0))
             draw.text((tmx*5,tly+tmy*2+1),str("{0:03d}".format(midCC7[midCH])),font=fontm,fill=(255,255,55))
             mode0_write= True
              
             midiout.send_message([0xb0+midCH,7,midCC7[midCH]])
          if mode0_coordi ==3:
             midCC11[midCH] +=1
             if midCC11[midCH] >127:
                midCC11[midCH] =0
             draw.rectangle((tmx*5,tly+tmy*3+1,65,tly+tmy*4),(0,0,0))
             draw.text((tmx*5,tly+tmy*3+1),str("{0:03d}".format(midCC11[midCH])),font=fontm,fill=(255,255,55))
             mode0_write= True
             midiout.send_message([0xb0+midCH,11,midCC11[midCH]])
          if mode0_coordi ==4:
             midCC10[midCH] +=1
             if midCC10[midCH] >127:
                midCC10[midCH] =0
             draw.rectangle((tmx*5,tly+tmy*4+1,65,tly+tmy*5),(0,0,0))
             draw.text((tmx*5,tly+tmy*4+1),str("{0:03d}".format(midCC10[midCH]-64)),font=fontm,fill=(255,255,55))
             mode0_write= True
             midiout.send_message([0xb0+midCH,10,midCC10[midCH]])
          if mode0_coordi ==5:
             midCC1[midCH] +=1
             if midCC1[midCH] >127:
                midCC1[midCH] =0
             draw.rectangle((tmx*5,tly+tmy*5+1,65,tly+tmy*6),(0,0,0))
             draw.text((tmx*5,tly+tmy*5+1),str("{0:03d}".format(midCC1[midCH])),font=fontm,fill=(255,255,55))
             mode0_write= True
             
             midiout.send_message([0xb0+midCH,1,midCC1[midCH]])
          if mode0_coordi ==6:
             midCC91[midCH] +=1
             if midCC91[midCH] >127:
                midCC91[midCH] =0
             draw.rectangle((tmx*5,tly+tmy*6+1,65,tly+tmy*7),(0,0,0))
             draw.text((tmx*5,tly+tmy*6+1),str("{0:03d}".format(midCC91[midCH])),font=fontm,fill=(255,255,55))
             mode0_write= True
             midiout.send_message([0xb0+midCH,91,midCC91[midCH]])
          if mode0_coordi ==7:
             midCC93[midCH] +=1
             if midCC93[midCH] >127:
                midCC93[midCH] =0
             draw.rectangle((tmx*5,tly+tmy*7+1,65,128),(0,0,0))
             draw.text((tmx*5,tly+tmy*7+1),str("{0:03d}".format(midCC93[midCH])),font=fontm,fill=(255,255,55))
             midiout.send_message([0xb0+midCH,93,midCC93[midCH]])
             mode0_write= True
          if mode0_coordi ==8:
             midCC94[midCH] +=1
             if midCC94[midCH] >127:
                midCC94[midCH] =0
             draw.rectangle((tmx*18,tly+tmy+1,160,tly+tmy*2),(0,0,0))
             draw.text((tmx*18,tly+tmy+1),str("{0:03d}".format(midCC94[midCH])),font=fontm,fill=(255,255,55))
             midiout.send_message([0xb0+midCH,94,midCC94[midCH]])
             mode0_write= True
          if mode0_coordi ==9:
             if pb1[midCH] < 0x7f:
                pb1[midCH] += 0x01
             elif pb1[midCH] == 0x7f and pb2[midCH] < 0x7f:
                pb2[midCH] += 0x01
                pb1[midCH] = 0x00
             elif pb1[midCH] == 0x7f and pb2[midCH] == 0x7f:
                pb1[midCH] = 0x00
                pb2[midCH] = 0x00
             draw.rectangle((tmx*18,tly+tmy*2+1,160,tly+tmy*3),(0,0,0))
             draw.text((tmx*18,tly+tmy*2+1),str("{0:04d}".format(0x80*pb2[midCH]+pb1[midCH]-8192)),font=fontm,fill=(255,255,55))
             mode0_write= True
             midiout.send_message([0xe0+midCH,pb1[midCH],pb2[midCH]])

       if mode==1:
          if mode1_coordi ==0:
             sf2counter += 1
             if sf2counter == len(sf2):
                sf2counter = 0
             draw.rectangle((tmx*5,tly+tmy+1,160,tly+tmy*2+2),(0,0,0))
             draw.rectangle((9,tly+tmy*2+1,160,tly+tmy*3+2),(0,0,0))
             draw.text((9+tmx*4,tly+tmy+1),"{0:03d}/{1:03d}" .format(sf2counter + 1 ,len(sf2)),font=fontm,fill=(55,255,255))
             draw.text((9,tly+tmy*2+1),sf2[sf2counter],font=fontm,fill=(255,255,55))
             if sf2used[sf2counter]==1:
                draw.text((9,tly+tmy+1),"            ♪",font=fontm,fill=(55,255,255))
             disp.display(img)
          if mode1_coordi ==1:
             midicounter += 1
             if midicounter == len(midi):
                midicounter = 0
             draw.rectangle((tmx*5,tly+tmy*3+3,160,tly+tmy*4+2),(0,0,0))
             draw.rectangle((9,tly+tmy*4+1,160,tly+tmy*5+2),(0,0,0))
             draw.text((9+tmx*4,tly+tmy*3+1),"{0:03d}/{1:03d}".format(midicounter + 1 ,len(midi) ),font=fontm,fill=(55,255,255))
             draw.text((9,tly+tmy*4+1),midi[midicounter],font=fontm,fill=(255,255,55))  
             if playflag[midicounter]==1:
                draw.text((9,tly+tmy*3+1),"            ▶",font=fontm,fill=(55,255,255))
             disp.display(img) 
       if mode==3:
          wificounter +=1
          if wificounter==len(wifi):
             wificounter=0
          draw.rectangle((9+tmx*5,tly+tmy+1,9+tmx*8,tly+tmy*2+2),(0,0,0))
          draw.rectangle((9,tly+tmy*2+1,160,tly+tmy*3+2),(0,0,0))
          draw.text((9,tly+tmy+1),"     {0:03d}" .format(wificounter+1),font=fontm,fill=(55,255,255))
          draw.text((9,tly+tmy*2+1),wifi[wificounter],font=fontm,fill=(255,255,55))
          disp.display(img)
       longpush_(input_RIGHT)

    if GPIO.input(input_UP) == 0 and GPIO.input(input_MODE) != 0: 
       time.sleep(0.01)
       if mode==0 and GPIO.input(input_OK) != 0:
          draw.rectangle((mode0_coordi_xl[mode0_coordi],mode0_coordi_yl[mode0_coordi],mode0_coordi_xl[mode0_coordi]+csx,mode0_coordi_yl[mode0_coordi]+csy),(0,0,0))
          mode0_coordi -=1
          if mode0_coordi <0:
             mode0_coordi=9
          draw.text((mode0_coordi_xl[mode0_coordi],mode0_coordi_yl[mode0_coordi]),cur_size,font=fontss,fill=(255,255,255))   
          mode0_write= True
       if mode==1 and GPIO.input(input_OK) != 0:
          draw.rectangle((mode1_coordi_xl[mode1_coordi],mode1_coordi_yl[mode1_coordi],mode1_coordi_xl[mode1_coordi]+csx,mode1_coordi_yl[mode1_coordi]+csy),(0,0,0))
          mode1_coordi -=1
          if mode1_coordi <0:
             mode1_coordi=1
          draw.text((mode1_coordi_xl[mode1_coordi],mode1_coordi_yl[mode1_coordi]),cur_size,font=fontss,fill=(255,255,255)) 
          disp.display(img)  
       if mode==2 and GPIO.input(input_OK) != 0:
          draw.rectangle((mode2_coordi_xl[mode2_coordi],mode2_coordi_yl[mode2_coordi],mode2_coordi_xl[mode2_coordi]+csx,mode2_coordi_yl[mode2_coordi]+csy),(0,0,0))
          mode2_coordi -=1
          if mode2_coordi <0:
             mode2_coordi=6
          draw.text((mode2_coordi_xl[mode2_coordi],mode2_coordi_yl[mode2_coordi]),cur_size,font=fontss,fill=(255,255,255))  
          disp.display(img) 
       longpush_(input_UP)
    if GPIO.input(input_DOWN) == 0 and GPIO.input(input_MODE) != 0: 
       time.sleep(0.01)
       if mode==0 and GPIO.input(input_OK) != 0:
          draw.rectangle((mode0_coordi_xl[mode0_coordi],mode0_coordi_yl[mode0_coordi],mode0_coordi_xl[mode0_coordi]+csx,mode0_coordi_yl[mode0_coordi]+csy),(0,0,0))
          mode0_coordi +=1
          if mode0_coordi >9:
             mode0_coordi=0
          draw.text((mode0_coordi_xl[mode0_coordi],mode0_coordi_yl[mode0_coordi]),cur_size,font=fontss,fill=(255,255,255)) 
          mode0_write= True
       if mode==1 and GPIO.input(input_OK) != 0:
          draw.rectangle((mode1_coordi_xl[mode1_coordi],mode1_coordi_yl[mode1_coordi],mode1_coordi_xl[mode1_coordi]+csx,mode1_coordi_yl[mode1_coordi]+csy),(0,0,0))
          mode1_coordi +=1
          if mode1_coordi >1:
             mode1_coordi=0
          draw.text((mode1_coordi_xl[mode1_coordi],mode1_coordi_yl[mode1_coordi]),cur_size,font=fontss,fill=(255,255,255)) 
          disp.display(img)  
       if mode==2 and GPIO.input(input_OK) != 0:
          draw.rectangle((mode2_coordi_xl[mode2_coordi],mode2_coordi_yl[mode2_coordi],mode2_coordi_xl[mode2_coordi]+csx,mode2_coordi_yl[mode2_coordi]+csy),(0,0,0))
          mode2_coordi +=1
          if mode2_coordi >6:
             mode2_coordi=0
          draw.text((mode2_coordi_xl[mode2_coordi],mode2_coordi_yl[mode2_coordi]),cur_size,font=fontss,fill=(255,255,255))  
          disp.display(img) 
       longpush_(input_DOWN)

    if GPIO.input(input_MODE) == 0:  
       time.sleep(0.0001)
       if GPIO.input(input_RIGHT) == 0 and GPIO.input(input_LEFT) == 1 and GPIO.input(input_UP) == 1 and GPIO.input(input_DOWN) == 1:
          dialog_open=0
          time.sleep(0.01)
          mode +=1
          if mode >2:
             mode=0
          if mode==0:
             mode0_default_disp()
          if mode==1:
             mode1_default_disp()
             if sf2used[sf2counter]==1:
                draw.text((9,tly+tmy+1),"            ♪",font=fontm,fill=(55,255,255))
                disp.display(img)
             if playflag[midicounter]==1:
                draw.text((9,tly+tmy*3+1),"            ▶",font=fontm,fill=(55,255,255))
                disp.display(img)
          if mode==2:      
             mode2_default_disp()
       longpush_(input_RIGHT)
       if GPIO.input(input_LEFT) == 0 and GPIO.input(input_RIGHT) == 1 and GPIO.input(input_UP) == 1 and GPIO.input(input_DOWN) == 1:
          dialog_open=0
          time.sleep(0.01)
          mode -=1
          if mode <0:
             mode=2
          if mode==0:
             mode0_default_disp()
          if mode==1:
             mode1_default_disp()
             if sf2used[sf2counter]==1:
                draw.text((9,tly+tmy+1),"            ♪",font=fontm,fill=(55,255,255))
                disp.display(img)
             if playflag[midicounter]==1:
                draw.text((9,tly+tmy*3+1),"            ▶",font=fontm,fill=(55,255,255))
                disp.display(img)
          if mode==2:
             mode2_default_disp()
       longpush_(input_LEFT)

       if GPIO.input(input_UP) == 0 and GPIO.input(input_DOWN) == 1 and GPIO.input(input_LEFT) == 1 and GPIO.input(input_RIGHT) == 1:
          dialog_open=0
          time.sleep(0.01)
          volume +=1
          if volume>100:
             volume=0
          subprocess.call('amixer cset numid=1 {}% > /dev/null'.format(volume) ,shell=True)
          draw.rectangle((tlx*8+tsx*8,0,tlx*9+tsx*10,tsy),(0,0,0))
          draw.text((tlx*8+tsx*8,0),str(volume),font=fontss,fill=(0,255,0))
          if mode !=0:
             disp.display(img)
          if mode ==0:
             mode0_write= True
          longpush_(input_UP)
       if GPIO.input(input_DOWN) == 0 and GPIO.input(input_UP) == 1 and GPIO.input(input_LEFT) == 1 and GPIO.input(input_RIGHT) == 1:
          dialog_open=0
          time.sleep(0.01)
          volume -=1
          if volume<0:
             volume=100
          subprocess.call('amixer cset numid=1 {}% > /dev/null'.format(volume) ,shell=True)
          draw.rectangle((tlx*8+tsx*8,0,tlx*9+tsx*10,tsy),(0,0,0))
          draw.text((tlx*8+tsx*8,0),str(volume),font=fontss,fill=(0,255,0))
          if mode !=0:
             disp.display(img)
          if mode ==0:
             mode0_write= True
          longpush_(input_DOWN)  
       if GPIO.input(input_LEFT) == 0 and GPIO.input(input_RIGHT) == 0 and GPIO.input(input_UP) == 0 and GPIO.input(input_DOWN) == 0 and GPIO.input(input_OK) == 0:
          allnoteoff()
          ST7735.ST7735(port=0,cs=0,dc=12,rst=25,rotation=90,width=128,height=160,spi_speed_hz=31200000+15600000)
          while GPIO.input(input_LEFT) == 0 and GPIO.input(input_RIGHT) == 0 and GPIO.input(input_UP) == 0 and GPIO.input(input_DOWN) == 0 and GPIO.input(input_OK) == 0:
               continue 
    if GPIO.input(input_OK) == 0 and GPIO.input(input_MODE) != 0: 
       time.sleep(0.01)        
       if mode==0:
          allnoteoff()
          while (GPIO.input(input_OK)) == 0: 
               continue 
       if mode==1 and mode1_coordi ==0 and sf2used[sf2counter]==0 and sf2[0] != "sf2_None":  
          time.sleep(0.05)
          sf2used = [0]*len(sf2)
          sf2used[sf2counter]=1
          draw.rectangle((tmx*13,tly+tmy+1,160,tly+tmy*2+2),(0,0,0))
          waitflag=3
          subprocess.call('sudo killall timidity',shell=True)
          subprocess.call('sudo killall aplaymidi',shell=True)
          playflag = [0]*len(midi)
          subprocess.Popen('sudo timidity -c "/media/usb0/timidity_cfg/{}.cfg"' .format(sf2[sf2counter]),shell=True)
          time.sleep(3)
          subprocess.call('sh /home/pi/ysynth4/midiconnect.sh',shell=True)

          draw.rectangle((9,tly+tmy*2+1,160,tly+tmy*3+2),(0,0,0))
          draw.text((9,tly+tmy*2+1),"準備完了!",font=fontm,fill=(255,255,55))
          waitflag=0
          disp.display(img)
          midPRG=  [0]*16
          midCC7=  [100]*16
          midCC11=  [127]*16
          midCC10=  [64]*16
          midCC1=  [0]*16
          midCC91=  [40]*16
          midCC93=  [0]*16
          midCC94=  [0]*16
          pb1 = [0]*16
          pb2 = [0x40]*16
          time.sleep(2)
          mode1_default_disp()
          
       if GPIO.input(input_OK) == 0 and  mode==1 and mode1_coordi ==1 : 
          if playflag[midicounter]==0 and midi[0] != "midi_None":
             time.sleep(0.05)
             playflag = [0]*len(midi)
             playflag[midicounter]=1
             draw.rectangle((tmx*13,tly+tmy*3+1,160,tly+tmy*4+2),(0,0,0))
             draw.text((9,tly+tmy*3+1),"            ▶",font=fontm,fill=(55,255,255))
             subprocess.call('sudo killall aplaymidi',shell=True)
             allnoteoff()
             aplaymidi = subprocess.Popen('aplaymidi -p 14:0 "/media/usb0/midi/{}.mid"' .format(midi[midicounter]),shell=True)
             disp.display(img)
             mode1_default_disp()
             while (GPIO.input(input_OK)) == 0: 
               continue 

          if GPIO.input(input_OK) == 0 and playflag[midicounter]==1:
             time.sleep(0.05)
             playflag = [0]*len(midi)
             draw.rectangle((tmx*13,tly+tmy*3+1,160,tly+tmy*4+2),(0,0,0))
             allnoteoff()
             subprocess.call('sudo killall aplaymidi',shell=True)
             allnoteoff()
             disp.display(img)
             mode1_default_disp()
             while (GPIO.input(input_OK)) == 0: 
               continue 

       if mode==2 and mode2_coordi ==0:
          time.sleep(0.05)
          while (GPIO.input(input_OK)) == 0: 
               continue 
          mode=3

       if mode==2 and mode2_coordi ==1:
          time.sleep(0.05)
          dialog_window0()
          if audio_card == str("IQaudIODAC") or audio_card == str("") :
             draw.text((11,tly+tmy*2+1)," bcm2835に切り替えます",font=fontss,fill=(0,0,0))
             draw.text((11,tly+tmy*3+1),"か?(再起動します)",font=fontss,fill=(0,0,0))
             draw.text((dlog_zahyo_xl[dlog_zahyo],dlog_zahyo_yl[dlog_zahyo]),cur_size,font=fontss,fill=(0,0,0))
             disp.display(img)
             dialog_loop0("    再起動します...","")
             if dlog_zahyo==0:
                subprocess.call("sudo sed -i -e '$ a dtparam=audio=on' /boot/config.txt" ,shell=True)
                subprocess.call("sudo sed -i -e '/dtoverlay=iqaudio-dacplus/d' /boot/config.txt" ,shell=True)
                subprocess.call("sudo sed -i -e '$ a opt B3,8' /usr/local/share/timidity/timidity.cfg" ,shell=True)
                subprocess.call("sudo sed -i -e '/opt B2,8/d' /usr/local/share/timidity/timidity.cfg" ,shell=True)
                subprocess.call("sudo reboot" ,shell=True)
                
          if audio_card == str("bcm2835"):          
             draw.text((11,tly+tmy*2+1)," IQaudIODACに切り替えま",font=fontss,fill=(0,0,0))
             draw.text((11,tly+tmy*3+1),"すか?(再起動します)",font=fontss,fill=(0,0,0))
             draw.text((dlog_zahyo_xl[dlog_zahyo],dlog_zahyo_yl[dlog_zahyo]),cur_size,font=fontss,fill=(0,0,0))
             disp.display(img)
             dialog_loop0("    再起動します...","")
             if dlog_zahyo==0:
                subprocess.call("sudo sed -i -e '$ a dtoverlay=iqaudio-dacplus' /boot/config.txt" ,shell=True)
                subprocess.call("sudo sed -i -e '/dtparam=audio=on/d' /boot/config.txt" ,shell=True)
                subprocess.call("sudo sed -i -e '$ a opt B2,8' /usr/local/share/timidity/timidity.cfg" ,shell=True)
                subprocess.call("sudo sed -i -e '/opt B3,8/d' /usr/local/share/timidity/timidity.cfg" ,shell=True)
                subprocess.call("sudo reboot" ,shell=True)

       if mode==2 and mode2_coordi ==2:
          time.sleep(0.05)
          dialog_window0()
          if mountcheck != str("/media/usb0"):
             draw.text((11,tly+tmy*2+1),"    認識させますか?",font=fontss,fill=(0,0,0))
             draw.text((dlog_zahyo_xl[dlog_zahyo],dlog_zahyo_yl[dlog_zahyo]),cur_size,font=fontss,fill=(0,0,0))
             disp.display(img)
             dialog_loop0("      認識します...","sudo mount -t vfat -o ,iocharset=utf8 /dev/sda1 /media/usb0")
             if dlog_zahyo==0:
                subprocess.call('rename.ul .MID .mid /media/usb0/midi/*' ,shell=True)
                subprocess.call('rename.ul .SF2 .sf2 /media/usb0/sf2/*' ,shell=True)
                subprocess.call('rename.ul .CFG .cfg /media/usb0/timidity_cfg/*' ,shell=True)
                midi = subprocess.check_output('find /media/usb0/midi/ -name \*.mid|sort' ,shell=True).decode('utf-8').strip().replace('/media/usb0/midi/','').replace('.mid','').replace('.MID','').split('\n')
                playflag = [0]*len(midi)
                if midi[0]=='':
                   midi= ["midi_None"]
                   midicounter=0
                sf2 = subprocess.check_output('find /media/usb0/sf2/ -name \*.sf2|sort' ,shell=True).decode('utf-8').strip().replace('/media/usb0/sf2/','').replace('.sf2','').replace('.SF2','').split('\n')
                sf2used = [0]*len(sf2)
                if sf2[0]=='':
                   sf2 = ["sf2_None"]
                   sf2counter = 0
                cfg = subprocess.check_output('find /media/usb0/timidity_cfg/ -name \*.cfg|sort' ,shell=True).decode('utf-8').strip().replace('/media/usb0/timidity_cfg/','').replace('.cfg','').split('\n')
                if (sf2 != cfg) and (sf2[0] != "sf2_None"):
                 list_difference = list(set(cfg) - set(sf2))
                 for x in range(len(list_difference)):
                   subprocess.call('sudo rm /media/usb0/timidity_cfg/{}.cfg' .format(list_difference[x])  ,shell=True)
                 list_difference = list(set(sf2) - set(cfg))
                 for x in range(len(list_difference)):
                  subprocess.call('''sudo /home/pi/ysynth4/cfgforsf -C "/media/usb0/sf2/{sf2name}.sf2" | sed -e 's/(null)//' -e 's/^[ ]*//g' -e '/(null)#/d'  -e /^#/d | grep -C 1 % | sed -e '/--/d' -e /^$/d > "/media/usb0/timidity_cfg/{sf2name}.cfg"''' .format(sf2name=list_difference[x])  ,shell=True)
                if sf2[0] == "sf2_None":
                   subprocess.call('sudo rm "/home/pi/timidity_cfg/*.cfg"' ,shell=True)
                time.sleep(2)
                dlog_zahyo=1
                mountcheck=subprocess.check_output("mount|grep -m1 /dev/sda|awk '{print $3}'" ,shell=True).decode('utf-8').strip()
                mode2_default_disp()
                continue

          if mountcheck == str("/media/usb0"):  
             draw.text((11,tly+tmy*2+1),"    取り出しますか?",font=fontss,fill=(0,0,0))
             draw.text((dlog_zahyo_xl[dlog_zahyo],dlog_zahyo_yl[dlog_zahyo]),cur_size,font=fontss,fill=(0,0,0))
             disp.display(img)
             dialog_loop0("    取り出します...","sudo umount /media/usb0/")
             if dlog_zahyo==0:
              subprocess.call('sudo killall timidity',shell=True)
              subprocess.call('sudo killall aplaymidi',shell=True)
              midi= ["midi_None"]
              midicounter=0
              playflag = [0]
              sf2 = ["sf2_None"]
              sf2counter = 0
              sf2used = [0]
              cfg = [ ]
              dlog_zahyo=1
              while mountcheck == str("/media/usb0"):  
                    mountcheck=subprocess.check_output("mount|grep -m1 /dev/sda|awk '{print $3}'" ,shell=True).decode('utf-8').strip()
              mode2_default_disp()

       if mode==2 and mode2_coordi ==3:
          time.sleep(0.05)
          dialog_window0()
          draw.text((11,tly+tmy*2+1)," アップデートしますか?",font=fontss,fill=(0,0,0))
          draw.text((dlog_zahyo_xl[dlog_zahyo],dlog_zahyo_yl[dlog_zahyo]),cur_size,font=fontss,fill=(0,0,0))
          disp.display(img)
          subprocess.call("sudo rm /home/pi/ysynth4/ysynth4.py.*" ,shell=True)
          dialog_loop0("    ダウンロード中...","wget https://raw.githubusercontent.com/YoutechA320U/ysynth4/master/ysynth4.py -P /home/pi/ysynth4/")
          latest_dl =int(subprocess.check_output("test -f /home/pi/ysynth4/ysynth4.py.1;echo $?" ,shell=True).decode('utf-8').strip())
          if latest_dl == 1 and dlog_zahyo==0:
             draw.rectangle((0,0,160,128),(0,0,0)) 
             draw.text((3,60),"    ダウンロード失敗",font=fontss,fill=(0,255,0))
             disp.display(img)
             dlog_zahyo=1
             time.sleep(2)
             mode2_default_disp()
          if latest_dl ==0:
             download_v=float(subprocess.check_output("grep -m1 version= /home/pi/ysynth4/ysynth4.py.1|awk '{print $2;}'" ,shell=True).decode('utf-8').strip().replace('\nysynth4/ysynth4.py.1|grep',''))
             if download_v > version:
                draw.rectangle((0,0,160,128),(0,0,0)) 
                waitflag=4
                subprocess.call('sudo chown -R pi:pi /home/pi/' ,shell=True)
                subprocess.call("sudo mv -f /home/pi/ysynth4/ysynth4.py.1 /home/pi/ysynth4/ysynth4.py" ,shell=True)
                subprocess.call("wget https://raw.githubusercontent.com/YoutechA320U/ysynth4/master/setup.sh -P /home/pi/ysynth4/" ,shell=True)
                subprocess.call("sudo mv -f /home/pi/ysynth4/setup.sh.1 /home/pi/ysynth4/setup.sh" ,shell=True)
                subprocess.call("sudo sh /home/pi/ysynth4/setup.sh" ,shell=True)
                waitflag=0
                draw.rectangle((0,0,160,128),(0,0,0)) 
                draw.text((3,60),"    リロードします...",font=fontss,fill=(0,255,0))
                disp.display(img)
                subprocess.call('sudo systemctl restart ysynth4.service',shell=True)
             if download_v <= version:
                draw.rectangle((0,0,160,128),(0,0,0)) 
                draw.text((3,60),"   最新のバージョンです",font=fontss,fill=(0,255,0))
                subprocess.call("sudo rm /home/pi/ysynth4/ysynth4.py.*" ,shell=True)
                disp.display(img)
                dlog_zahyo=1
                time.sleep(2)
                mode2_default_disp()
       
       if mode==2 and mode2_coordi ==4:
          time.sleep(0.05)
          dialog_window0()
          draw.text((11,tly+tmy*2+1),"     再起動しますか?",font=fontss,fill=(0,0,0))
          draw.text((dlog_zahyo_xl[dlog_zahyo],dlog_zahyo_yl[dlog_zahyo]),cur_size,font=fontss,fill=(0,0,0))
          disp.display(img)
          dialog_loop0("    再起動します...","sudo reboot")

       if mode==2 and mode2_coordi ==5:
          time.sleep(0.05)
          dialog_window0()
          draw.text((11,tly+tmy*2+1),"シャットダウンしますか?",font=fontss,fill=(0,0,0))
          draw.text((dlog_zahyo_xl[dlog_zahyo],dlog_zahyo_yl[dlog_zahyo]),cur_size,font=fontss,fill=(0,0,0))
          disp.display(img)
          dialog_loop0("  シャットダウンします...","sudo shutdown -h now")

       if mode==2 and mode2_coordi ==6:
          time.sleep(0.05)
          dialog_window0()
          draw.text((11,tly+tmy*2+1),"   リロードしますか?",font=fontss,fill=(0,0,0))
          draw.text((dlog_zahyo_xl[dlog_zahyo],dlog_zahyo_yl[dlog_zahyo]),cur_size,font=fontss,fill=(0,0,0))
          disp.display(img)
          dialog_loop0("    リロードします...","sudo systemctl restart ysynth4.service")    
       if mode==3 and dialog_open !=1:
          mode3_default_disp()
          dialog_open=1
       if mode==3 and dialog_open ==1:
          if GPIO.input(input_OK) == 0 and wifi[0] !="見つかりませんでした":
             time.sleep(0.05)
             sc_key()   
              
    if (GPIO.input(input_LEFT) and GPIO.input(input_RIGHT) and GPIO.input(input_UP) and GPIO.input(input_DOWN) and GPIO.input(input_OK))== 1:  
       longpush=0 


def mode0_write_():
   global mode0_write
   while True:
      time.sleep(0.0001)
      if mode0_write is True and mode==0:
         mode0_write= False
         disp.display(img)
         #time.sleep(0.01)
         

thread2 = threading.Thread(target=mididisp)
thread3 = threading.Thread(target=ysynthmain)
thread4 = threading.Thread(target=mode0_write_)

thread2.start()
thread3.start()
thread4.start()

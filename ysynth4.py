# -*- coding: utf-8 -*-
#!/usr/bin/env python
import RPi.GPIO as GPIO
import time
import subprocess
import rtmidi
import sys

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import ST7735

width = 128
height = 160

disp = ST7735.ST7735(
    port=0,
    cs=0,  # BG_SPI_CSB_BACK or BG_SPI_CS_FRONT
    dc=12, 
    rst=25,            
    rotation=90,
    width=128,
    height=160,
    spi_speed_hz=40000000 #66659200
)

# Initialize display.
disp.begin()

width = disp.width
height = disp.height

img = Image.new('RGB', (width, height), color=(0, 0, 0))

draw = ImageDraw.Draw(img)
draw.rectangle((0, 0, 160, 160), (0,0,0))

#*#*#*#*#*#*#
version= 1.5
day="2019/09/06"
#*#*#*#*#*#*#*
volume = 70
mode = 0

midiCH = 0
midiPROG=  [0]*16
midiCC7=  [100]*16
midiCC11=  [127]*16
midiCC10=  [64]*16
midiCC1=  [0]*16
midiCC91=  [40]*16
midiCC93=  [0]*16
midiCC94=  [0]*16
pb1 = [0]*16
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

GPIO.setmode(GPIO.BCM)
GPIO.setup(input_OK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(input_MODE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(input_RIGHT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(input_LEFT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(input_UP, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(input_DOWN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
fontss = ImageFont.truetype('/usr/share/fontss/truetype/takao-gothic/TakaoGothic.ttf', 12, encoding='unic')
fonts = ImageFont.truetype('/usr/share/fontss/truetype/takao-gothic/TakaoGothic.ttf', 13, encoding='unic')
fontm = ImageFont.truetype('/usr/share/fontss/truetype/takao-gothic/TakaoGothic.ttf', 14, encoding='unic')
fontl = ImageFont.truetype('/usr/share/fontss/truetype/takao-gothic/TakaoGothic.ttf', 20, encoding='unic')
fontll = ImageFont.truetype('/usr/share/fontss/truetype/takao-gothic/TakaoGothic.ttf', 24, encoding='unic')

subprocess.call('sudo mount -t vfat -o ,iocharset=utf8 /dev/sda1 /media/usb0' ,shell=True)
mountcheck=subprocess.check_output("mount|grep -m1 /dev/sda|awk '{print $3}'" ,shell=True).decode('utf-8').strip()

def boot_disp():
   global mountcheck
   for x in range(69):
    draw.rectangle((0, 0, 160, 128), (0,0,0))
    if mountcheck == str("/media/usb0"):
       draw.text((35, 1+x-32),"Ysynth4",  font=fontll, fill=(55, 255, 255))
       #draw.text((35, 1+x-32),"         ®",  font=fontl, fill=(55, 255, 255))
    if mountcheck != str("/media/usb0"):
       draw.rectangle((40, 1+x-32, 120, 1+x-10),outline=(100,100,100), fill=(55, 255, 255))
       #draw.text((35, 1+x-32),"         ®",  font=fontl, fill=(55, 255, 255))
    draw.text((35, 100),"v{0}/{1}" .format(version,day), font=fontss, fill=(55, 255, 255))
    draw.text((40, 110),"@YoutechA320U",  font=fontss, fill=(55, 255, 255))
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
midi = subprocess.check_output('find /media/usb0/midi/ -name \*.mid|sort' ,shell=True).decode('utf-8').strip().replace('/media/usb0/midi/', '').replace('.mid', '').split('\n')
playflag = [0]*len(midi)
if midi[0]=='':
   midi= ["midi_None"]
   midicounter=0
sf2 = subprocess.check_output('find /media/usb0/sf2/ -name \*.sf2|sort' ,shell=True).decode('utf-8').strip().replace('/media/usb0/sf2/', '').replace('.sf2', '').split('\n')
sf2used = [0]*len(sf2)
if sf2[0]=='':
   sf2 = ["sf2_None"]
   sf2counter = 0
cfg = subprocess.check_output('find /media/usb0/timidity_cfg/ -name \*.cfg|sort' ,shell=True).decode('utf-8').strip().replace('/media/usb0/timidity_cfg/', '').replace('.cfg', '').split('\n')
if (sf2 != cfg) and (sf2[0] != "sf2_None"):
 list_difference = list(set(cfg) - set(sf2))
 for x in range(len(list_difference)):
  subprocess.call('sudo rm "/media/usb0/timidity_cfg/{}.cfg"' .format(list_difference[x])  ,shell=True)
 list_difference = list(set(sf2) - set(cfg))
 for x in range(len(list_difference)):
  subprocess.call('''sudo /home/pi/ysynth4/cfgforsf -C "/media/usb0/sf2/{sf2name}.sf2" | sed -e 's/(null)//' -e 's/^[ ]*//g' -e '/(null)#/d'  -e /^#/d | grep -C 1 % | sed -e '/--/d' -e /^$/d > "/media/usb0/timidity_cfg/{sf2name}.cfg"''' .format(sf2name=list_difference[x])  ,shell=True)
if sf2[0] == "sf2_None":
   subprocess.call('sudo rm /home/pi/timidity_cfg/*.cfg' ,shell=True)

draw.rectangle((0, 0, 160, 128), (0,0,0))
time.sleep(2)
disp.display(img)

subprocess.call('sudo killall ttymidi', shell=True)
subprocess.call('sudo killall timidity', shell=True)
subprocess.Popen('sudo /home/pi/ysynth4/ttymidi -s /dev/ttyAMA0 -b 38400', shell=True)
time.sleep(1)
midiout = rtmidi.MidiOut()
midiout.open_virtual_port("Ysynth4_out") # 仮想MIDI出力ポートの名前
midiin = rtmidi.MidiIn()
midiin.open_virtual_port("Ysynth4_in") # 仮想MIDI入力ポートの名前
midiin.ignore_types(sysex=False)
def allnoteoff():
    a = 0xb0
    while (a < 0xbf ):
        midiout.send_message([a, 0x78, 0x00])
        a += 1
subprocess.call('amixer cset numid=1 {}% > /dev/null'.format(volume) , shell=True)
wifi_ssid=str(subprocess.check_output('''iwconfig wlan0 | grep ESSID | sed -e 's/wlan0//g' -e 's/IEEE 802.11//g' -e 's/ESSID://g' -e 's/"//g' -e 's/^[ ]*//g' ''' ,shell=True).decode('utf-8').strip())
if wifi_ssid=="off/any":
   wifi_ssid="接続していません" 
#wifi_ssid="**********"
audio_card = str(subprocess.check_output("aplay -l |grep -m1 'card 0'|awk '{print $4;}' " ,shell=True).decode('utf-8').strip().replace(']', '').replace('[', '').replace(',', ''))
mountcheck=subprocess.check_output("mount|grep -m1 /dev/sda|awk '{print $3}'" ,shell=True).decode('utf-8').strip()
subprocess.call('sh /home/pi/ysynth4/midiconnect.sh', shell=True)

x = 3
y = 0
m_size="A" #1文字分
cur_size="▶"

t_size_s_x, t_size_s_y  = draw.textsize(m_size, fontss)
t_size_m_x, t_size_m_y  = draw.textsize(m_size, fontm)
t_size_l_x, t_size_l_y  = draw.textsize(m_size, fontl)
cur_size_x, cur_size_y  = draw.textsize(m_size, fontss)

mode0_coordi=0
mode0_coordi_xl=[3,3,3,3,3,3,3,3,t_size_m_x*10,t_size_m_x*10]
mode0_coordi_yl=[t_size_l_y/4,t_size_l_y+t_size_m_y+1,\
   t_size_l_y+t_size_m_y*2+1,t_size_l_y+t_size_m_y*3+1,\
      t_size_l_y+t_size_m_y*4+1,t_size_l_y+t_size_m_y*5+1,\
         t_size_l_y+t_size_m_y*6+1,t_size_l_y+t_size_m_y*7+1,\
            t_size_l_y+t_size_m_y+1,t_size_l_y+t_size_m_y*2+1]

mode1_coordi=0
mode1_coordi_xl=[3,3]
mode1_coordi_yl=[t_size_l_y+t_size_m_y+8, t_size_l_y+t_size_m_y*3+8]

mode2_coordi=0
mode2_coordi_xl=[3,3,3,3,3,3,3]
mode2_coordi_yl=[t_size_l_y+t_size_m_y+1,t_size_l_y+t_size_m_y*2+1,\
   t_size_l_y+t_size_m_y*3+1,t_size_l_y+t_size_m_y*4+1,\
      t_size_l_y+t_size_m_y*5+1,t_size_l_y+t_size_m_y*6+1,t_size_l_y+t_size_m_y*7+1]

dialog_coordi=1
dialog_coordi_xl=[12,82]
dialog_coordi_yl=[90,90]

sckey_coordi=0

msg = None
def mididisp():
##MIDI入力をディスプレイに反映する処理
    global midiPROG,midiCC7,midiCC11,midiCC10,midiCC10,midiCC1,midiCC91,midiCC93,midiCC94,pb1,pb2
    msg = midiin.get_message()
    if msg is None:
       message, deltatime = None,None
       time.sleep(0.00001) 
    if msg is not None:
       message, deltatime = msg
       #time.sleep(0.00001) 
       try:
        if message == ([240, 65, 16, 66, 18, 64, 0, 127, 0, 65, 247]) or message ==( [240, 67, 16, 76, 0, 0, 126, 0, 247]) or message == ([240, 126, 127, 9, 1, 247]) or message == ([240, 126, 127, 9, 3, 247]) :
           midiPROG= [0]*16
           midiCC7=  [100]*16
           midiCC11=  [127]*16
           midiCC10=  [64]*16
           midiCC1=  [0]*16
           midiCC91=  [40]*16
           midiCC93=  [0]*16
           midiCC94=  [0]*16
           pb1 = [0]*16
           pb2 = [0x40]*16
           if mode == 0:
              draw.rectangle((t_size_m_x*5, t_size_l_y+t_size_m_y+1, 65, 128), (0,0,0))
              draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y+1),str("{0:03d}".format(midiPROG[midiCH] + 1)), font=fontm, fill=(255, 255, 55))
              draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*2+1),str("{0:03d}".format(midiCC7[midiCH])),  font=fontm, fill=(255, 255, 55))
              draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*3+1),str("{0:03d}".format(midiCC11[midiCH])),  font=fontm, fill=(255, 255, 55))
              draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*4+1),str("{0:03d}".format(midiCC10[midiCH]-64)),  font=fontm, fill=(255, 255, 55))
              draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*5+1),str("{0:03d}".format(midiCC1[midiCH])),  font=fontm, fill=(255, 255, 55))
              draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*6+1),str("{0:03d}".format(midiCC91[midiCH])), font=fontm, fill=(255, 255, 55))
              draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*7+1),str("{0:03d}".format(midiCC93[midiCH])),  font=fontm, fill=(255, 255, 55))
              draw.rectangle((t_size_m_x*18, t_size_l_y+t_size_m_y+1, 160, 128), (0,0,0))
              draw.text((t_size_m_x*18, t_size_l_y+t_size_m_y+1),str("{0:03d}".format(midiCC94[midiCH])), font=fontm, fill=(255, 255, 55))
              draw.text((t_size_m_x*18, t_size_l_y+t_size_m_y*2+1),str("{0:04d}".format(0x80*pb2[midiCH]+pb1[midiCH]-8192)), font=fontm, fill=(255, 255, 55))
              disp.display(img)
       except :
        pass
       for forlch in range(16):
        if message[0] == 192+forlch :
           if midiPROG[forlch] != message[1]:
              midiPROG[forlch] = message[1]
              if mode == 0 and forlch==midiCH:
                 draw.rectangle((t_size_m_x*5, t_size_l_y+t_size_m_y+1, 65, t_size_l_y+t_size_m_y*2), (0,0,0))
                 draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y+1),str("{0:03d}".format(midiPROG[midiCH] + 1)), font=fontm, fill=(255, 255, 55))
                 disp.display(img)
        if message[0] == 176+forlch and message[1] ==7:
           if midiCC7[forlch] != message[2]:
              midiCC7[forlch] = message[2]
              if mode == 0 and forlch==midiCH:
                 draw.rectangle((t_size_m_x*5, t_size_l_y+t_size_m_y*2+1, 65, t_size_l_y+t_size_m_y*3), (0,0,0))
                 draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*2+1),str("{0:03d}".format(midiCC7[midiCH])),  font=fontm, fill=(255, 255, 55))
                 disp.display(img)
        if message[0] == 176+forlch and message[1] ==11:
           if midiCC11[forlch] != message[2]:
              midiCC11[forlch] = message[2]
              if mode == 0 and forlch==midiCH:
                 draw.rectangle((t_size_m_x*5, t_size_l_y+t_size_m_y*3+1, 65, t_size_l_y+t_size_m_y*4), (0,0,0))
                 draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*3+1),str("{0:03d}".format(midiCC11[midiCH])),  font=fontm, fill=(255, 255, 55))
                 disp.display(img)
        if message[0] == 176+forlch and message[1] ==10:
           if midiCC10[forlch] != message[2]:
              midiCC10[forlch] = message[2] 
              if mode == 0 and forlch==midiCH:
                 draw.rectangle((t_size_m_x*5, t_size_l_y+t_size_m_y*4+1, 65, t_size_l_y+t_size_m_y*5), (0,0,0))
                 draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*4+1),str("{0:03d}".format(midiCC10[midiCH]-64)),  font=fontm, fill=(255, 255, 55))
                 disp.display(img)
        if message[0] == 176+forlch and message[1] ==1:
           if midiCC1[forlch] != message[2]:
              midiCC1[forlch] = message[2]
              if mode == 0 and forlch==midiCH:
                 draw.rectangle((t_size_m_x*5, t_size_l_y+t_size_m_y*5+1, 65, t_size_l_y+t_size_m_y*6), (0,0,0))
                 draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*5+1),str("{0:03d}".format(midiCC1[midiCH])),  font=fontm, fill=(255, 255, 55))
                 disp.display(img)
        if message[0] == 176+forlch and message[1] ==91:
           if midiCC91[forlch] != message[2]:
              midiCC91[forlch] = message[2]
              if mode == 0 and forlch==midiCH:
                 draw.rectangle((t_size_m_x*5, t_size_l_y+t_size_m_y*6+1, 65, t_size_l_y+t_size_m_y*7), (0,0,0))
                 draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*6+1),str("{0:03d}".format(midiCC91[midiCH])), font=fontm, fill=(255, 255, 55))
                 disp.display(img)
        if message[0] == 176+forlch and message[1] ==93:
           if midiCC93[forlch] != message[2]:
              midiCC93[forlch] = message[2]
              if mode == 0 and forlch==midiCH:
                 draw.rectangle((t_size_m_x*5, t_size_l_y+t_size_m_y*7+1, 65, 128), (0,0,0))
                 draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*7+1),str("{0:03d}".format(midiCC93[midiCH])),  font=fontm, fill=(255, 255, 55))
                 disp.display(img)
        if message[0] == 176+forlch and message[1] ==94:
           if midiCC94[forlch] != message[2]:
              midiCC94[forlch] = message[2]
              if mode == 0 and forlch==midiCH:
                 draw.rectangle((t_size_m_x*18, t_size_l_y+t_size_m_y+1, 160,  t_size_l_y+t_size_m_y*2), (0,0,0))
                 draw.text((t_size_m_x*18, t_size_l_y+t_size_m_y+1),str("{0:03d}".format(midiCC94[midiCH])), font=fontm, fill=(255, 255, 55))
                 disp.display(img)
        if message[0] == 0xe0+forlch :
           if pb1[forlch] != message[1] or pb2[forlch] != message[2]:
              pb1[forlch] = message[1]
              pb2[forlch] = message[2]
              if mode == 0 and forlch==midiCH:
                 draw.rectangle((t_size_m_x*18, t_size_l_y+t_size_m_y*2+1, 160, t_size_l_y+t_size_m_y*3), (0,0,0))
                 draw.text((t_size_m_x*18, t_size_l_y+t_size_m_y*2+1),str("{0:04d}".format(0x80*pb2[forlch]+pb1[forlch]-8192)), font=fontm, fill=(255, 255, 55))
                 disp.display(img)
##MIDI入力をディスプレイに反映する処理ここまで

def mode0_default_disp():
   draw.rectangle((0, 0, 160, 128), (0,0,0))
   draw.text((mode0_coordi_xl[mode0_coordi], mode0_coordi_yl[mode0_coordi]),cur_size,  font=fontss, fill=(255, 255, 255))
   draw.text((9, 0),"CH:",  font=fontl, fill=(55, 255, 255))
   draw.text((9, t_size_l_y+t_size_m_y+1),"PC :", font=fontm, fill=(55, 255, 255))
   draw.text((9, t_size_l_y+t_size_m_y*2+1),"VOL:",  font=fontm, fill=(55, 255, 255))
   draw.text((9, t_size_l_y+t_size_m_y*3+1),"EXP:",  font=fontm, fill=(55, 255, 255))
   draw.text((9, t_size_l_y+t_size_m_y*4+1),"PAN:",  font=fontm, fill=(55, 255, 255))
   draw.text((9, t_size_l_y+t_size_m_y*5+1),"MOD:",  font=fontm, fill=(55, 255, 255))
   draw.text((9, t_size_l_y+t_size_m_y*6+1),"REV:", font=fontm, fill=(55, 255, 255))
   draw.text((9, t_size_l_y+t_size_m_y*7+1),"CHO:",  font=fontm, fill=(55, 255, 255))
   draw.text((t_size_l_x*4, 0),str("{0:02}".format(midiCH + 1)),  font=fontl, fill=(255, 255, 55))
   draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y+1),str("{0:03d}".format(midiPROG[midiCH] + 1)), font=fontm, fill=(255, 255, 55))
   draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*2+1),str("{0:03d}".format(midiCC7[midiCH])),  font=fontm, fill=(255, 255, 55))
   draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*3+1),str("{0:03d}".format(midiCC11[midiCH])),  font=fontm, fill=(255, 255, 55))
   draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*4+1),str("{0:03d}".format(midiCC10[midiCH]-64)),  font=fontm, fill=(255, 255, 55))
   draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*5+1),str("{0:03d}".format(midiCC1[midiCH])),  font=fontm, fill=(255, 255, 55))
   draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*6+1),str("{0:03d}".format(midiCC91[midiCH])), font=fontm, fill=(255, 255, 55))
   draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*7+1),str("{0:03d}".format(midiCC93[midiCH])),  font=fontm, fill=(255, 255, 55))
   draw.text((cur_size_x+t_size_m_x*10, t_size_l_y+t_size_m_y+1),"DLY   :", font=fontm, fill=(55, 255, 255))
   draw.text((t_size_m_x*18, t_size_l_y+t_size_m_y+1),str("{0:03d}".format(midiCC94[midiCH])), font=fontm, fill=(255, 255, 55))
   draw.text((cur_size_x+t_size_m_x*10, t_size_l_y+t_size_m_y*2+1),"P.BEND:", font=fontm, fill=(55, 255, 255))
   draw.text((t_size_m_x*18, t_size_l_y+t_size_m_y*2+1),str("{0:04d}".format(0x80*pb2[midiCH]+pb1[midiCH]-8192)), font=fontm, fill=(255, 255, 55))
   draw.text((t_size_l_x*8, 0),"SysVol: "+str(volume),  font=fontss, fill=(0, 255, 0))
   disp.display(img)

def mode1_default_disp():
   draw.rectangle((0, 0, 160, 128), (0,0,0))
   draw.text((mode1_coordi_xl[mode1_coordi], mode1_coordi_yl[mode1_coordi]),cur_size,  font=fontss, fill=(255, 255, 255))
   draw.text((9, 0),"SMF",  font=fontl, fill=(255, 255, 55))
   draw.text((9, t_size_l_y+t_size_m_y+1),"SF2:{0:03d}/{1:03d}" .format(sf2counter + 1 ,len(sf2)), font=fontm, fill=(55, 255, 255))
   draw.text((9, t_size_l_y+t_size_m_y*3+1),"SMF:{0:03d}/{1:03d}".format(midicounter + 1 ,len(midi) ), font=fontm, fill=(55, 255, 255))
   draw.text((9, t_size_l_y+t_size_m_y*2+1),sf2[sf2counter], font=fontm, fill=(255, 255, 55))
   if sf2used[sf2counter]==1:
      draw.text((9, t_size_l_y+t_size_m_y+1),"            ♪", font=fontm, fill=(55, 255, 255))
   if playflag[midicounter]==1:
      draw.text((9, t_size_l_y+t_size_m_y*3+1),"            ▶", font=fontm, fill=(55, 255, 255))
   draw.text((9, t_size_l_y+t_size_m_y*4+1),midi[midicounter],  font=fontm, fill=(255, 255, 55))
   draw.text((t_size_l_x*8, 0),"SysVol: "+str(volume),  font=fontss, fill=(0, 255, 0))
   disp.display(img)

def mode2_default_disp():
   wifi_ssid=str(subprocess.check_output('''iwconfig wlan0 | grep ESSID | sed -e 's/wlan0//g' -e 's/IEEE 802.11//g' -e 's/ESSID://g' -e 's/"//g' -e 's/^[ ]*//g' ''' ,shell=True).decode('utf-8').strip())
   if wifi_ssid=="off/any":
      wifi_ssid="接続していません" 
   draw.rectangle((0, 0, 160, 128), (0,0,0))
   draw.text((mode2_coordi_xl[mode2_coordi], mode2_coordi_yl[mode2_coordi]),cur_size,  font=fontss, fill=(255, 255, 255))
   draw.text((9, 0),"設定",  font=fontl, fill=(255, 255, 55))
   draw.text((9, t_size_l_y+t_size_m_y+1),"WiFi:",  font=fontm, fill=(55, 255, 255))
   draw.text((9, t_size_l_y+t_size_m_y*2+1),"Audio:",  font=fontm, fill=(55, 255, 255))
   draw.text((9, t_size_l_y+t_size_m_y*3+1),"USBメモリ",  font=fontm, fill=(55, 255, 255))
   draw.text((9, t_size_l_y+t_size_m_y*4+1),"Ysynth4アップデート",  font=fontm, fill=(55, 255, 255))
   draw.text((9, t_size_l_y+t_size_m_y*5+1),"再起動", font=fontm, fill=(55, 255, 255))
   draw.text((9, t_size_l_y+t_size_m_y*6+1),"シャットダウン",  font=fontm, fill=(55, 255, 255))
   draw.text((9, t_size_l_y+t_size_m_y*7+1),"リロード",  font=fontm, fill=(55, 255, 255))
   draw.text((t_size_m_x*6, t_size_l_y+t_size_m_y+1),wifi_ssid,  font=fontm, fill=(255, 255, 55))
   draw.text((t_size_m_x*7, t_size_l_y+t_size_m_y*2+1),audio_card,  font=fontm, fill=(255, 255, 55))
   draw.text((t_size_l_x*8, 0),"SysVol: "+str(volume),  font=fontss, fill=(0, 255, 0))
   disp.display(img)
def mode3_default_disp():
   global wifi, wificounter
   wificounter=0
   draw.rectangle((0, 0, 160, 128), (0,0,0))
   draw.text((9, 0),"WiFi",  font=fontl, fill=(255, 255, 55))
   draw.text((t_size_l_x*8, 0),"SysVol: "+str(volume),  font=fontss, fill=(0, 255, 0))
   draw.text((9, t_size_l_y+t_size_m_y+1),"SSID:Scanning...", font=fontm, fill=(55, 255, 255))
   disp.display(img)
   wifi=subprocess.check_output('''iwlist wlan0 scan| grep ESSID | sed -e 's/ESSID://g' -e 's/"//g' -e 's/^[ ]*//g' ''' ,shell=True).decode('utf-8').strip().split('\n')
   if len(wifi)>1:
       [s for s in wifi if s != ""]
   if wifi[0]=="" and len(wifi)==1:
      wifi[0]="見つかりませんでした"
   draw.rectangle((9+t_size_m_x*5, t_size_l_y+t_size_m_y+1, 160, t_size_l_y+t_size_m_y*2+2), (0,0,0))
   draw.text((9, t_size_l_y+t_size_m_y+1),"     {0:03d}/{1:03d}" .format(wificounter + 1,len(wifi)), font=fontm, fill=(55, 255, 255))
   draw.text((mode2_coordi_xl[1], mode2_coordi_yl[1]),cur_size,  font=fontss, fill=(255, 255, 255))
   draw.text((9, t_size_l_y+t_size_m_y*2+1),wifi[wificounter], font=fontm, fill=(255, 255, 55))
   disp.display(img)

def dialog_window0():
   draw.rectangle((10, t_size_l_y+t_size_m_y+1, 150, 110),outline=(255,255,255), fill=(217,207,201))
   draw.rectangle((10, t_size_l_y+t_size_m_y+5, 150, 20),outline=(217,207,201), fill=(8,34,109))
   draw.text((12,22),"確認",  font=fontss, fill=(255, 255, 255))
   draw.rectangle((20, 90, 70, 90+t_size_s_y),outline=(100,100,100), fill=(217,207,201))
   draw.rectangle((90, 90, 140, 90+t_size_s_y),outline=(100,100,100), fill=(217,207,201))
   draw.text((34,90),"はい",  font=fontss, fill=(0, 0, 0))
   draw.text((98,90),"いいえ",  font=fontss, fill=(0, 0, 0))
   disp.display(img)
   
def longpush_(button):
    global longpush
    while (GPIO.input(button) == 0 and longpush !=100): 
          mididisp()
          time.sleep(0.01)
          longpush +=1
          if longpush==100:
             break
          else:
             continue

def dialog_loop0(txt, cmd):
    global dialog_coordi, dialog_coordi_xl, dialog_coordi_yl, longpush
    while (GPIO.input(input_OK)) == 0: 
          mididisp()
          continue 
    while True:
       time.sleep(0.00001)   
       mididisp()
       if GPIO.input(input_RIGHT) == 0 :
          time.sleep(0.01)
          draw.rectangle((dialog_coordi_xl[dialog_coordi], dialog_coordi_yl[dialog_coordi],dialog_coordi_xl[dialog_coordi]+cur_size_x, dialog_coordi_yl[dialog_coordi]+cur_size_y),(217,207,201))
          dialog_coordi +=1
          if dialog_coordi >1:
             dialog_coordi=0
          draw.text((dialog_coordi_xl[dialog_coordi], dialog_coordi_yl[dialog_coordi]),cur_size,  font=fontss, fill=(0, 0, 0))
          disp.display(img)
          longpush_(input_RIGHT)
       if GPIO.input(input_LEFT) == 0 :
          time.sleep(0.01)
          draw.rectangle((dialog_coordi_xl[dialog_coordi], dialog_coordi_yl[dialog_coordi],dialog_coordi_xl[dialog_coordi]+cur_size_x, dialog_coordi_yl[dialog_coordi]+cur_size_y),(217,207,201))
          dialog_coordi -=1
          if dialog_coordi <0:
             dialog_coordi=1
          draw.text((dialog_coordi_xl[dialog_coordi], dialog_coordi_yl[dialog_coordi]),cur_size,  font=fontss, fill=(0, 0, 0))   
          disp.display(img)
          longpush_(input_LEFT)
       if GPIO.input(input_OK) == 0:
          time.sleep(0.05)
          if dialog_coordi==0:
             subprocess.Popen(cmd ,shell=True)
             draw.rectangle((0, 0, 160, 128), (0,0,0)) 
             draw.text((3,60),txt,  font=fontss, fill=(0, 255, 0))
             disp.display(img)
             time.sleep(3)
             draw.rectangle((0, 0, 160, 128), (0,0,0)) 
             time.sleep(1)
             break
          if dialog_coordi==1:
             mode2_default_disp()
             while (GPIO.input(input_OK)) == 0: 
                   mididisp()
                   continue 
             break
       if (GPIO.input(input_LEFT) and GPIO.input(input_RIGHT))== 1 and longpush !=0:  
          longpush=0 
def sc_key():
   global longpush, mode, dialog_open, wifi, wificounter, wifi_psk, wifi_conf
   moji_in=[]
   wifi_psk=[]
   wifi_conf=subprocess.check_output('''cat /etc/wpa_supplicant/wpa_supplicant.conf |grep  ssid|sed -e 's/ssid=//g' -e 's/"//g' -e 's/psk=//g' -e 's/^[ \t]*//g' ''' ,shell=True).decode('utf-8').strip().split('\n')
   wifi_conf_check=wifi[wificounter] in wifi_conf
   if wifi_conf_check is True:
      wifi_psk=subprocess.check_output('''cat /etc/wpa_supplicant/wpa_supplicant.conf |grep {0} -A 1|sed -e 's/ssid=//g' -e 's/"//g' -e 's/{0}//g' -e 's/psk=//g' -e 's/^[ \t]*//g' '''.format(wifi[wificounter]) ,shell=True).decode('utf-8').strip().split('\n')
      moji_in=wifi_psk
   shift=0
   moji=["1","2","3","4","5","6","7","8","9","0","-","BS","q","w","e","r","t","y","u","i",\
   "o","p"," ","⏎","a","s","d","f","g","h","j","k","l",":","'","`","z","x","c","v","b","n",\
      "m",",",".","/","=","@"]
   draw.rectangle((0, 61, 160, 76),outline=(0,0,0), fill=(255,255,255))
   for k in range(48):
    k_size_x, k_size_y  = draw.textsize(moji[k], fonts)
    moji_center_w=(13-k_size_x)/2+1
    draw.rectangle((13*(k-12*(k//12)), 76+13*(k//12), 13*(1+k-12*(k//12)), 76+13*((k//12)+1)),outline=(0,0,0), fill=(217,207,201))
    draw.text((13*(k-12*(k//12))+moji_center_w,76+13*(k//12)),moji[k],  font=fonts, fill=(0, 0, 0))
   draw.rectangle((0, 76, 13, 76+13),outline=(217,207,201), fill=(8,34,109))
   draw.text((4,76),moji[0],  font=fonts, fill=(255,255,255))
   moji_in=("".join(map(str, moji_in)))
   draw.text((1, 61),moji_in,  font=fonts, fill=(0,0,0))
   disp.display(img)
   moji_in=list(moji_in)
   sckey_coordi = 0
   while True:
      mididisp()
      time.sleep(0.001)
      sckey_coordi_size_x, sckey_coordi_size_y  = draw.textsize(moji[sckey_coordi], fonts)
      moji_center_w=(13-sckey_coordi_size_x)/2+1
      if GPIO.input(input_LEFT) == 0:
         draw.rectangle((13*(sckey_coordi-12*(sckey_coordi//12)), 76+13*(sckey_coordi//12), 13*(1+sckey_coordi-12*(sckey_coordi//12)), 76+13*((sckey_coordi//12)+1)),outline=(0,0,0), fill=(217,207,201))
         if moji[sckey_coordi]=="_":
            draw.text((13*(sckey_coordi-12*(sckey_coordi//12))+moji_center_w,76+13*(sckey_coordi//12)-2),moji[sckey_coordi],  font=fonts, fill=(0,0,0))
         else:
            draw.text((13*(sckey_coordi-12*(sckey_coordi//12))+moji_center_w,76+13*(sckey_coordi//12)),moji[sckey_coordi],  font=fonts, fill=(0,0,0))
         sckey_coordi -= 1
         if sckey_coordi==-1 or sckey_coordi==11 or sckey_coordi==23 or sckey_coordi==35:
            sckey_coordi += 12
         sckey_coordi_size_x, sckey_coordi_size_y  = draw.textsize(moji[sckey_coordi], fonts)
         moji_center_w=(13-sckey_coordi_size_x)/2+1
         draw.rectangle((13*(sckey_coordi-12*(sckey_coordi//12)), 76+13*(sckey_coordi//12), 13*(1+sckey_coordi-12*(sckey_coordi//12)), 76+13*((sckey_coordi//12)+1)),outline=(217,207,201), fill=(8,34,109))
         if moji[sckey_coordi]=="_":
            draw.text((13*(sckey_coordi-12*(sckey_coordi//12))+moji_center_w,76+13*(sckey_coordi//12)-2),moji[sckey_coordi],  font=fonts, fill=(255,255,255))
         else:
            draw.text((13*(sckey_coordi-12*(sckey_coordi//12))+moji_center_w,76+13*(sckey_coordi//12)),moji[sckey_coordi],  font=fonts, fill=(255,255,255))
         disp.display(img) 
         longpush_(input_LEFT)
      if GPIO.input(input_RIGHT) == 0:  
         draw.rectangle((13*(sckey_coordi-12*(sckey_coordi//12)), 76+13*(sckey_coordi//12), 13*(1+sckey_coordi-12*(sckey_coordi//12)), 76+13*((sckey_coordi//12)+1)),outline=(0,0,0), fill=(217,207,201))
         if moji[sckey_coordi]=="_":
            draw.text((13*(sckey_coordi-12*(sckey_coordi//12))+moji_center_w,76+13*(sckey_coordi//12)-2),moji[sckey_coordi],  font=fonts, fill=(0,0,0))
         else:
            draw.text((13*(sckey_coordi-12*(sckey_coordi//12))+moji_center_w,76+13*(sckey_coordi//12)),moji[sckey_coordi],  font=fonts, fill=(0,0,0))
         sckey_coordi += 1
         if sckey_coordi==12 or sckey_coordi==24 or sckey_coordi==36 or sckey_coordi==48:
            sckey_coordi -= 12
         sckey_coordi_size_x, sckey_coordi_size_y  = draw.textsize(moji[sckey_coordi], fonts)
         moji_center_w=(13-sckey_coordi_size_x)/2+1
         draw.rectangle((13*(sckey_coordi-12*(sckey_coordi//12)), 76+13*(sckey_coordi//12), 13*(1+sckey_coordi-12*(sckey_coordi//12)), 76+13*((sckey_coordi//12)+1)),outline=(217,207,201), fill=(8,34,109))
         if moji[sckey_coordi]=="_":
            draw.text((13*(sckey_coordi-12*(sckey_coordi//12))+moji_center_w,76+13*(sckey_coordi//12)-2),moji[sckey_coordi],  font=fonts, fill=(255,255,255))
         else:
            draw.text((13*(sckey_coordi-12*(sckey_coordi//12))+moji_center_w,76+13*(sckey_coordi//12)),moji[sckey_coordi],  font=fonts, fill=(255,255,255))
         disp.display(img) 
         longpush_(input_RIGHT)
      if GPIO.input(input_UP) == 0:
         draw.rectangle((13*(sckey_coordi-12*(sckey_coordi//12)), 76+13*(sckey_coordi//12), 13*(1+sckey_coordi-12*(sckey_coordi//12)), 76+13*((sckey_coordi//12)+1)),outline=(0,0,0), fill=(217,207,201))
         if moji[sckey_coordi]=="_":
            draw.text((13*(sckey_coordi-12*(sckey_coordi//12))+moji_center_w,76+13*(sckey_coordi//12)-2),moji[sckey_coordi],  font=fonts, fill=(0,0,0))
         else:
            draw.text((13*(sckey_coordi-12*(sckey_coordi//12))+moji_center_w,76+13*(sckey_coordi//12)),moji[sckey_coordi],  font=fonts, fill=(0,0,0))
         sckey_coordi -= 12
         if sckey_coordi <=-1:
            sckey_coordi += 48
         sckey_coordi_size_x, sckey_coordi_size_y  = draw.textsize(moji[sckey_coordi], fonts)
         moji_center_w=(13-sckey_coordi_size_x)/2+1
         draw.rectangle((13*(sckey_coordi-12*(sckey_coordi//12)), 76+13*(sckey_coordi//12), 13*(1+sckey_coordi-12*(sckey_coordi//12)), 76+13*((sckey_coordi//12)+1)),outline=(217,207,201), fill=(8,34,109))
         if moji[sckey_coordi]=="_":
            draw.text((13*(sckey_coordi-12*(sckey_coordi//12))+moji_center_w,76+13*(sckey_coordi//12)-2),moji[sckey_coordi],  font=fonts, fill=(255,255,255))
         else:
            draw.text((13*(sckey_coordi-12*(sckey_coordi//12))+moji_center_w,76+13*(sckey_coordi//12)),moji[sckey_coordi],  font=fonts, fill=(255,255,255))
         disp.display(img) 
         longpush_(input_UP)
      if GPIO.input(input_DOWN) == 0:   
         draw.rectangle((13*(sckey_coordi-12*(sckey_coordi//12)), 76+13*(sckey_coordi//12), 13*(1+sckey_coordi-12*(sckey_coordi//12)), 76+13*((sckey_coordi//12)+1)),outline=(0,0,0), fill=(217,207,201))
         if moji[sckey_coordi]=="_":
            draw.text((13*(sckey_coordi-12*(sckey_coordi//12))+moji_center_w,76+13*(sckey_coordi//12)-2),moji[sckey_coordi],  font=fonts, fill=(0,0,0))
         else:
            draw.text((13*(sckey_coordi-12*(sckey_coordi//12))+moji_center_w,76+13*(sckey_coordi//12)),moji[sckey_coordi],  font=fonts, fill=(0,0,0))
         sckey_coordi += 12  
         if sckey_coordi >=48:
            sckey_coordi -= 48
         sckey_coordi_size_x, sckey_coordi_size_y  = draw.textsize(moji[sckey_coordi], fonts)
         moji_center_w=(13-sckey_coordi_size_x)/2+1
         draw.rectangle((13*(sckey_coordi-12*(sckey_coordi//12)), 76+13*(sckey_coordi//12), 13*(1+sckey_coordi-12*(sckey_coordi//12)), 76+13*((sckey_coordi//12)+1)),outline=(217,207,201), fill=(8,34,109))
         if moji[sckey_coordi]=="_":
            draw.text((13*(sckey_coordi-12*(sckey_coordi//12))+moji_center_w,76+13*(sckey_coordi//12)-2),moji[sckey_coordi],  font=fonts, fill=(255,255,255))
         else:
            draw.text((13*(sckey_coordi-12*(sckey_coordi//12))+moji_center_w,76+13*(sckey_coordi//12)),moji[sckey_coordi],  font=fonts, fill=(255,255,255))
         disp.display(img) 
         longpush_(input_DOWN)
      if GPIO.input(input_OK) == 0 : 
         if sckey_coordi !=11 and sckey_coordi !=23 and len(moji_in) < 22:
            draw.rectangle((0, 61, 160, 76),outline=(0,0,0), fill=(255,255,255))
            moji_in.append(moji[sckey_coordi] )
            moji_in=("".join(map(str, moji_in)))
            draw.text((1, 61),moji_in,  font=fonts, fill=(0,0,0))
            disp.display(img)
            moji_in=list(moji_in)
         if sckey_coordi == 11 and moji_in !=[]:
            draw.rectangle((0, 61, 160, 76),outline=(0,0,0), fill=(255,255,255))
            moji_in.pop()
            moji_in=("".join(map(str, moji_in)))
            draw.text((1, 61),moji_in,  font=fonts, fill=(0,0,0))
            disp.display(img)
            moji_in=list(moji_in)
         if sckey_coordi == 23 :
            moji_in=("".join(map(str, moji_in)))
            wifi_psk=("".join(map(str, wifi_psk)))
            if wifi_psk==moji_in:
               mode2_default_disp()
               mode=2
               dialog_open=0
               longpush_(input_OK)
               break
            if wifi_psk !="" and moji_in !="" and wifi_psk !=moji_in:
               tmp0="/{0}/".format(wifi[wificounter])
               tmp1="{"+"n;s/{0}/{1}/;".format(wifi[wificounter],wifi_psk,moji_in)
               tmp=tmp0+tmp1+"}"
               subprocess.call('''cat /etc/wpa_supplicant/wpa_supplicant.conf |sudo sed -i -e '{}' /etc/wpa_supplicant/wpa_supplicant.conf'''.format(tmp) ,shell=True)
               subprocess.call('''sudo wpa_cli -i wlan0 reconfigure''' ,shell=True)
               mode2_default_disp()
               mode=2
               dialog_open=0
               longpush_(input_OK)
               break
            if wifi_psk =="":
               subprocess.call('''sudo sed -i -e '$ a network={' /etc/wpa_supplicant/wpa_supplicant.conf''' ,shell=True)
               subprocess.call('''sudo sed -i -e '$ a ssid="{}"' /etc/wpa_supplicant/wpa_supplicant.conf''' .format(wifi[wificounter]),shell=True)
               subprocess.call('''sudo sed -i -e '$ a psk="{}"' /etc/wpa_supplicant/wpa_supplicant.conf''' .format(moji_in),shell=True)
               subprocess.call('''sudo sed -i -e '$ a }' /etc/wpa_supplicant/wpa_supplicant.conf''' ,shell=True)
               subprocess.call('''sudo wpa_cli -i wlan0 reconfigure''' ,shell=True)
               mode2_default_disp()
               mode=2
               dialog_open=0
               longpush_(input_OK)
               break
            if moji_in =="":
               delconf=subprocess.check_output('''grep -A 2 -B 1 {} -n /etc/wpa_supplicant/wpa_supplicant.conf| sed -e 's/:.*//g' -e 's/-.*//g' ''' .format(wifi[wificounter]) ,shell=True).decode('utf-8').strip().split('\n')
               subprocess.call('''sudo sed -i '{},{}d' /etc/wpa_supplicant/wpa_supplicant.conf ''' .format(delconf[0],delconf[len(delconf)-1]) ,shell=True)
               subprocess.call('''sudo wpa_cli -i wlan0 reconfigure''' ,shell=True)
               mode2_default_disp()
               mode=2
               dialog_open=0
               longpush_(input_OK)
               break
         longpush_(input_OK)
      if GPIO.input(input_MODE) == 0 and shift==0: 
         shift=1
         moji=["!","¥","#","＄","%","^","&","*","(",")","_","BS","Q","W","E","R","T","Y","U","I",\
         "O","P"," ","⏎","A","S","D","F","G","H","J","K","L",";",'"',"~","Z","X","C","V","B","N",\
            "M","<",">","?","+","|"]
         for k in range(48):
          k_size_x, k_size_y  = draw.textsize(moji[k], fonts)
          moji_center_w=(13-k_size_x)/2+1
          draw.rectangle((13*(k-12*(k//12)), 76+13*(k//12), 13*(1+k-12*(k//12)), 76+13*((k//12)+1)),outline=(0,0,0), fill=(217,207,201))
          if moji[k]=="_":
             draw.text((13*(k-12*(k//12))+moji_center_w,76+13*(k//12)-2),moji[k],  font=fonts, fill=(0, 0, 0))
          else:
            draw.text((13*(k-12*(k//12))+moji_center_w,76+13*(k//12)),moji[k],  font=fonts, fill=(0, 0, 0))
         sckey_coordi_size_x, sckey_coordi_size_y  = draw.textsize(moji[sckey_coordi], fonts)
         moji_center_w=(13-sckey_coordi_size_x)/2+1
         draw.rectangle((13*(sckey_coordi-12*(sckey_coordi//12)), 76+13*(sckey_coordi//12), 13*(1+sckey_coordi-12*(sckey_coordi//12)), 76+13*((sckey_coordi//12)+1)),outline=(217,207,201), fill=(8,34,109))
         if moji[sckey_coordi]=="_":
            draw.text((13*(sckey_coordi-12*(sckey_coordi//12))+moji_center_w,76+13*(sckey_coordi//12)-2),moji[sckey_coordi],  font=fonts, fill=(255,255,255))
         else:
            draw.text((13*(sckey_coordi-12*(sckey_coordi//12))+moji_center_w,76+13*(sckey_coordi//12)),moji[sckey_coordi],  font=fonts, fill=(255,255,255))
         disp.display(img)

      if GPIO.input(input_MODE) == 1 and shift==1:
         shift=0
         moji=["1","2","3","4","5","6","7","8","9","0","-","BS","q","w","e","r","t","y","u","i",\
            "o","p"," ","⏎","a","s","d","f","g","h","j","k","l",":","'","`","z","x","c","v","b","n",\
               "m",",",".","/","=","@"]
         for k in range(48):
          k_size_x, k_size_y  = draw.textsize(moji[k], fonts)
          moji_center_w=(13-k_size_x)/2+1
          draw.rectangle((13*(k-12*(k//12)), 76+13*(k//12), 13*(1+k-12*(k//12)), 76+13*((k//12)+1)),outline=(0,0,0), fill=(217,207,201))
          draw.text((13*(k-12*(k//12))+moji_center_w,76+13*(k//12)),moji[k],  font=fonts, fill=(0, 0, 0))
         sckey_coordi_size_x, sckey_coordi_size_y  = draw.textsize(moji[sckey_coordi], fonts)
         moji_center_w=(13-sckey_coordi_size_x)/2+1
         draw.rectangle((13*(sckey_coordi-12*(sckey_coordi//12)), 76+13*(sckey_coordi//12), 13*(1+sckey_coordi-12*(sckey_coordi//12)), 76+13*((sckey_coordi//12)+1)),outline=(217,207,201), fill=(8,34,109))
         draw.text((13*(sckey_coordi-12*(sckey_coordi//12))+moji_center_w,76+13*(sckey_coordi//12)),moji[sckey_coordi],  font=fonts, fill=(255,255,255))
         disp.display(img)
      if (GPIO.input(input_LEFT) and GPIO.input(input_RIGHT) and GPIO.input(input_UP) and GPIO.input(input_DOWN) and GPIO.input(input_OK))== 1:  
         longpush=0

##初期設定ここまで##
time.sleep(1)
msg = None
mode0_default_disp()
while True:
    try:
     if aplaymidi.poll() is not None:
        if mode == 1 and playflag[midicounter] == 1:
           draw.rectangle((t_size_m_x*13, t_size_l_y+t_size_m_y*3+1, 160, t_size_l_y+t_size_m_y*4+2), (0,0,0))
           disp.display(img)
        playflag = [0]*len(midi)
    except:
     pass
    mididisp()
    if GPIO.input(input_LEFT) == 0 and GPIO.input(input_MODE) != 0: 
       time.sleep(0.00001)
       if mode==0:
          if mode0_coordi ==0:
             midiCH -=1
             if midiCH<0:
                midiCH=15 
             draw.rectangle((t_size_l_x*4,0, t_size_l_x*6,t_size_l_y), (0,0,0))
             draw.text((t_size_l_x*4, 0),str("{0:02}".format(midiCH + 1)),  font=fontl, fill=(255, 255, 55))
             draw.rectangle((t_size_m_x*5, t_size_l_y+t_size_m_y+1, 65, 128), (0,0,0))
             draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y+1),str("{0:03d}".format(midiPROG[midiCH] + 1)), font=fontm, fill=(255, 255, 55))
             draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*2+1),str("{0:03d}".format(midiCC7[midiCH])),  font=fontm, fill=(255, 255, 55))
             draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*3+1),str("{0:03d}".format(midiCC11[midiCH])),  font=fontm, fill=(255, 255, 55))
             draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*4+1),str("{0:03d}".format(midiCC10[midiCH]-64)),  font=fontm, fill=(255, 255, 55))
             draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*5+1),str("{0:03d}".format(midiCC1[midiCH])),  font=fontm, fill=(255, 255, 55))
             draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*6+1),str("{0:03d}".format(midiCC91[midiCH])), font=fontm, fill=(255, 255, 55))
             draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*7+1),str("{0:03d}".format(midiCC93[midiCH])),  font=fontm, fill=(255, 255, 55))
             draw.rectangle((t_size_m_x*18, t_size_l_y+t_size_m_y+1, 160, 128), (0,0,0))
             draw.text((t_size_m_x*18, t_size_l_y+t_size_m_y+1),str("{0:03d}".format(midiCC94[midiCH])), font=fontm, fill=(255, 255, 55))
             draw.text((t_size_m_x*18, t_size_l_y+t_size_m_y*2+1),str("{0:04d}".format(0x80*pb2[midiCH]+pb1[midiCH]-8192)), font=fontm, fill=(255, 255, 55))       
             disp.display(img)
          if mode0_coordi ==1:
             midiPROG[midiCH] -=1
             if midiPROG[midiCH] <0:
                midiPROG[midiCH] =127
             draw.rectangle((t_size_m_x*5, t_size_l_y+t_size_m_y+1, 65, t_size_l_y+t_size_m_y*2), (0,0,0))
             draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y+1),str("{0:03d}".format(midiPROG[midiCH] + 1)), font=fontm, fill=(255, 255, 55))
             disp.display(img)
             midiout.send_message([0xc0+midiCH, midiPROG[midiCH]])
          if mode0_coordi ==2:
             midiCC7[midiCH] -=1
             if midiCC7[midiCH] <0:
                midiCC7[midiCH] =127
             draw.rectangle((t_size_m_x*5, t_size_l_y+t_size_m_y*2+1, 65, t_size_l_y+t_size_m_y*3), (0,0,0))
             draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*2+1),str("{0:03d}".format(midiCC7[midiCH])),  font=fontm, fill=(255, 255, 55))
             disp.display(img)
             midiout.send_message([0xb0+midiCH, 7, midiCC7[midiCH]])
          if mode0_coordi ==3:
             midiCC11[midiCH] -=1
             if midiCC11[midiCH] <0:
                midiCC11[midiCH] =127
             draw.rectangle((t_size_m_x*5, t_size_l_y+t_size_m_y*3+1, 65, t_size_l_y+t_size_m_y*4), (0,0,0))
             draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*3+1),str("{0:03d}".format(midiCC11[midiCH])),  font=fontm, fill=(255, 255, 55))
             disp.display(img) 
             midiout.send_message([0xb0+midiCH, 11, midiCC11[midiCH]]) 
          if mode0_coordi ==4:
             midiCC10[midiCH] -=1
             if midiCC10[midiCH] <0:
                midiCC10[midiCH] =127
             draw.rectangle((t_size_m_x*5, t_size_l_y+t_size_m_y*4+1, 65, t_size_l_y+t_size_m_y*5), (0,0,0))
             draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*4+1),str("{0:03d}".format(midiCC10[midiCH]-64)),  font=fontm, fill=(255, 255, 55))
             disp.display(img)
             midiout.send_message([0xb0+midiCH, 10, midiCC10[midiCH]])
          if mode0_coordi ==5:
             midiCC1[midiCH] -=1
             if midiCC1[midiCH] <0:
                midiCC1[midiCH] =127
             draw.rectangle((t_size_m_x*5, t_size_l_y+t_size_m_y*5+1, 65, t_size_l_y+t_size_m_y*6), (0,0,0))
             draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*5+1),str("{0:03d}".format(midiCC1[midiCH])),  font=fontm, fill=(255, 255, 55))
             disp.display(img)
             midiout.send_message([0xb0+midiCH, 1, midiCC1[midiCH]])
          if mode0_coordi ==6:
             midiCC91[midiCH] -=1
             if midiCC91[midiCH] <0:
                midiCC91[midiCH] =127
             draw.rectangle((t_size_m_x*5, t_size_l_y+t_size_m_y*6+1, 65, t_size_l_y+t_size_m_y*7), (0,0,0))
             draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*6+1),str("{0:03d}".format(midiCC91[midiCH])), font=fontm, fill=(255, 255, 55))
             disp.display(img)
             midiout.send_message([0xb0+midiCH, 91, midiCC91[midiCH]])
          if mode0_coordi ==7:
             midiCC93[midiCH] -=1
             if midiCC93[midiCH] <0:
                midiCC93[midiCH] =127
             draw.rectangle((t_size_m_x*5, t_size_l_y+t_size_m_y*7+1, 65, 128), (0,0,0))
             draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*7+1),str("{0:03d}".format(midiCC93[midiCH])),  font=fontm, fill=(255, 255, 55))
             midiout.send_message([0xb0+midiCH, 93, midiCC93[midiCH]])
             disp.display(img)
          if mode0_coordi ==8:
             midiCC94[midiCH] -=1
             if midiCC94[midiCH] <0:
                midiCC94[midiCH] =127
             draw.rectangle((t_size_m_x*18, t_size_l_y+t_size_m_y+1, 160,  t_size_l_y+t_size_m_y*2), (0,0,0))
             draw.text((t_size_m_x*18, t_size_l_y+t_size_m_y+1),str("{0:03d}".format(midiCC94[midiCH])), font=fontm, fill=(255, 255, 55))
             midiout.send_message([0xb0+midiCH, 94, midiCC94[midiCH]])
             disp.display(img)
          if mode0_coordi ==9:
             pb1[midiCH] -= 1
             if pb1[midiCH] < 0:
                pb1[midiCH] = 0x7f
                if pb2[midiCH] == 0:
                   pb1[midiCH] = 0x7f
                   pb2[midiCH] = 0x7f
                else:
                   pb2[midiCH] -= 1
             draw.rectangle((t_size_m_x*18, t_size_l_y+t_size_m_y*2+1, 160, t_size_l_y+t_size_m_y*3), (0,0,0))
             draw.text((t_size_m_x*18, t_size_l_y+t_size_m_y*2+1),str("{0:04d}".format(0x80*pb2[midiCH]+pb1[midiCH]-8192)), font=fontm, fill=(255, 255, 55))
             disp.display(img)
             midiout.send_message([0xe0+midiCH, pb1[midiCH], pb2[midiCH]])

       if mode==1:
          if mode1_coordi ==0:
             sf2counter -= 1
             if sf2counter == -1:
                sf2counter =  len(sf2) -1
             draw.rectangle((t_size_m_x*5, t_size_l_y+t_size_m_y+1, 160, t_size_l_y+t_size_m_y*2+2), (0,0,0))
             draw.rectangle((9, t_size_l_y+t_size_m_y*2+1, 160, t_size_l_y+t_size_m_y*3+2), (0,0,0))
             draw.text((9+t_size_m_x*4, t_size_l_y+t_size_m_y+1),"{0:03d}/{1:03d}" .format(sf2counter + 1 ,len(sf2)), font=fontm, fill=(55, 255, 255))
             draw.text((9, t_size_l_y+t_size_m_y*2+1),sf2[sf2counter], font=fontm, fill=(255, 255, 55))
             if sf2used[sf2counter]==1:
                 draw.text((9, t_size_l_y+t_size_m_y+1),"            ♪", font=fontm, fill=(55, 255, 255))
             disp.display(img)
          if mode1_coordi ==1:
             midicounter -= 1
             if midicounter == -1:
                midicounter =  len(midi)-1
             draw.rectangle((t_size_m_x*5, t_size_l_y+t_size_m_y*3+1, 160, t_size_l_y+t_size_m_y*4+2), (0,0,0))
             draw.rectangle((9, t_size_l_y+t_size_m_y*4+1, 160, t_size_l_y+t_size_m_y*5+2), (0,0,0))
             draw.text((9+t_size_m_x*4, t_size_l_y+t_size_m_y*3+1),"{0:03d}/{1:03d}".format(midicounter + 1 ,len(midi) ), font=fontm, fill=(55, 255, 255))
             draw.text((9, t_size_l_y+t_size_m_y*4+1),midi[midicounter],  font=fontm, fill=(255, 255, 55))
             if playflag[midicounter]==1:
                draw.text((9, t_size_l_y+t_size_m_y*3+1),"            ▶", font=fontm, fill=(55, 255, 255))
             disp.display(img)
       if mode==3:
          wificounter -=1
          if wificounter == -1:
             wificounter =  len(wifi) -1
          draw.rectangle((9+t_size_m_x*5, t_size_l_y+t_size_m_y+1, 9+t_size_m_x*8, t_size_l_y+t_size_m_y*2+2), (0,0,0))
          draw.rectangle((9, t_size_l_y+t_size_m_y*2+1, 160, t_size_l_y+t_size_m_y*3+2), (0,0,0))
          draw.text((9, t_size_l_y+t_size_m_y+1),"     {0:03d}" .format(wificounter+1), font=fontm, fill=(55, 255, 255))
          draw.text((9, t_size_l_y+t_size_m_y*2+1),wifi[wificounter], font=fontm, fill=(255, 255, 55))
          disp.display(img)
       longpush_(input_LEFT)

    if GPIO.input(input_RIGHT) == 0 and GPIO.input(input_MODE) != 0: 
       time.sleep(0.00001)
       if mode==0:
          if mode0_coordi ==0:
             midiCH +=1
             if midiCH>15:
                midiCH=0 
             draw.rectangle((t_size_l_x*4,0, t_size_l_x*6,t_size_l_y), (0,0,0))
             draw.text((t_size_l_x*4, 0),str("{0:02}".format(midiCH + 1)),  font=fontl, fill=(255, 255, 55))
             draw.rectangle((t_size_m_x*5, t_size_l_y+t_size_m_y+1, 65, 128), (0,0,0))
             draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y+1),str("{0:03d}".format(midiPROG[midiCH] + 1)), font=fontm, fill=(255, 255, 55))
             draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*2+1),str("{0:03d}".format(midiCC7[midiCH])),  font=fontm, fill=(255, 255, 55))
             draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*3+1),str("{0:03d}".format(midiCC11[midiCH])),  font=fontm, fill=(255, 255, 55))
             draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*4+1),str("{0:03d}".format(midiCC10[midiCH]-64)),  font=fontm, fill=(255, 255, 55))
             draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*5+1),str("{0:03d}".format(midiCC1[midiCH])),  font=fontm, fill=(255, 255, 55))
             draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*6+1),str("{0:03d}".format(midiCC91[midiCH])), font=fontm, fill=(255, 255, 55))
             draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*7+1),str("{0:03d}".format(midiCC93[midiCH])),  font=fontm, fill=(255, 255, 55))
             draw.rectangle((t_size_m_x*18, t_size_l_y+t_size_m_y+1, 160, 128), (0,0,0))
             draw.text((t_size_m_x*18, t_size_l_y+t_size_m_y+1),str("{0:03d}".format(midiCC94[midiCH])), font=fontm, fill=(255, 255, 55))
             draw.text((t_size_m_x*18, t_size_l_y+t_size_m_y*2+1),str("{0:04d}".format(0x80*pb2[midiCH]+pb1[midiCH]-8192)), font=fontm, fill=(255, 255, 55))
             disp.display(img)
          if mode0_coordi ==1:
             midiPROG[midiCH] +=1
             if midiPROG[midiCH] >127:
                midiPROG[midiCH] =0
             draw.rectangle((t_size_m_x*5, t_size_l_y+t_size_m_y+1, 65, t_size_l_y+t_size_m_y*2), (0,0,0))
             draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y+1),str("{0:03d}".format(midiPROG[midiCH] + 1)), font=fontm, fill=(255, 255, 55))
             disp.display(img) 
             midiout.send_message([0xc0+midiCH, midiPROG[midiCH]])
          if mode0_coordi ==2:
             midiCC7[midiCH] +=1
             if midiCC7[midiCH] >127:
                midiCC7[midiCH] =0
             draw.rectangle((t_size_m_x*5, t_size_l_y+t_size_m_y*2+1, 65, t_size_l_y+t_size_m_y*3), (0,0,0))
             draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*2+1),str("{0:03d}".format(midiCC7[midiCH])),  font=fontm, fill=(255, 255, 55))
             disp.display(img) 
             midiout.send_message([0xb0+midiCH, 7, midiCC7[midiCH]])
          if mode0_coordi ==3:
             midiCC11[midiCH] +=1
             if midiCC11[midiCH] >127:
                midiCC11[midiCH] =0
             draw.rectangle((t_size_m_x*5, t_size_l_y+t_size_m_y*3+1, 65, t_size_l_y+t_size_m_y*4), (0,0,0))
             draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*3+1),str("{0:03d}".format(midiCC11[midiCH])),  font=fontm, fill=(255, 255, 55))
             disp.display(img) 
             midiout.send_message([0xb0+midiCH, 11, midiCC11[midiCH]])
          if mode0_coordi ==4:
             midiCC10[midiCH] +=1
             if midiCC10[midiCH] >127:
                midiCC10[midiCH] =0
             draw.rectangle((t_size_m_x*5, t_size_l_y+t_size_m_y*4+1, 65, t_size_l_y+t_size_m_y*5), (0,0,0))
             draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*4+1),str("{0:03d}".format(midiCC10[midiCH]-64)),  font=fontm, fill=(255, 255, 55))
             disp.display(img)
             midiout.send_message([0xb0+midiCH, 10, midiCC10[midiCH]])
          if mode0_coordi ==5:
             midiCC1[midiCH] +=1
             if midiCC1[midiCH] >127:
                midiCC1[midiCH] =0
             draw.rectangle((t_size_m_x*5, t_size_l_y+t_size_m_y*5+1, 65, t_size_l_y+t_size_m_y*6), (0,0,0))
             draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*5+1),str("{0:03d}".format(midiCC1[midiCH])),  font=fontm, fill=(255, 255, 55))
             disp.display(img)
             midiout.send_message([0xb0+midiCH, 1, midiCC1[midiCH]])
          if mode0_coordi ==6:
             midiCC91[midiCH] +=1
             if midiCC91[midiCH] >127:
                midiCC91[midiCH] =0
             draw.rectangle((t_size_m_x*5, t_size_l_y+t_size_m_y*6+1, 65, t_size_l_y+t_size_m_y*7), (0,0,0))
             draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*6+1),str("{0:03d}".format(midiCC91[midiCH])), font=fontm, fill=(255, 255, 55))
             disp.display(img)
             midiout.send_message([0xb0+midiCH, 91, midiCC91[midiCH]])
          if mode0_coordi ==7:
             midiCC93[midiCH] +=1
             if midiCC93[midiCH] >127:
                midiCC93[midiCH] =0
             draw.rectangle((t_size_m_x*5, t_size_l_y+t_size_m_y*7+1, 65, 128), (0,0,0))
             draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*7+1),str("{0:03d}".format(midiCC93[midiCH])),  font=fontm, fill=(255, 255, 55))
             midiout.send_message([0xb0+midiCH, 93, midiCC93[midiCH]])
             disp.display(img)
          if mode0_coordi ==8:
             midiCC94[midiCH] +=1
             if midiCC94[midiCH] >127:
                midiCC94[midiCH] =0
             draw.rectangle((t_size_m_x*18, t_size_l_y+t_size_m_y+1, 160,  t_size_l_y+t_size_m_y*2), (0,0,0))
             draw.text((t_size_m_x*18, t_size_l_y+t_size_m_y+1),str("{0:03d}".format(midiCC94[midiCH])), font=fontm, fill=(255, 255, 55))
             midiout.send_message([0xb0+midiCH, 94, midiCC94[midiCH]])
             disp.display(img)
          if mode0_coordi ==9:
             pb1[midiCH] += 1
             if pb1[midiCH] > 0x7f:
                pb1[midiCH] = 0
                pb2[midiCH] += 1
                if pb2[midiCH] > 0x7f:
                   pb2[midiCH] = 0
             draw.rectangle((t_size_m_x*18, t_size_l_y+t_size_m_y*2+1, 160, t_size_l_y+t_size_m_y*3), (0,0,0))
             draw.text((t_size_m_x*18, t_size_l_y+t_size_m_y*2+1),str("{0:04d}".format(0x80*pb2[midiCH]+pb1[midiCH]-8192)), font=fontm, fill=(255, 255, 55))
             disp.display(img)
             midiout.send_message([0xe0+midiCH, pb1[midiCH], pb2[midiCH]])

       if mode==1:
          if mode1_coordi ==0:
             sf2counter += 1
             if sf2counter == len(sf2):
                sf2counter = 0
             draw.rectangle((t_size_m_x*5, t_size_l_y+t_size_m_y+1, 160, t_size_l_y+t_size_m_y*2+2), (0,0,0))
             draw.rectangle((9, t_size_l_y+t_size_m_y*2+1, 160, t_size_l_y+t_size_m_y*3+2), (0,0,0))
             draw.text((9+t_size_m_x*4, t_size_l_y+t_size_m_y+1),"{0:03d}/{1:03d}" .format(sf2counter + 1 ,len(sf2)), font=fontm, fill=(55, 255, 255))
             draw.text((9, t_size_l_y+t_size_m_y*2+1),sf2[sf2counter], font=fontm, fill=(255, 255, 55))
             if sf2used[sf2counter]==1:
                draw.text((9, t_size_l_y+t_size_m_y+1),"            ♪", font=fontm, fill=(55, 255, 255))
             disp.display(img)
          if mode1_coordi ==1:
             midicounter += 1
             if midicounter == len(midi):
                midicounter = 0
             draw.rectangle((t_size_m_x*5, t_size_l_y+t_size_m_y*3+1, 160, t_size_l_y+t_size_m_y*4+2), (0,0,0))
             draw.rectangle((9, t_size_l_y+t_size_m_y*4+1, 160, t_size_l_y+t_size_m_y*5+2), (0,0,0))
             draw.text((9+t_size_m_x*4, t_size_l_y+t_size_m_y*3+1),"{0:03d}/{1:03d}".format(midicounter + 1 ,len(midi) ), font=fontm, fill=(55, 255, 255))
             draw.text((9, t_size_l_y+t_size_m_y*4+1),midi[midicounter],  font=fontm, fill=(255, 255, 55))  
             if playflag[midicounter]==1:
                draw.text((9, t_size_l_y+t_size_m_y*3+1),"            ▶", font=fontm, fill=(55, 255, 255))
             disp.display(img) 
       if mode==3:
          wificounter +=1
          if wificounter==len(wifi):
             wificounter=0
          draw.rectangle((9+t_size_m_x*5, t_size_l_y+t_size_m_y+1, 9+t_size_m_x*8, t_size_l_y+t_size_m_y*2+2), (0,0,0))
          draw.rectangle((9, t_size_l_y+t_size_m_y*2+1, 160, t_size_l_y+t_size_m_y*3+2), (0,0,0))
          draw.text((9, t_size_l_y+t_size_m_y+1),"     {0:03d}" .format(wificounter+1), font=fontm, fill=(55, 255, 255))
          draw.text((9, t_size_l_y+t_size_m_y*2+1),wifi[wificounter], font=fontm, fill=(255, 255, 55))
          disp.display(img)

       longpush_(input_RIGHT)
      

    if GPIO.input(input_UP) == 0 and GPIO.input(input_MODE) != 0: 
       time.sleep(0.01)
       if mode==0 and GPIO.input(input_OK) != 0:
          draw.rectangle((mode0_coordi_xl[mode0_coordi], mode0_coordi_yl[mode0_coordi],mode0_coordi_xl[mode0_coordi]+cur_size_x, mode0_coordi_yl[mode0_coordi]+cur_size_y), (0,0,0))
          mode0_coordi -=1
          if mode0_coordi <0:
             mode0_coordi=9
          draw.text((mode0_coordi_xl[mode0_coordi], mode0_coordi_yl[mode0_coordi]),cur_size,  font=fontss, fill=(255, 255, 255))   
          disp.display(img) 
       if mode==1 and GPIO.input(input_OK) != 0:
          draw.rectangle((mode1_coordi_xl[mode1_coordi], mode1_coordi_yl[mode1_coordi],mode1_coordi_xl[mode1_coordi]+cur_size_x, mode1_coordi_yl[mode1_coordi]+cur_size_y), (0,0,0))
          mode1_coordi -=1
          if mode1_coordi <0:
             mode1_coordi=1
          draw.text((mode1_coordi_xl[mode1_coordi], mode1_coordi_yl[mode1_coordi]),cur_size,  font=fontss, fill=(255, 255, 255)) 
          disp.display(img)  
       if mode==2 and GPIO.input(input_OK) != 0:
          draw.rectangle((mode2_coordi_xl[mode2_coordi], mode2_coordi_yl[mode2_coordi],mode2_coordi_xl[mode2_coordi]+cur_size_x, mode2_coordi_yl[mode2_coordi]+cur_size_y), (0,0,0))
          mode2_coordi -=1
          if mode2_coordi <0:
             mode2_coordi=6
          draw.text((mode2_coordi_xl[mode2_coordi], mode2_coordi_yl[mode2_coordi]),cur_size,  font=fontss, fill=(255, 255, 255))  
          disp.display(img) 
       longpush_(input_UP)

    if GPIO.input(input_DOWN) == 0 and GPIO.input(input_MODE) != 0: 
       time.sleep(0.01)
       if mode==0 and GPIO.input(input_OK) != 0:
          draw.rectangle((mode0_coordi_xl[mode0_coordi], mode0_coordi_yl[mode0_coordi],mode0_coordi_xl[mode0_coordi]+cur_size_x, mode0_coordi_yl[mode0_coordi]+cur_size_y), (0,0,0))
          mode0_coordi +=1
          if mode0_coordi >9:
             mode0_coordi=0
          draw.text((mode0_coordi_xl[mode0_coordi], mode0_coordi_yl[mode0_coordi]),cur_size,  font=fontss, fill=(255, 255, 255)) 
          disp.display(img)
       if mode==1 and GPIO.input(input_OK) != 0:
          draw.rectangle((mode1_coordi_xl[mode1_coordi], mode1_coordi_yl[mode1_coordi],mode1_coordi_xl[mode1_coordi]+cur_size_x, mode1_coordi_yl[mode1_coordi]+cur_size_y), (0,0,0))
          mode1_coordi +=1
          if mode1_coordi >1:
             mode1_coordi=0
          draw.text((mode1_coordi_xl[mode1_coordi], mode1_coordi_yl[mode1_coordi]),cur_size,  font=fontss, fill=(255, 255, 255)) 
          disp.display(img)  
       if mode==2 and GPIO.input(input_OK) != 0:
          draw.rectangle((mode2_coordi_xl[mode2_coordi], mode2_coordi_yl[mode2_coordi],mode2_coordi_xl[mode2_coordi]+cur_size_x, mode2_coordi_yl[mode2_coordi]+cur_size_y), (0,0,0))
          mode2_coordi +=1
          if mode2_coordi >6:
             mode2_coordi=0
          draw.text((mode2_coordi_xl[mode2_coordi], mode2_coordi_yl[mode2_coordi]),cur_size,  font=fontss, fill=(255, 255, 255))  
          disp.display(img) 
       longpush_(input_DOWN)

    if GPIO.input(input_MODE) == 0:  
       time.sleep(0.0001)
       if GPIO.input(input_RIGHT) == 0:
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
                draw.text((9, t_size_l_y+t_size_m_y+1),"            ♪", font=fontm, fill=(55, 255, 255))
                disp.display(img)
             if playflag[midicounter]==1:
                draw.text((9, t_size_l_y+t_size_m_y*3+1),"            ▶", font=fontm, fill=(55, 255, 255))
                disp.display(img)
          if mode==2:      
             mode2_default_disp()
       longpush_(input_RIGHT)
       if GPIO.input(input_LEFT) == 0:
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
                draw.text((9, t_size_l_y+t_size_m_y+1),"            ♪", font=fontm, fill=(55, 255, 255))
                disp.display(img)
             if playflag[midicounter]==1:
                draw.text((9, t_size_l_y+t_size_m_y*3+1),"            ▶", font=fontm, fill=(55, 255, 255))
                disp.display(img)
          if mode==2:      
             mode2_default_disp()
       longpush_(input_LEFT)

       if GPIO.input(input_UP) == 0:
          dialog_open=0
          time.sleep(0.01)
          volume +=1
          if volume>100:
             volume=0
          subprocess.call('amixer cset numid=1 {}% > /dev/null'.format(volume) , shell=True)
          draw.rectangle((t_size_l_x*8+t_size_s_x*8, 0, t_size_l_x*9+t_size_s_x*10, t_size_s_y), (0,0,0))
          draw.text((t_size_l_x*8+t_size_s_x*8, 0),str(volume),  font=fontss, fill=(0, 255, 0))
          disp.display(img)
          longpush_(input_UP)
       if GPIO.input(input_DOWN) == 0:
          dialog_open=0
          time.sleep(0.01)
          volume -=1
          if volume<0:
             volume=100
          subprocess.call('amixer cset numid=1 {}% > /dev/null'.format(volume) , shell=True)
          draw.rectangle((t_size_l_x*8+t_size_s_x*8, 0, t_size_l_x*9+t_size_s_x*10, t_size_s_y), (0,0,0))
          draw.text((t_size_l_x*8+t_size_s_x*8, 0),str(volume),  font=fontss, fill=(0, 255, 0))
          disp.display(img)
          longpush_(input_DOWN)  

    if GPIO.input(input_OK) == 0 and GPIO.input(input_MODE) != 0: 
       time.sleep(0.01)        
       if mode==0:
          allnoteoff()
          while (GPIO.input(input_OK)) == 0: 
               mididisp()
               continue 
       if mode==1 and mode1_coordi ==0 and sf2used[sf2counter]==0 and sf2[0] != "sf2_None":  
          time.sleep(0.05)
          sf2used = [0]*len(sf2)
          sf2used[sf2counter]=1
          draw.rectangle((t_size_m_x*13, t_size_l_y+t_size_m_y+1, 160, t_size_l_y+t_size_m_y*2+2), (0,0,0))
          draw.rectangle((t_size_m_x*13, t_size_l_y+t_size_m_y*3+1, 160, t_size_l_y+t_size_m_y*4+2), (0,0,0))
          draw.text((9, t_size_l_y+t_size_m_y+1),"            Wait...", font=fontm, fill=(55, 255, 255))
          disp.display(img)
          subprocess.call('sudo killall timidity', shell=True)
          subprocess.call('sudo killall aplaymidi', shell=True)
          playflag = [0]*len(midi)
          subprocess.Popen('sudo timidity -c "/media/usb0/timidity_cfg/{}.cfg"' .format(sf2[sf2counter]), shell=True)
          time.sleep(2)
          subprocess.call('sh /home/pi/ysynth4/midiconnect.sh', shell=True)
          draw.rectangle((t_size_m_x*13, t_size_l_y+t_size_m_y+1, 160, t_size_l_y+t_size_m_y*2+2), (0,0,0))
          draw.text((9, t_size_l_y+t_size_m_y+1),"            OK!", font=fontm, fill=(55, 255, 255))
          disp.display(img)
          midiPROG=  [0]*16
          midiCC7=  [100]*16
          midiCC11=  [127]*16
          midiCC10=  [64]*16
          midiCC1=  [0]*16
          midiCC91=  [40]*16
          midiCC93=  [0]*16
          midiCC94=  [0]*16
          pb1 = [0]*16
          pb2 = [0x40]*16
          time.sleep(2)
          mode1_default_disp()

       if GPIO.input(input_OK) == 0 and  mode==1 and mode1_coordi ==1 : 
          if playflag[midicounter]==0 and midi[0] != "midi_None":
             time.sleep(0.05)
             playflag = [0]*len(midi)
             playflag[midicounter]=1
             draw.rectangle((t_size_m_x*13, t_size_l_y+t_size_m_y*3+1, 160, t_size_l_y+t_size_m_y*4+2), (0,0,0))
             draw.text((9, t_size_l_y+t_size_m_y*3+1),"            ▶", font=fontm, fill=(55, 255, 255))
             subprocess.call('sudo killall aplaymidi', shell=True)
             allnoteoff()
             aplaymidi = subprocess.Popen('aplaymidi -p 14:0 "/media/usb0/midi/{}.mid"' .format(midi[midicounter]), shell=True)
             disp.display(img)
             mode1_default_disp()
             while (GPIO.input(input_OK)) == 0: 
               mididisp()
               continue 

          if GPIO.input(input_OK) == 0 and playflag[midicounter]==1:
             time.sleep(0.05)
             playflag = [0]*len(midi)
             draw.rectangle((t_size_m_x*13, t_size_l_y+t_size_m_y*3+1, 160, t_size_l_y+t_size_m_y*4+2), (0,0,0))
             allnoteoff()
             subprocess.call('sudo killall aplaymidi', shell=True)
             allnoteoff()
             disp.display(img)
             mode1_default_disp()
             while (GPIO.input(input_OK)) == 0: 
               mididisp()
               continue 

       if mode==2 and mode2_coordi ==0:
          time.sleep(0.05)
          while (GPIO.input(input_OK)) == 0: 
               mididisp()
               continue 
          mode=3


       if mode==2 and mode2_coordi ==1:
          time.sleep(0.05)
          dialog_window0()
          if audio_card == str("IQaudIODAC"):
             draw.text((11, t_size_l_y+t_size_m_y*2+1)," bcm2835に切り替えます",  font=fontss, fill=(0, 0, 0))
             draw.text((11, t_size_l_y+t_size_m_y*3+1),"か?(再起動します)",  font=fontss, fill=(0, 0, 0))
             draw.text((dialog_coordi_xl[dialog_coordi], dialog_coordi_yl[dialog_coordi]),cur_size,  font=fontss, fill=(0, 0, 0))
             disp.display(img)
             dialog_loop0("    再起動します...", "")
             if dialog_coordi==0:
                subprocess.call("sudo sed -i -e '$ a dtparam=audio=on' /boot/config.txt" ,shell=True)
                subprocess.call("sudo sed -i -e '/dtoverlay=iqaudio-dacplus/d' /boot/config.txt" ,shell=True)
                subprocess.call("sudo sed -i -e '$ a opt B3,8' /etc/timidity/timidity.cfg" ,shell=True)
                subprocess.call("sudo sed -i -e '/opt B2,8/d' /etc/timidity/timidity.cfg" ,shell=True)
                subprocess.call("sudo reboot" ,shell=True)
                
          if audio_card == str("bcm2835"):          
             draw.text((11, t_size_l_y+t_size_m_y*2+1)," IQaudIODACに切り替えま",  font=fontss, fill=(0, 0, 0))
             draw.text((11, t_size_l_y+t_size_m_y*3+1),"すか?(再起動します)",  font=fontss, fill=(0, 0, 0))
             draw.text((dialog_coordi_xl[dialog_coordi], dialog_coordi_yl[dialog_coordi]),cur_size,  font=fontss, fill=(0, 0, 0))
             disp.display(img)
             dialog_loop0("    再起動します...", "")
             if dialog_coordi==0:
                subprocess.call("sudo sed -i -e '$ a dtoverlay=iqaudio-dacplus' /boot/config.txt" ,shell=True)
                subprocess.call("sudo sed -i -e '/dtparam=audio=on/d' /boot/config.txt" ,shell=True)
                subprocess.call("sudo sed -i -e '$ a opt B2,8' /etc/timidity/timidity.cfg" ,shell=True)
                subprocess.call("sudo sed -i -e '/opt B3,8/d' /etc/timidity/timidity.cfg" ,shell=True)
                subprocess.call("sudo reboot" ,shell=True)

       if mode==2 and mode2_coordi ==2:
          time.sleep(0.05)
          dialog_window0()
          if mountcheck != str("/media/usb0"):
             draw.text((11, t_size_l_y+t_size_m_y*2+1),"    認識させますか?",  font=fontss, fill=(0, 0, 0))
             draw.text((dialog_coordi_xl[dialog_coordi], dialog_coordi_yl[dialog_coordi]),cur_size,  font=fontss, fill=(0, 0, 0))
             disp.display(img)
             dialog_loop0("      認識します...", "sudo mount -t vfat -o ,iocharset=utf8 /dev/sda1 /media/usb0")
             if dialog_coordi==0:
                subprocess.call('rename.ul .MID .mid /media/usb0/midi/*' ,shell=True)
                subprocess.call('rename.ul .SF2 .sf2 /media/usb0/sf2/*' ,shell=True)
                subprocess.call('rename.ul .CFG .cfg /media/usb0/timidity_cfg/*' ,shell=True)
                midi = subprocess.check_output('find /media/usb0/midi/ -name \*.mid|sort' ,shell=True).decode('utf-8').strip().replace('/media/usb0/midi/', '').replace('.mid', '').replace('.MID', '').split('\n')
                playflag = [0]*len(midi)
                if midi[0]=='':
                   midi= ["midi_None"]
                   midicounter=0
                sf2 = subprocess.check_output('find /media/usb0/sf2/ -name \*.sf2|sort' ,shell=True).decode('utf-8').strip().replace('/media/usb0/sf2/', '').replace('.sf2', '').replace('.SF2', '').split('\n')
                sf2used = [0]*len(sf2)
                if sf2[0]=='':
                   sf2 = ["sf2_None"]
                   sf2counter = 0
                cfg = subprocess.check_output('find /media/usb0/timidity_cfg/ -name \*.cfg|sort' ,shell=True).decode('utf-8').strip().replace('/media/usb0/timidity_cfg/', '').replace('.cfg', '').split('\n')
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
                dialog_coordi=1
                mountcheck=subprocess.check_output("mount|grep -m1 /dev/sda|awk '{print $3}'" ,shell=True).decode('utf-8').strip()
                mode2_default_disp()

          if mountcheck == str("/media/usb0"):          
             draw.text((11, t_size_l_y+t_size_m_y*2+1),"    取り出しますか?",  font=fontss, fill=(0, 0, 0))
             draw.text((dialog_coordi_xl[dialog_coordi], dialog_coordi_yl[dialog_coordi]),cur_size,  font=fontss, fill=(0, 0, 0))
             disp.display(img)
             dialog_loop0("    取り出します...", "sudo umount /media/usb0/")
             if dialog_coordi==0:
              subprocess.call('sudo killall timidity', shell=True)
              subprocess.call('sudo killall aplaymidi', shell=True)
              midi= ["midi_None"]
              midicounter=0
              playflag = [0]
              sf2 = ["sf2_None"]
              sf2counter = 0
              sf2used = [0]
              cfg = [ ]
              dialog_coordi=1
              while mountcheck == str("/media/usb0"):  
                    mountcheck=subprocess.check_output("mount|grep -m1 /dev/sda|awk '{print $3}'" ,shell=True).decode('utf-8').strip()
              mode2_default_disp()

       if mode==2 and mode2_coordi ==3:
          time.sleep(0.05)
          dialog_window0()
          draw.text((11, t_size_l_y+t_size_m_y*2+1)," アップデートしますか?",  font=fontss, fill=(0, 0, 0))
          draw.text((dialog_coordi_xl[dialog_coordi], dialog_coordi_yl[dialog_coordi]),cur_size,  font=fontss, fill=(0, 0, 0))
          disp.display(img)
          dialog_loop0("    ダウンロード中...", "wget https://raw.githubusercontent.com/YoutechA320U/ysynth4/master/ysynth4.py -P /home/pi/ysynth4/")
          latest_dl =int(subprocess.check_output("test -f /home/pi/ysynth4/ysynth4.py.1;echo $?" ,shell=True).decode('utf-8').strip())
          if latest_dl == 1 and dialog_coordi==0:
             draw.rectangle((0, 0, 160, 128), (0,0,0)) 
             draw.text((3,60),"    ダウンロード失敗",  font=fontss, fill=(0, 255, 0))
             disp.display(img)
             dialog_coordi=1
             time.sleep(2)
             mode2_default_disp()
          if latest_dl ==0:
             download_v=float(subprocess.check_output("sudo cat /home/pi/ysynth4/ysynth4.py.1|grep -m1 version=|awk '{print $2;}'" , shell=True).decode('utf-8').strip().replace('\nysynth4/ysynth4.py.1|grep', ''))
             if download_v > version:
                draw.rectangle((0, 0, 160, 128), (0,0,0)) 
                draw.text((3,60),"  アップデートします...",  font=fontss, fill=(0, 255, 0))
                subprocess.call('sudo chown -R pi:pi /home/pi/' ,shell=True)
                subprocess.call("sudo mv -f /home/pi/ysynth4/ysynth4.py.1 /home/pi/ysynth4/ysynth4.py" , shell=True)
                disp.display(img)
                time.sleep(2)
                draw.rectangle((0, 0, 160, 128), (0,0,0)) 
                disp.display(img)
                subprocess.call('sudo systemctl restart ysynth4.service', shell=True)
             if download_v <= version:
                draw.rectangle((0, 0, 160, 128), (0,0,0)) 
                draw.text((3,60),"   最新のバージョンです",  font=fontss, fill=(0, 255, 0))
                subprocess.call("sudo rm /home/pi/ysynth4/ysynth4.py.1" , shell=True)
                disp.display(img)
                dialog_coordi=1
                time.sleep(2)
                mode2_default_disp()
       
       if mode==2 and mode2_coordi ==4:
          time.sleep(0.05)
          dialog_window0()
          draw.text((11, t_size_l_y+t_size_m_y*2+1),"     再起動しますか?",  font=fontss, fill=(0, 0, 0))
          draw.text((dialog_coordi_xl[dialog_coordi], dialog_coordi_yl[dialog_coordi]),cur_size,  font=fontss, fill=(0, 0, 0))
          disp.display(img)
          dialog_loop0("    再起動します...", "sudo reboot")

       if mode==2 and mode2_coordi ==5:
          time.sleep(0.05)
          dialog_window0()
          draw.text((11, t_size_l_y+t_size_m_y*2+1),"シャットダウンしますか?",  font=fontss, fill=(0, 0, 0))
          draw.text((dialog_coordi_xl[dialog_coordi], dialog_coordi_yl[dialog_coordi]),cur_size,  font=fontss, fill=(0, 0, 0))
          disp.display(img)
          dialog_loop0("  シャットダウンします...", "sudo shutdown -h now")

       if mode==2 and mode2_coordi ==6:
          time.sleep(0.05)
          dialog_window0()
          draw.text((11, t_size_l_y+t_size_m_y*2+1),"   リロードしますか?",  font=fontss, fill=(0, 0, 0))
          draw.text((dialog_coordi_xl[dialog_coordi], dialog_coordi_yl[dialog_coordi]),cur_size,  font=fontss, fill=(0, 0, 0))
          disp.display(img)
          dialog_loop0("    リロードします...", "sudo systemctl restart ysynth4.service")    
       if mode==3 and dialog_open !=1:
          mode3_default_disp()
          dialog_open=1
       if mode==3 and dialog_open ==1:
          if GPIO.input(input_OK) == 0 and wifi[0] !="見つかりませんでした":
             time.sleep(0.05)
             sc_key()   
              
    if (GPIO.input(input_LEFT) and GPIO.input(input_RIGHT) and GPIO.input(input_UP) and GPIO.input(input_DOWN) and GPIO.input(input_OK))== 1:  
       longpush=0 
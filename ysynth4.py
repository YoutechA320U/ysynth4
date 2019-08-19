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
    spi_speed_hz=48000000
)


# Initialize display.
disp.begin()

width = disp.width
height = disp.height


#img = Image.new('1', (160, height))
img = Image.new('RGB', (width, height), color=(0, 0, 0))

draw = ImageDraw.Draw(img)
#draw.rectangle((0,0,160, height), outline=0, fill=0)
draw.rectangle((0, 0, 160, 160), (0,0,0))

volume = 100
mode = 0
CC2 = 0
CC1 = 0

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

try:
  midi = subprocess.check_output('ls -v /media/usb0/midi/*.mid' ,shell=True).decode('utf-8').strip().replace('/media/usb0/midi/', '').replace('.mid', '').split('\n')
  playflag = [0]*len(midi)
except:
 midi= ["midi_None"]
 midicounter=0
try:
 sf2 = subprocess.check_output('ls -v /media/usb0/sf2/*.sf2' ,shell=True).decode('utf-8').strip().replace('/media/usb0/sf2/', '').replace('.sf2', '').split('\n')
 sf2used = [0]*len(sf2)
except:
 sf2 = ["sf2_None"]
 sf2counter = 0
try:
 cfg = subprocess.check_output('ls -v /media/usb0/timidity_cfg/*.cfg' ,shell=True).decode('utf-8').strip().replace('/media/usb0/timidity_cfg/', '').replace('.cfg', '').split('\n')
except:
 cfg = [ ]
if (sf2 != cfg) and (sf2[0] != "sf2_None"):
 list_difference = list(set(cfg) - set(sf2))
 list_difference = [l.replace(' ', '\ ') for l in list_difference]
 for x in range(len(list_difference)):
  subprocess.call('sudo rm /media/usb0/timidity_cfg/{}.cfg' .format(list_difference[x])  ,shell=True)
 list_difference = list(set(sf2) - set(cfg))
 list_difference = [l.replace(' ', '\ ') for l in list_difference]
 for x in range(len(list_difference)):
  subprocess.call("sudo /home/pi/ysynth4/cfgforsf -C /media/usb0/sf2/{sf2name}.sf2 | sed -e 's/(null)//' -e 's/^[ ]*//g' -e '/(null)#/d'  -e /^#/d | grep -C 1 % | sed -e '/--/d' -e /^$/d > /media/usb0/timidity_cfg/{sf2name}.cfg" .format(sf2name=list_difference[x])  ,shell=True)
  print(list_difference[x])
 subprocess.call('sudo chown -R pi:pi /media/usb0/timidity_cfg' ,shell=True)
if sf2[0] == "sf2_None":
   subprocess.call('sudo rm /home/pi/timidity_cfg/*.cfg' ,shell=True)


subprocess.call('sudo killall ttymidi', shell=True)
subprocess.call('sudo killall timidity', shell=True)
subprocess.Popen('sudo /home/pi/ttymidi -s /dev/ttyAMA0 -b 38400', shell=True)
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

fonts = ImageFont.truetype('/usr/share/fonts/truetype/takao-gothic/TakaoGothic.ttf', 12, encoding='unic')
fontm = ImageFont.truetype('/usr/share/fonts/truetype/takao-gothic/TakaoGothic.ttf', 14, encoding='unic')
fontl = ImageFont.truetype('/usr/share/fonts/truetype/takao-gothic/TakaoGothic.ttf', 20, encoding='unic')

x = 3
y = 0
m_size="A" #1文字分
cur_size="▶"

t_size_s_x, t_size_s_y  = draw.textsize(m_size, fonts)
t_size_m_x, t_size_m_y  = draw.textsize(m_size, fontm)
t_size_l_x, t_size_l_y  = draw.textsize(m_size, fontl)
cur_size_x, cur_size_y  = draw.textsize(m_size, fonts)

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


def mode0_default_disp():
   draw.rectangle((0, 0, 160, 128), (0,0,0))
   draw.text((mode0_coordi_xl[mode0_coordi], mode0_coordi_yl[mode0_coordi]),cur_size,  font=fonts, fill=(255, 255, 255))
   draw.text((cur_size_x+x, 0),"CH:",  font=fontl, fill=(55, 255, 255))
   draw.text((cur_size_x+x, t_size_l_y+t_size_m_y+1),"PC :", font=fontm, fill=(55, 255, 255))
   draw.text((cur_size_x+x, t_size_l_y+t_size_m_y*2+1),"VOL:",  font=fontm, fill=(55, 255, 255))
   draw.text((cur_size_x+x, t_size_l_y+t_size_m_y*3+1),"EXP:",  font=fontm, fill=(55, 255, 255))
   draw.text((cur_size_x+x, t_size_l_y+t_size_m_y*4+1),"PAN:",  font=fontm, fill=(55, 255, 255))
   draw.text((cur_size_x+x, t_size_l_y+t_size_m_y*5+1),"MOD:",  font=fontm, fill=(55, 255, 255))
   draw.text((cur_size_x+x, t_size_l_y+t_size_m_y*6+1),"REV:", font=fontm, fill=(55, 255, 255))
   draw.text((cur_size_x+x, t_size_l_y+t_size_m_y*7+1),"CHO:",  font=fontm, fill=(55, 255, 255))
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
   draw.text((t_size_l_x*8, 0),"SysVol: "+str(volume),  font=fonts, fill=(0, 255, 0))
   disp.display(img)

def mode1_default_disp():
   draw.rectangle((0, 0, 160, 128), (0,0,0))
   draw.text((mode1_coordi_xl[mode1_coordi], mode1_coordi_yl[mode1_coordi]),cur_size,  font=fonts, fill=(255, 255, 255))
   draw.text((cur_size_x+x, 0),"SMF",  font=fontl, fill=(255, 255, 55))
   draw.text((cur_size_x+x, t_size_l_y+t_size_m_y+1),"SF2:" +"{0:03d}".format(sf2counter + 1), font=fontm, fill=(55, 255, 255))
   draw.text((cur_size_x+x, t_size_l_y+t_size_m_y*3+1),"SMF:"+"{0:03d}".format(midicounter + 1), font=fontm, fill=(55, 255, 255))
   draw.text((cur_size_x+x, t_size_l_y+t_size_m_y*2+1),sf2[sf2counter], font=fontm, fill=(255, 255, 55))
   if sf2used[sf2counter]==1:
      draw.text((cur_size_x+x, t_size_l_y+t_size_m_y+1),"        ♪", font=fontm, fill=(55, 255, 255))
   if playflag[midicounter]==1:
      draw.text((cur_size_x+x, t_size_l_y+t_size_m_y*3+1),"        ▶", font=fontm, fill=(55, 255, 255))
   draw.text((cur_size_x+x, t_size_l_y+t_size_m_y*4+1),midi[midicounter],  font=fontm, fill=(255, 255, 55))
   draw.text((t_size_l_x*8, 0),"SysVol: "+str(volume),  font=fonts, fill=(0, 255, 0))
   disp.display(img)

def mode2_default_disp():
   draw.rectangle((0, 0, 160, 128), (0,0,0))
   draw.text((mode2_coordi_xl[mode2_coordi], mode2_coordi_yl[mode2_coordi]),cur_size,  font=fonts, fill=(255, 255, 255))
   draw.text((cur_size_x+x, 0),"設定",  font=fontl, fill=(255, 255, 55))
   draw.text((cur_size_x+x, t_size_l_y+t_size_m_y+1),"WiFi:",  font=fontm, fill=(55, 255, 255))
   draw.text((cur_size_x+x, t_size_l_y+t_size_m_y*2+1),"Audio:",  font=fontm, fill=(55, 255, 255))
   draw.text((cur_size_x+x, t_size_l_y+t_size_m_y*3+1),"USBメモリ",  font=fontm, fill=(55, 255, 255))
   draw.text((cur_size_x+x, t_size_l_y+t_size_m_y*4+1),"Ysynth4アップデート",  font=fontm, fill=(55, 255, 255))
   draw.text((cur_size_x+x, t_size_l_y+t_size_m_y*5+1),"再起動", font=fontm, fill=(55, 255, 255))
   draw.text((cur_size_x+x, t_size_l_y+t_size_m_y*6+1),"シャットダウン",  font=fontm, fill=(55, 255, 255))
   draw.text((cur_size_x+x, t_size_l_y+t_size_m_y*7+1),"リロード",  font=fontm, fill=(55, 255, 255))
   draw.text((t_size_m_x*6, t_size_l_y+t_size_m_y+1),wifi_ssid,  font=fontm, fill=(255, 255, 55))
   draw.text((t_size_m_x*7, t_size_l_y+t_size_m_y*2+1),audio_card,  font=fontm, fill=(255, 255, 55))
   draw.text((t_size_l_x*8, 0),"SysVol: "+str(volume),  font=fonts, fill=(0, 255, 0))
   disp.display(img)

def dialog_window0():
   draw.rectangle((10, t_size_l_y+t_size_m_y+1, 150, 110),outline=(255,255,255), fill=(217,207,201))
   draw.rectangle((10, t_size_l_y+t_size_m_y+1, 150, 20),outline=(217,207,201), fill=(8,34,109))
   draw.rectangle((20, 90, 70, 90+t_size_s_y),outline=(100,100,100), fill=(217,207,201))
   draw.rectangle((90, 90, 140, 90+t_size_s_y),outline=(100,100,100), fill=(217,207,201))
   draw.text((34,90),"はい",  font=fonts, fill=(0, 0, 0))
   draw.text((98,90),"いいえ",  font=fonts, fill=(0, 0, 0))
   disp.display(img)

def dialog_loop0(txt, cmd):
    global dialog_coordi, dialog_coordi_xl, dialog_coordi_yl, dialog_open
    while (GPIO.input(input_OK)) == 0: 
          continue 
    while dialog_open==1:
       time.sleep(0.00001)   
       if GPIO.input(input_RIGHT) == 0 :
          time.sleep(0.01)
          draw.rectangle((dialog_coordi_xl[dialog_coordi], dialog_coordi_yl[dialog_coordi],dialog_coordi_xl[dialog_coordi]+cur_size_x, dialog_coordi_yl[dialog_coordi]+cur_size_y),(217,207,201))
          dialog_coordi +=1
          if dialog_coordi >1:
             dialog_coordi=0
          draw.text((dialog_coordi_xl[dialog_coordi], dialog_coordi_yl[dialog_coordi]),cur_size,  font=fonts, fill=(0, 0, 0))
          disp.display(img)
          while (GPIO.input(input_LEFT) == 0 and longpush !=100) or (GPIO.input(input_RIGHT) == 0 and longpush !=100): 
                time.sleep(0.01)
                longpush +=1
                if longpush==100:
                   break
                else:
                   continue
       if GPIO.input(input_LEFT) == 0 :
          time.sleep(0.01)
          draw.rectangle((dialog_coordi_xl[dialog_coordi], dialog_coordi_yl[dialog_coordi],dialog_coordi_xl[dialog_coordi]+cur_size_x, dialog_coordi_yl[dialog_coordi]+cur_size_y),(217,207,201))
          dialog_coordi -=1
          if dialog_coordi <0:
             dialog_coordi=1
          draw.text((dialog_coordi_xl[dialog_coordi], dialog_coordi_yl[dialog_coordi]),cur_size,  font=fonts, fill=(0, 0, 0))   
          disp.display(img)
          while (GPIO.input(input_LEFT) == 0 and longpush !=100): 
                time.sleep(0.01)
                longpush +=1
                if longpush==100:
                   break
                else:
                   continue
       if GPIO.input(input_OK) == 0:
          time.sleep(0.05)
          if dialog_coordi==0:
             subprocess.Popen(cmd ,shell=True)
             draw.rectangle((0, 0, 160, 128), (0,0,0)) 
             draw.text((3,60),txt,  font=fonts, fill=(0, 255, 0))
             disp.display(img)
             time.sleep(3)
             draw.rectangle((0, 0, 160, 128), (0,0,0)) 
             time.sleep(1)
             dialog_open=0
          if dialog_coordi==1:
             while (GPIO.input(input_OK)) == 0: 
                   continue 
             dialog_open=0 
             mode2_default_disp()
       if (GPIO.input(input_LEFT) and GPIO.input(input_RIGHT))== 1:  
          longpush=0 
##初期設定ここまで##

msg = None
#subprocess.Popen('sudo timidity -c /media/usb0/timidity_cfg/{}.cfg' .format(sf2[sf2counter]), shell=True)
#time.sleep(2)
#subprocess.call('sh /home/pi/ysynth4/midiconnect.sh', shell=True)

mode0_default_disp()

while True:
    try:
     if aplaymidi.poll() is not None:
        if mode == 1 and playflag[midicounter] == 1:
           draw.rectangle((t_size_m_x*9, t_size_l_y+t_size_m_y*3+1, 160, t_size_l_y+t_size_m_y*4+2), (0,0,0))
           disp.display(img)
        playflag = [0]*len(midi)
    except:
     pass

    msg = midiin.get_message()
    #print(msg)
    if msg is None:
       message, deltatime = 0,0
    #print(message)
##MIDI入力をディスプレイに反映する処理
    if msg is not None:
       message, deltatime = msg
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
        continue
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

    if GPIO.input(input_LEFT) == 0: 
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
             draw.rectangle((cur_size_x+x, t_size_l_y+t_size_m_y*2+1, 160, t_size_l_y+t_size_m_y*3+2), (0,0,0))
             draw.text((cur_size_x+x+t_size_m_x*4, t_size_l_y+t_size_m_y+1),"{0:03d}".format(sf2counter + 1), font=fontm, fill=(55, 255, 255))
             draw.text((cur_size_x+x, t_size_l_y+t_size_m_y*2+1),sf2[sf2counter], font=fontm, fill=(255, 255, 55))
             if sf2used[sf2counter]==1:
                 draw.text((cur_size_x+x, t_size_l_y+t_size_m_y+1),"        ♪", font=fontm, fill=(55, 255, 255))
             if playflag[midicounter]==1:
                draw.text((cur_size_x+x, t_size_l_y+t_size_m_y*3+1),"        ▶", font=fontm, fill=(55, 255, 255))
             disp.display(img)
          if mode1_coordi ==1:
             midicounter -= 1
             if midicounter == -1:
                midicounter =  len(midi)-1
             draw.rectangle((t_size_m_x*5, t_size_l_y+t_size_m_y*3+1, 160, t_size_l_y+t_size_m_y*4+2), (0,0,0))
             draw.rectangle((cur_size_x+x, t_size_l_y+t_size_m_y*4+1, 160, t_size_l_y+t_size_m_y*5+2), (0,0,0))
             draw.text((cur_size_x+x+t_size_m_x*4, t_size_l_y+t_size_m_y*3+1),"{0:03d}".format(midicounter + 1),  font=fontm, fill=(55, 255, 255))
             draw.text((cur_size_x+x, t_size_l_y+t_size_m_y*4+1),midi[midicounter],  font=fontm, fill=(255, 255, 55))
             if sf2used[sf2counter]==1:
                draw.text((cur_size_x+x, t_size_l_y+t_size_m_y+1),"        ♪", font=fontm, fill=(55, 255, 255))
             if playflag[midicounter]==1:
                draw.text((cur_size_x+x, t_size_l_y+t_size_m_y*3+1),"        ▶", font=fontm, fill=(55, 255, 255))
             disp.display(img)


       while (GPIO.input(input_LEFT) == 0 and longpush !=100): 
             time.sleep(0.01)
             longpush +=1
             if longpush==100:
                break
             else:
                continue
    if GPIO.input(input_RIGHT) == 0: 
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
             if pb1[midiCH] != 0x7f:
                pb1[midiCH] += 1
             if pb1[midiCH] == 0x7f:
                #pb1[midiCH] = 0
                pb2[midiCH] += 1
                if pb2[midiCH] > 0x7f:
                   pb1[midiCH] = 0
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
             draw.rectangle((cur_size_x+x, t_size_l_y+t_size_m_y*2+1, 160, t_size_l_y+t_size_m_y*3+2), (0,0,0))
             draw.text((cur_size_x+x+t_size_m_x*4, t_size_l_y+t_size_m_y+1),"{0:03d}".format(sf2counter + 1), font=fontm, fill=(55, 255, 255))
             draw.text((cur_size_x+x, t_size_l_y+t_size_m_y*2+1),sf2[sf2counter], font=fontm, fill=(255, 255, 55))
             if sf2used[sf2counter]==1:
                draw.text((cur_size_x+x, t_size_l_y+t_size_m_y+1),"        ♪", font=fontm, fill=(55, 255, 255))
             if playflag[midicounter]==1:
                draw.text((cur_size_x+x, t_size_l_y+t_size_m_y*3+1),"        ▶", font=fontm, fill=(55, 255, 255))
             disp.display(img)
          if mode1_coordi ==1:
             midicounter += 1
             if midicounter == len(midi):
                midicounter = 0
             draw.rectangle((t_size_m_x*5, t_size_l_y+t_size_m_y*3+1, 160, t_size_l_y+t_size_m_y*4+2), (0,0,0))
             draw.rectangle((cur_size_x+x, t_size_l_y+t_size_m_y*4+1, 160, t_size_l_y+t_size_m_y*5+2), (0,0,0))
             draw.text((cur_size_x+x+t_size_m_x*4, t_size_l_y+t_size_m_y*3+1),"{0:03d}".format(midicounter + 1),  font=fontm, fill=(55, 255, 255))
             draw.text((cur_size_x+x, t_size_l_y+t_size_m_y*4+1),midi[midicounter],  font=fontm, fill=(255, 255, 55))  
             if sf2used[sf2counter]==1:
                draw.text((cur_size_x+x, t_size_l_y+t_size_m_y+1),"        ♪", font=fontm, fill=(55, 255, 255))  
             if playflag[midicounter]==1:
                draw.text((cur_size_x+x, t_size_l_y+t_size_m_y*3+1),"        ▶", font=fontm, fill=(55, 255, 255))
             disp.display(img) 

       while (GPIO.input(input_RIGHT) == 0 and longpush !=100): 
             time.sleep(0.01)
             longpush +=1
             if longpush==100:
                break
             else:
                continue
    if GPIO.input(input_UP) == 0: 
       time.sleep(0.01)
       if mode==0 and GPIO.input(input_OK) != 0:
          draw.rectangle((mode0_coordi_xl[mode0_coordi], mode0_coordi_yl[mode0_coordi],mode0_coordi_xl[mode0_coordi]+cur_size_x, mode0_coordi_yl[mode0_coordi]+cur_size_y), (0,0,0))
          mode0_coordi -=1
          if mode0_coordi <0:
             mode0_coordi=9
          draw.text((mode0_coordi_xl[mode0_coordi], mode0_coordi_yl[mode0_coordi]),cur_size,  font=fonts, fill=(255, 255, 255))   
          disp.display(img) 
       if mode==1 and GPIO.input(input_OK) != 0:
          draw.rectangle((mode1_coordi_xl[mode1_coordi], mode1_coordi_yl[mode1_coordi],mode1_coordi_xl[mode1_coordi]+cur_size_x, mode1_coordi_yl[mode1_coordi]+cur_size_y), (0,0,0))
          mode1_coordi -=1
          if mode1_coordi <0:
             mode1_coordi=1
          draw.text((mode1_coordi_xl[mode1_coordi], mode1_coordi_yl[mode1_coordi]),cur_size,  font=fonts, fill=(255, 255, 255)) 
          disp.display(img)  
       if mode==2 and GPIO.input(input_OK) != 0:
          draw.rectangle((mode2_coordi_xl[mode2_coordi], mode2_coordi_yl[mode2_coordi],mode2_coordi_xl[mode2_coordi]+cur_size_x, mode2_coordi_yl[mode2_coordi]+cur_size_y), (0,0,0))
          mode2_coordi -=1
          if mode2_coordi <0:
             mode2_coordi=6
          draw.text((mode2_coordi_xl[mode2_coordi], mode2_coordi_yl[mode2_coordi]),cur_size,  font=fonts, fill=(255, 255, 255))  
          disp.display(img) 
       while (GPIO.input(input_UP) == 0 and longpush !=100): 
             time.sleep(0.01)
             longpush +=1
             if longpush==100:
                break
             else:
               continue   

    if GPIO.input(input_DOWN) == 0: 
       time.sleep(0.01)
       if mode==0 and GPIO.input(input_OK) != 0:
          draw.rectangle((mode0_coordi_xl[mode0_coordi], mode0_coordi_yl[mode0_coordi],mode0_coordi_xl[mode0_coordi]+cur_size_x, mode0_coordi_yl[mode0_coordi]+cur_size_y), (0,0,0))
          mode0_coordi +=1
          if mode0_coordi >9:
             mode0_coordi=0
          draw.text((mode0_coordi_xl[mode0_coordi], mode0_coordi_yl[mode0_coordi]),cur_size,  font=fonts, fill=(255, 255, 255)) 
          disp.display(img)
       if mode==1 and GPIO.input(input_OK) != 0:
          draw.rectangle((mode1_coordi_xl[mode1_coordi], mode1_coordi_yl[mode1_coordi],mode1_coordi_xl[mode1_coordi]+cur_size_x, mode1_coordi_yl[mode1_coordi]+cur_size_y), (0,0,0))
          mode1_coordi +=1
          if mode1_coordi >1:
             mode1_coordi=0
          draw.text((mode1_coordi_xl[mode1_coordi], mode1_coordi_yl[mode1_coordi]),cur_size,  font=fonts, fill=(255, 255, 255)) 
          disp.display(img)  
       if mode==2 and GPIO.input(input_OK) != 0:
          draw.rectangle((mode2_coordi_xl[mode2_coordi], mode2_coordi_yl[mode2_coordi],mode2_coordi_xl[mode2_coordi]+cur_size_x, mode2_coordi_yl[mode2_coordi]+cur_size_y), (0,0,0))
          mode2_coordi +=1
          if mode2_coordi >6:
             mode2_coordi=0
          draw.text((mode2_coordi_xl[mode2_coordi], mode2_coordi_yl[mode2_coordi]),cur_size,  font=fonts, fill=(255, 255, 255))  
          disp.display(img) 
       while (GPIO.input(input_DOWN) == 0 and longpush !=100): 
             time.sleep(0.01)
             longpush +=1
             if longpush==100:
                break
             else:
               continue
    if GPIO.input(input_MODE) == 0:  
       time.sleep(0.1)
       mode +=1
       if mode>2:
          mode=0
          wifi_ssid=str(subprocess.check_output('''iwconfig wlan0 | grep ESSID | sed -e 's/wlan0//g' -e 's/IEEE 802.11//g' -e 's/ESSID://g' -e 's/"//g' -e 's/^[ ]*//g' ''' ,shell=True).decode('utf-8').strip())
          if wifi_ssid=="off/any":
             wifi_ssid="接続していません" 
          mode0_default_disp()
       if mode==1:
          mode1_default_disp()
          if sf2used[sf2counter]==1:
             draw.text((cur_size_x+x, t_size_l_y+t_size_m_y+1),"        ♪", font=fontm, fill=(55, 255, 255))
             disp.display(img)
          if playflag[midicounter]==1:
             draw.text((cur_size_x+x, t_size_l_y+t_size_m_y*3+1),"        ▶", font=fontm, fill=(55, 255, 255))
             disp.display(img)
       if mode==2:      
          mode2_default_disp()
       while (GPIO.input(input_MODE)) == 0: 
          continue 

    if GPIO.input(input_OK) == 0: 
       time.sleep(0.01)        
       if mode==1 and mode1_coordi ==0 and sf2used[sf2counter]==0 and sf2[0] != "sf2_None":  
          time.sleep(0.05)
          sf2used = [0]*len(sf2)
          sf2used[sf2counter]=1
          draw.rectangle((t_size_m_x*9, t_size_l_y+t_size_m_y+1, 160, t_size_l_y+t_size_m_y*2+2), (0,0,0))
          draw.rectangle((t_size_m_x*9, t_size_l_y+t_size_m_y*3+1, 160, t_size_l_y+t_size_m_y*4+2), (0,0,0))
          draw.text((cur_size_x+x, t_size_l_y+t_size_m_y+1),"        Wait...", font=fontm, fill=(55, 255, 255))
          disp.display(img)
          subprocess.call('sudo killall timidity', shell=True)
          subprocess.call('sudo killall aplaymidi', shell=True)
          playflag = [0]*len(midi)
          sf2 = [s.replace(' ', '\ ') for s in sf2]
          subprocess.Popen('sudo timidity -c /media/usb0/timidity_cfg/{}.cfg' .format(sf2[sf2counter]), shell=True)
          sf2 = [s.replace('\ ', ' ') for s in sf2]
          time.sleep(2)
          subprocess.call('sh /home/pi/ysynth4/midiconnect.sh', shell=True)
          draw.rectangle((t_size_m_x*9, t_size_l_y+t_size_m_y+1, 160, t_size_l_y+t_size_m_y*2+2), (0,0,0))
          draw.text((cur_size_x+x, t_size_l_y+t_size_m_y+1),"        OK!", font=fontm, fill=(55, 255, 255))
          disp.display(img)
          time.sleep(2)
          mode1_default_disp()

       if GPIO.input(input_OK) == 0 and  mode==1 and mode1_coordi ==1 : 
          if playflag[midicounter]==0 and midi[0] != "midi_None":
             time.sleep(0.05)
             playflag = [0]*len(midi)
             playflag[midicounter]=1
             draw.rectangle((t_size_m_x*9, t_size_l_y+t_size_m_y*3+1, 160, t_size_l_y+t_size_m_y*4+2), (0,0,0))
             draw.text((cur_size_x+x, t_size_l_y+t_size_m_y*3+1),"        ▶", font=fontm, fill=(55, 255, 255))
             subprocess.call('sudo killall aplaymidi', shell=True)
             allnoteoff()
             midi = [s.replace(' ', '\ ') for s in midi]
             aplaymidi = subprocess.Popen('aplaymidi -p 14:0 /media/usb0/midi/{}.mid' .format(midi[midicounter]), shell=True)
             midi = [s.replace('\ ', ' ') for s in midi]
             disp.display(img)
             mode1_default_disp()
             while (GPIO.input(input_OK)) == 0: 
               continue 

          if GPIO.input(input_OK) == 0 and playflag[midicounter]==1:
             time.sleep(0.05)
             playflag = [0]*len(midi)
             draw.rectangle((t_size_m_x*9, t_size_l_y+t_size_m_y*3+1, 160, t_size_l_y+t_size_m_y*4+2), (0,0,0))
             allnoteoff()
             subprocess.call('sudo killall aplaymidi', shell=True)
             allnoteoff()
             disp.display(img)
             mode1_default_disp()
             while (GPIO.input(input_OK)) == 0: 
               continue 

       if mode==2 and mode2_coordi ==0:
          time.sleep(0.05)
          dialog_open=1
          dialog_window0()
          if wifi_ssid =="接続していません":
             draw.text((11, t_size_l_y+t_size_m_y*2+1)," WiFiに接続しますか?",  font=fonts, fill=(0, 0, 0))
             draw.text((dialog_coordi_xl[dialog_coordi], dialog_coordi_yl[dialog_coordi]),cur_size,  font=fonts, fill=(0, 0, 0))
             disp.display(img)
             dialog_loop0("  オンにします...", "sudo ifup wlan0")
             if dialog_coordi==0:
                wifi_ssid=str(subprocess.check_output('''iwconfig wlan0 | grep ESSID | sed -e 's/wlan0//g' -e 's/IEEE 802.11//g' -e 's/ESSID://g' -e 's/"//g' -e 's/^[ ]*//g' ''' ,shell=True).decode('utf-8').strip())
                dialog_coordi=1
                if wifi_ssid=="off/any":
                   wifi_ssid="接続していません" 
                mode2_default_disp()

          if wifi_ssid !="接続していません":          
             draw.text((11, t_size_l_y+t_size_m_y*2+1)," WiFiを切断しますか?",  font=fonts, fill=(0, 0, 0))
             draw.text((dialog_coordi_xl[dialog_coordi], dialog_coordi_yl[dialog_coordi]),cur_size,  font=fonts, fill=(0, 0, 0))
             disp.display(img)
             dialog_loop0("  オフにします...", "sudo ifdown wlan0")
             if dialog_coordi==0:
                wifi_ssid ="接続していません"
                dialog_coordi=1
                mode2_default_disp()

       if mode==2 and mode2_coordi ==1:
          time.sleep(0.05)
          dialog_open=1
          dialog_window0()
          if audio_card == str("IQaudIODAC"):
             draw.text((11, t_size_l_y+t_size_m_y*2+1)," bcm2835に切り替えます",  font=fonts, fill=(0, 0, 0))
             draw.text((11, t_size_l_y+t_size_m_y*3+1),"か?(再起動します)",  font=fonts, fill=(0, 0, 0))
             draw.text((dialog_coordi_xl[dialog_coordi], dialog_coordi_yl[dialog_coordi]),cur_size,  font=fonts, fill=(0, 0, 0))
             disp.display(img)
             dialog_loop0("  再起動します...", "")
             if dialog_coordi==0:
                subprocess.call("sudo sed -i -e '$ a dtparam=audio=on' /boot/config.txt" ,shell=True)
                subprocess.call("sudo sed -i -e '/dtoverlay=iqaudio-dacplus/d' /boot/config.txt" ,shell=True)
                subprocess.call("sudo reboot" ,shell=True)

             draw.rectangle((0, 0, 160, 128), (0,0,0)) 
          if audio_card == str("bcm2835"):          
             draw.text((11, t_size_l_y+t_size_m_y*2+1)," IQaudIODACに切り替えま",  font=fonts, fill=(0, 0, 0))
             draw.text((11, t_size_l_y+t_size_m_y*3+1),"すか?(再起動します)",  font=fonts, fill=(0, 0, 0))
             draw.text((dialog_coordi_xl[dialog_coordi], dialog_coordi_yl[dialog_coordi]),cur_size,  font=fonts, fill=(0, 0, 0))
             disp.display(img)
             dialog_loop0("  再起動します...", "")
             if dialog_coordi==0:
                subprocess.call("sudo sed -i -e '$ a dtoverlay=iqaudio-dacplus' /boot/config.txt" ,shell=True)
                subprocess.call("sudo sed -i -e '/dtparam=audio=on/d' /boot/config.txt" ,shell=True)
                subprocess.call("sudo reboot" ,shell=True)

       if mode==2 and mode2_coordi ==2:
          time.sleep(0.05)
          dialog_open=1
          dialog_window0()
          if mountcheck != str("/media/usb0"):
             draw.text((11, t_size_l_y+t_size_m_y*2+1),"    認識させますか?",  font=fonts, fill=(0, 0, 0))
             draw.text((dialog_coordi_xl[dialog_coordi], dialog_coordi_yl[dialog_coordi]),cur_size,  font=fonts, fill=(0, 0, 0))
             disp.display(img)
             dialog_loop0("      認識します...", "sudo mount -t vfat -o ,iocharset=utf8 /dev/sda1 /media/usb0")
             if dialog_coordi==0:
              try:
               midi = subprocess.check_output('ls -v /media/usb0/midi/*.mid' ,shell=True).decode('utf-8').strip().replace('/media/usb0/midi/', '').replace('.mid', '').split('\n')
               playflag = [0]*len(midi)
              except:
               midi= ["midi_None"]
               midicounter=0
              try:
               sf2 = subprocess.check_output('ls -v /media/usb0/sf2/*.sf2' ,shell=True).decode('utf-8').strip().replace('/media/usb0/sf2/', '').replace('.sf2', '').split('\n')
               sf2used = [0]*len(sf2)
              except:
               sf2 = ["sf2_None"]
               sf2counter = 0
              try:
               cfg = subprocess.check_output('ls -v /media/usb0/timidity_cfg/*.cfg' ,shell=True).decode('utf-8').strip().replace('/media/usb0/timidity_cfg/', '').replace('.cfg', '').split('\n')
              except:
               cfg = [ ]
              if (sf2 != cfg) and (sf2[0] != "sf2_None"):
               list_difference = list(set(cfg) - set(sf2))
               list_difference = [l.replace(' ', '\ ') for l in list_difference]
               for x in range(len(list_difference)):
                subprocess.call('sudo rm /media/usb0/timidity_cfg/{}.cfg' .format(list_difference[x])  ,shell=True)
               list_difference = list(set(sf2) - set(cfg))
               list_difference = [l.replace(' ', '\ ') for l in list_difference]
               for x in range(len(list_difference)):
                subprocess.call("sudo /home/pi/ysynth4/cfgforsf -C /media/usb0/sf2/{sf2name}.sf2 | sed -e 's/(null)//' -e 's/^[ ]*//g' -e '/(null)#/d'  -e /^#/d | grep -C 1 % | sed -e '/--/d' -e /^$/d > /media/usb0/timidity_cfg/{sf2name}.cfg" .format(sf2name=list_difference[x])  ,shell=True)
                subprocess.call('sudo chown -R pi:pi /media/usb0/timidity_cfg' ,shell=True)
              if sf2[0] == "sf2_None":
                 subprocess.call('sudo rm /home/pi/timidity_cfg/*.cfg' ,shell=True)
              subprocess.Popen('sudo timidity -c /media/usb0/timidity_cfg/{}.cfg' .format(sf2[sf2counter]), shell=True)
              time.sleep(2)
              dialog_coordi=1
              subprocess.call('sh /home/pi/ysynth4/midiconnect.sh', shell=True)
              mountcheck=subprocess.check_output("mount|grep -m1 /dev/sda|awk '{print $3}'" ,shell=True).decode('utf-8').strip()
              mode2_default_disp()

          if mountcheck == str("/media/usb0"):          
             draw.text((11, t_size_l_y+t_size_m_y*2+1),"    取り出しますか?",  font=fonts, fill=(0, 0, 0))
             draw.text((dialog_coordi_xl[dialog_coordi], dialog_coordi_yl[dialog_coordi]),cur_size,  font=fonts, fill=(0, 0, 0))
             disp.display(img)
             dialog_loop0("    取り出します...", "sudo umount /media/usb0/")
             subprocess.call('sudo killall timidity', shell=True)
             subprocess.call('sudo killall aplaymidi', shell=True)
             if dialog_coordi==0:
              try:
               midi = subprocess.check_output('ls -v /media/usb0/midi/*.mid' ,shell=True).decode('utf-8').strip().replace('/media/usb0/midi/', '').replace('.mid', '').split('\n')
               playflag = [0]*len(midi)
              except:
               midi= ["midi_None"]
               midicounter=0
              try:
               sf2 = subprocess.check_output('ls -v /media/usb0/sf2/*.sf2' ,shell=True).decode('utf-8').strip().replace('/media/usb0/sf2/', '').replace('.sf2', '').split('\n')
               sf2used = [0]*len(sf2)
              except:
               sf2 = ["sf2_None"]
               sf2counter = 0
              try:
               cfg = subprocess.check_output('ls -v /media/usb0/timidity_cfg/*.cfg' ,shell=True).decode('utf-8').strip().replace('/media/usb0/timidity_cfg/', '').replace('.cfg', '').split('\n')
              except:
               cfg = [ ]
              dialog_coordi=1
              time.sleep(2)
              mountcheck=subprocess.check_output("mount|grep -m1 /dev/sda|awk '{print $3}'" ,shell=True).decode('utf-8').strip()
              mode2_default_disp()


       if mode==2 and mode2_coordi ==3:
          time.sleep(0.05)
          dialog_open=1
          dialog_window0()
          draw.text((11, t_size_l_y+t_size_m_y*2+1)," アップデートしますか?",  font=fonts, fill=(0, 0, 0))
          draw.text((dialog_coordi_xl[dialog_coordi], dialog_coordi_yl[dialog_coordi]),cur_size,  font=fonts, fill=(0, 0, 0))
          disp.display(img)
          dialog_loop0("    ダウンロード中...", "wget https://raw.githubusercontent.com/YoutechA320U/ysynth4/master/ysynth4.py -P /home/pi/ysynth4/")
          latest_dl =int(subprocess.check_output("test -f /home/pi/ysynth4/ysynth4.py.1;echo $?" ,shell=True).decode('utf-8').strip())
          if latest_dl == 1 and dialog_coordi==0:
             draw.rectangle((0, 0, 160, 128), (0,0,0)) 
             draw.text((3,60),"    ダウンロード失敗",  font=fonts, fill=(0, 255, 0))
             disp.display(img)
             dialog_coordi=1
             time.sleep(2)
             mode2_default_disp()
          if latest_dl ==0:
             draw.rectangle((0, 0, 160, 128), (0,0,0)) 
             draw.text((3,60),"  アップデートします...",  font=fonts, fill=(0, 255, 0))
             subprocess.call('sudo chown -R pi:pi /home/pi/' ,shell=True)
             subprocess.call("sudo mv -f /home/pi/ysynth4/ysynth4.py.1 /home/pi/ysynth4/ysynth4.py" , shell=True)
             disp.display(img)
             time.sleep(2)
             draw.rectangle((0, 0, 160, 128), (0,0,0)) 
             disp.display(img)
             subprocess.call('sudo systemctl restart ysynth4.service', shell=True)
       
       if mode==2 and mode2_coordi ==4:
          time.sleep(0.05)
          dialog_open=1
          dialog_window0()
          draw.text((11, t_size_l_y+t_size_m_y*2+1),"     再起動しますか?",  font=fonts, fill=(0, 0, 0))
          draw.text((dialog_coordi_xl[dialog_coordi], dialog_coordi_yl[dialog_coordi]),cur_size,  font=fonts, fill=(0, 0, 0))
          disp.display(img)
          dialog_loop0("    再起動します...", "sudo reboot")
          draw.rectangle((0, 0, 160, 128), (0,0,0)) 


       if mode==2 and mode2_coordi ==5:
          time.sleep(0.05)
          dialog_open=1
          dialog_window0()
          draw.text((11, t_size_l_y+t_size_m_y*2+1),"シャットダウンしますか?",  font=fonts, fill=(0, 0, 0))
          draw.text((dialog_coordi_xl[dialog_coordi], dialog_coordi_yl[dialog_coordi]),cur_size,  font=fonts, fill=(0, 0, 0))
          disp.display(img)
          dialog_loop0("   シャットダウンします...", "sudo shutdown -h now")
          draw.rectangle((0, 0, 160, 128), (0,0,0)) 

       if mode==2 and mode2_coordi ==6:
          time.sleep(0.05)
          dialog_open=1
          dialog_window0()
          draw.text((11, t_size_l_y+t_size_m_y*2+1),"   リロードしますか?",  font=fonts, fill=(0, 0, 0))
          draw.text((dialog_coordi_xl[dialog_coordi], dialog_coordi_yl[dialog_coordi]),cur_size,  font=fonts, fill=(0, 0, 0))
          disp.display(img)
          dialog_loop0("    リロードします...", "sudo systemctl restart ysynth4.service")
          draw.rectangle((0, 0, 160, 128), (0,0,0))             
       if GPIO.input(input_UP) == 0:
          time.sleep(0.01)
          volume +=1
          if volume>100:
             volume=0
          subprocess.call('amixer cset numid=1 {}% > /dev/null'.format(volume) , shell=True)
          draw.rectangle((t_size_l_x*8+t_size_s_x*8, 0, t_size_l_x*9+t_size_s_x*10, t_size_s_y), (0,0,0))
          draw.text((t_size_l_x*8+t_size_s_x*8, 0),str(volume),  font=fonts, fill=(0, 255, 0))
          disp.display(img)
          while GPIO.input(input_UP) == 0 and longpush !=100: 
                time.sleep(0.01)
                longpush +=1
                if longpush==100:
                   break
                else:
                  continue
       if GPIO.input(input_DOWN) == 0:
          time.sleep(0.01)
          volume -=1
          if volume<0:
             volume=100
          subprocess.call('amixer cset numid=1 {}% > /dev/null'.format(volume) , shell=True)
          draw.rectangle((t_size_l_x*8+t_size_s_x*8, 0, t_size_l_x*9+t_size_s_x*10, t_size_s_y), (0,0,0))
          draw.text((t_size_l_x*8+t_size_s_x*8, 0),str(volume),  font=fonts, fill=(0, 255, 0))
          disp.display(img)
          while GPIO.input(input_DOWN) == 0 and longpush !=100: 
                time.sleep(0.01)
                longpush +=1
                if longpush==100:
                   break
                else:
                  continue     
             
    if (GPIO.input(input_LEFT) and GPIO.input(input_RIGHT) and GPIO.input(input_UP) and GPIO.input(input_DOWN) and GPIO.input(input_OK))== 1:  
       longpush=0 
    if msg is None:         
       time.sleep(0.00001)  
##MIDI入力をディスプレイに反映する処理ここまで
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
mode1_coordi_yl=[t_size_l_y+t_size_m_y+1, t_size_l_y+t_size_m_y*2+1]

mode2_coordi=0
mode2_coordi_xl=[3,3,3,3,3,3,3]
mode2_coordi_yl=[t_size_l_y+t_size_m_y+1,t_size_l_y+t_size_m_y*2+1,\
   t_size_l_y+t_size_m_y*3+1,t_size_l_y+t_size_m_y*4+1,\
      t_size_l_y+t_size_m_y*5+1,t_size_l_y+t_size_m_y*6+1,\
         t_size_l_y+t_size_m_y*7+1,]

def mode0_default_disp():
   draw.rectangle((0, 0, 160, 128), (0,0,0))
   draw.text((mode0_coordi_xl[mode0_coordi], mode0_coordi_yl[mode0_coordi]),cur_size,  font=fonts, fill=(255, 255, 255))
   draw.text((cur_size_x+x, 0),"CH:",  font=fontl, fill=(55, 255, 255))
   draw.text((cur_size_x+x, t_size_l_y+t_size_m_y+1),"INS:", font=fontm, fill=(55, 255, 255))
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
   draw.text((cur_size_x+x, t_size_l_y+t_size_m_y+1),"SF2:", font=fontm, fill=(55, 255, 255))
   draw.text((cur_size_x+x, t_size_l_y+t_size_m_y*2+1),"SMF:",  font=fontm, fill=(55, 255, 255))
   draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y+1),"SGM-V2.01.sf2 ♪", font=fontm, fill=(255, 255, 55))
   draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y*2+1),"FeldschlachtI.mid ▶",  font=fontm, fill=(255, 255, 55))
   draw.text((t_size_l_x*8, 0),"SysVol: "+str(volume),  font=fonts, fill=(0, 255, 0))
   disp.display(img)

def mode2_default_disp():
   draw.rectangle((0, 0, 160, 128), (0,0,0))
   draw.text((mode2_coordi_xl[mode2_coordi], mode2_coordi_yl[mode2_coordi]),cur_size,  font=fonts, fill=(255, 255, 255))
   draw.text((cur_size_x+x, 0),"設定",  font=fontl, fill=(255, 255, 55))
   draw.text((cur_size_x+x, t_size_l_y+t_size_m_y+1),"SF2:", font=fontm, fill=(55, 255, 255))
   draw.text((cur_size_x+x, t_size_l_y+t_size_m_y*2+1),"WiFi:",  font=fontm, fill=(55, 255, 255))
   draw.text((cur_size_x+x, t_size_l_y+t_size_m_y*3+1),"Audio:",  font=fontm, fill=(55, 255, 255))
   draw.text((cur_size_x+x, t_size_l_y+t_size_m_y*4+1),"USBメモリ取り出し",  font=fontm, fill=(55, 255, 255))
   draw.text((cur_size_x+x, t_size_l_y+t_size_m_y*5+1),"Ysynth4アップデート",  font=fontm, fill=(55, 255, 255))
   draw.text((cur_size_x+x, t_size_l_y+t_size_m_y*6+1),"再起動", font=fontm, fill=(55, 255, 255))
   draw.text((cur_size_x+x, t_size_l_y+t_size_m_y*7+1),"シャットダウン",  font=fontm, fill=(55, 255, 255))
   draw.text((t_size_m_x*5, t_size_l_y+t_size_m_y+1),"SGM-V2.01.sf2 ♪", font=fontm, fill=(255, 255, 55))
   draw.text((t_size_m_x*6, t_size_l_y+t_size_m_y*2+1),"F660A-*******",  font=fontm, fill=(255, 255, 55))
   draw.text((t_size_m_x*7, t_size_l_y+t_size_m_y*3+1),"IQaudIODAC",  font=fontm, fill=(255, 255, 55))
   draw.text((t_size_l_x*8, 0),"SysVol: "+str(volume),  font=fonts, fill=(0, 255, 0))
   disp.display(img)
##初期設定ここまで##

msg = None
subprocess.Popen('sudo timidity -c /home/pi/SGM-V2.01.cfg', shell=True)
time.sleep(2)
subprocess.call('aconnect 128:0 131:0', shell=True)
subprocess.call('aconnect 128:0 130:0', shell=True)
subprocess.call('aconnect 129:0 128:1', shell=True)
subprocess.call('aconnect 129:0 131:0', shell=True)
subprocess.call('aconnect 128:0 20:0', shell=True)
subprocess.call('aconnect 129:0 20:0', shell=True)
subprocess.call('aconnect 20:0 130:0', shell=True)
subprocess.call('aconnect 20:0 128:1', shell=True)
subprocess.call('aconnect 20:0 24:0', shell=True)
subprocess.call('aconnect 20:0 131:0', shell=True)

mode0_default_disp()

while True:
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
          mode0_default_disp()       
       if mode==1:
          mode1_default_disp()
       if mode==2:      
          mode2_default_disp()
       while (GPIO.input(input_MODE)) == 0: 
          continue 

    if GPIO.input(input_OK) == 0: 
       if mode==2 and mode2_coordi ==4:
          draw.rectangle((0, 0, 160, 128), (0,0,0)) 
          disp.display(img)
          subprocess.call("sudo rm -f /home/pi/ysynth4/ysynth4.py" , shell=True)
          subprocess.call("sudo wget https://raw.githubusercontent.com/YoutechA320U/ysynth4/master/ysynth4.py" ,shell=True)
          subprocess.call('sudo systemctl restart ysynth4.service', shell=True)
       
       if mode==2 and mode2_coordi ==5:
          draw.rectangle((0, 0, 160, 128), (0,0,0)) 
          disp.display(img)
          subprocess.Popen("sudo reboot" ,shell=True)
       if mode==2 and mode2_coordi ==6:
          draw.rectangle((0, 0, 160, 128), (0,0,0)) 
          disp.display(img)
          subprocess.Popen("sudo shutdown -h now" ,shell=True)
       time.sleep(0.01)
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
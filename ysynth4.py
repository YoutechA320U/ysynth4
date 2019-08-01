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
    rst=25,             # 18 for back BG slot, 19 for front BG slot.
    rotation=90,
    width=128,
    height=160,
    spi_speed_hz=40000000
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

volume = 90
mode = 0
CC2 = 0
CC1 = 0
prevolume = 0
premode = 0
preCC2 = 0
preCC1 = 0
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

input_A = 6
input_B = 24
input_C = 16

GPIO.setmode(GPIO.BCM)
GPIO.setup(input_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(input_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(input_C, GPIO.IN, pull_up_down=GPIO.PUD_UP)

subprocess.call('sudo killall ttymidi', shell=True)
subprocess.call('sudo killall timidity', shell=True)
subprocess.Popen('sudo /home/pi/ttymidi -s /dev/ttyAMA0 -b 38400', shell=True)
time.sleep(1)
midiin = rtmidi.MidiIn()
midiin.open_virtual_port("Ysynth_in") # 仮想MIDI入力ポートの名前
midiin.ignore_types(sysex=False)
def allnoteoff():
    a = 0xb0
    while (a < 0xbf ):
        midiout.send_message([a, 0x78, 0x00])
        a += 1
subprocess.call('amixer cset numid=1 95% > /dev/null', shell=True)


font = ImageFont.truetype('/usr/share/fonts/truetype/takao-gothic/TakaoGothic.ttf', 14, encoding='unic')
fontl = ImageFont.truetype('/usr/share/fonts/truetype/takao-gothic/TakaoGothic.ttf', 20, encoding='unic')
fonts = ImageFont.truetype('/usr/share/fonts/truetype/takao-gothic/TakaoGothic.ttf', 12, encoding='unic')

x = 3
y = 0
MESSAGE="AAAA" #4文字分

xa, size_y  = draw.textsize(MESSAGE, fontl)
##初期設定ここまで##

draw.text((x, 0),"CH:",  font=fontl, fill=(55, 255, 255))
draw.text((x, 21),"PC :", font=font, fill=(55, 255, 255))
draw.text((x, 35),"VOL:",  font=font, fill=(55, 255, 255))
draw.text((x, 49),"EXP:",  font=font, fill=(55, 255, 255))
draw.text((x, 63),"PAN:",  font=font, fill=(55, 255, 255))
draw.text((x, 77),"MOD:",  font=font, fill=(55, 255, 255))
draw.text((x, 91),"REV:", font=font, fill=(55, 255, 255))
draw.text((x, 105),"CHO:",  font=font, fill=(55, 255, 255))
draw.text((xa-8, 0),str("{0:02}".format(midiCH + 1)),  font=fontl, fill=(255, 255, 55))
draw.text((xa-10, 21),str("{0:03d}".format(midiPROG[midiCH] + 1)), font=font, fill=(255, 255, 55))
draw.text((xa-10, 35),str("{0:03d}".format(midiCC7[midiCH])),  font=font, fill=(255, 255, 55))
draw.text((xa-10, 49),str("{0:03d}".format(midiCC11[midiCH])),  font=font, fill=(255, 255, 55))
draw.text((xa-10, 63),str("{0:03d}".format(midiCC10[midiCH]-64)),  font=font, fill=(255, 255, 55))
draw.text((xa-10, 77),str("{0:03d}".format(midiCC1[midiCH])),  font=font, fill=(255, 255, 55))
draw.text((xa-10, 91),str("{0:03d}".format(midiCC91[midiCH])), font=font, fill=(255, 255, 55))
draw.text((xa-10, 105),str("{0:03d}".format(midiCC93[midiCH])),  font=font, fill=(255, 255, 55))
draw.text((xa*2-10, 21),"DLY   :", font=font, fill=(55, 255, 255))
draw.text((xa*3, 21),str("{0:03d}".format(midiCC94[midiCH])), font=font, fill=(255, 255, 55))
draw.text((xa*2-10, 35),"P.BEND:", font=font, fill=(55, 255, 255))
draw.text((xa*3, 35),str("{0:04d}".format(0x80*pb2[midiCH]+pb1[midiCH]-8192)), font=font, fill=(255, 255, 55))
disp.display(img)

timer = time.time()
msg = 0
subprocess.Popen('sudo timidity -c /home/pi/SGM-V2.01.cfg', shell=True)
time.sleep(3)
subprocess.call('aconnect 128:0 130:0', shell=True)
subprocess.call('aconnect 128:0 129:0', shell=True)
subprocess.call('aconnect 128:0 20:0', shell=True)
subprocess.call('aconnect 20:0 129:0', shell=True)
subprocess.call('aconnect 20:0 128:1', shell=True)
subprocess.call('aconnect 20:0 24:0', shell=True)
while True:
    msg = midiin.get_message()
##MIDI入力をディスプレイに反映する処理
    if msg is not None:
       message, deltatime = msg
       #print(message)
       timer += deltatime
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
              draw.rectangle((xa-10, 21, 65, 128), (0,0,0))
              draw.text((xa-10, 21),str("{0:03d}".format(midiPROG[midiCH] + 1)), font=font, fill=(255, 255, 55))
              draw.text((xa-10, 35),str("{0:03d}".format(midiCC7[midiCH])),  font=font, fill=(255, 255, 55))
              draw.text((xa-10, 49),str("{0:03d}".format(midiCC11[midiCH])),  font=font, fill=(255, 255, 55))
              draw.text((xa-10, 63),str("{0:03d}".format(midiCC10[midiCH]-64)),  font=font, fill=(255, 255, 55))
              draw.text((xa-10, 77),str("{0:03d}".format(midiCC1[midiCH])),  font=font, fill=(255, 255, 55))
              draw.text((xa-10, 91),str("{0:03d}".format(midiCC91[midiCH])), font=font, fill=(255, 255, 55))
              draw.text((xa-10, 105),str("{0:03d}".format(midiCC93[midiCH])),  font=font, fill=(255, 255, 55))
              draw.rectangle((xa*3, 21, 160, 128), (0,0,0))
              draw.text((xa*3, 21),str("{0:03d}".format(midiCC94[midiCH])), font=font, fill=(255, 255, 55))
              draw.text((xa*3, 35),str("{0:04d}".format(0x80*pb2[midiCH]+pb1[midiCH]-8192)), font=font, fill=(255, 255, 55))
              disp.display(img)
       except :
        continue
       for forlch in range(16):
        if message[0] == 192+forlch :
           if midiPROG[forlch] != message[1]:
              midiPROG[forlch] = message[1]
              if mode == 0 and forlch==midiCH:
                 draw.rectangle((xa-10, 21, 65, 34), (0,0,0))
                 draw.text((xa-10, 21),str("{0:03d}".format(midiPROG[forlch] + 1)), font=font, fill=(255, 255, 55))
                 disp.display(img)
        if message[0] == 176+forlch and message[1] ==7:
           if midiCC7[forlch] != message[2]:
              midiCC7[forlch] = message[2]
              if mode == 0 and forlch==midiCH:
                 draw.rectangle((xa-10, 35, 65, 48), (0,0,0))
                 draw.text((xa-10, 35),str("{0:03d}".format(midiCC7[forlch])),  font=font, fill=(255, 255, 55))
                 disp.display(img)
        if message[0] == 176+forlch and message[1] ==11:
           if midiCC11[forlch] != message[2]:
              midiCC11[forlch] = message[2]
              if mode == 0 and forlch==midiCH:
                 draw.rectangle((xa-10, 49, 65, 62), (0,0,0))
                 draw.text((xa-10, 49),str("{0:03d}".format(midiCC11[forlch])),  font=font, fill=(255, 255, 55))
                 disp.display(img)
        if message[0] == 176+forlch and message[1] ==10:
           if midiCC10[forlch] != message[2]:
              midiCC10[forlch] = message[2] 
              if mode == 0 and forlch==midiCH:
                 draw.rectangle((xa-10, 63, 65, 76), (0,0,0))
                 draw.text((xa-10, 63),str("{0:03d}".format(midiCC10[forlch]-64)),  font=font, fill=(255, 255, 55))
                 disp.display(img)
        if message[0] == 176+forlch and message[1] ==1:
           if midiCC1[forlch] != message[2]:
              midiCC1[forlch] = message[2]
              if mode == 0 and forlch==midiCH:
                 draw.rectangle((xa-10, 77, 65, 90), (0,0,0))
                 draw.text((xa-10, 77),str("{0:03d}".format(midiCC1[forlch])),  font=font, fill=(255, 255, 55))
                 disp.display(img)
        if message[0] == 176+forlch and message[1] ==91:
           if midiCC91[forlch] != message[2]:
              midiCC91[forlch] = message[2]
              if mode == 0 and forlch==midiCH:
                 draw.rectangle((xa-10, 91, 65, 104), (0,0,0))
                 draw.text((xa-10, 91),str("{0:03d}".format(midiCC91[forlch])), font=font, fill=(255, 255, 55))
                 disp.display(img)
        if message[0] == 176+forlch and message[1] ==93:
           if midiCC93[forlch] != message[2]:
              midiCC93[forlch] = message[2]
              if mode == 0 and forlch==midiCH:
                 draw.rectangle((xa-10, 105, 65, 128), (0,0,0))
                 draw.text((xa-10, 105),str("{0:03d}".format(midiCC93[forlch])),  font=font, fill=(255, 255, 55))
                 disp.display(img)
        if message[0] == 176+forlch and message[1] ==94:
           if midiCC94[forlch] != message[2]:
              midiCC94[forlch] = message[2]
              if mode == 0 and forlch==midiCH:
                 draw.rectangle((xa*3, 21, 160, 34), (0,0,0))
                 draw.text((xa*3, 21),str("{0:03d}".format(midiCC94[forlch])), font=font, fill=(255, 255, 55))
                 disp.display(img)
        if message[0] == 0xe0+forlch :
           if pb1[forlch] != message[1] or pb2[forlch] != message[2]:
              pb1[forlch] = message[1]
              pb2[forlch] = message[2]
              if mode == 0 and forlch==midiCH:
                 draw.rectangle((xa*3, 35, 160, 48), (0,0,0))
                 draw.text((xa*3, 35),str("{0:04d}".format(0x80*pb2[midiCH]+pb1[forlch]-8192)), font=font, fill=(255, 255, 55))
                 disp.display(img)
    
    if GPIO.input(input_A) == 0:
       time.sleep(0.1)  
       midiCH -=1 
       if midiCH<0:
          midiCH=15 
       #print(midiCH)
       draw.rectangle((xa-8, 0, 65, 20), (0,0,0))
       draw.text((xa-8, 0),str("{0:02}".format(midiCH + 1)),  font=fontl, fill=(255, 255, 55))
       draw.rectangle((xa-10, 21, 65, 128), (0,0,0))
       draw.text((xa-10, 21),str("{0:03d}".format(midiPROG[midiCH] + 1)), font=font, fill=(255, 255, 55))
       draw.text((xa-10, 35),str("{0:03d}".format(midiCC7[midiCH])),  font=font, fill=(255, 255, 55))
       draw.text((xa-10, 49),str("{0:03d}".format(midiCC11[midiCH])),  font=font, fill=(255, 255, 55))
       draw.text((xa-10, 63),str("{0:03d}".format(midiCC10[midiCH]-64)),  font=font, fill=(255, 255, 55))
       draw.text((xa-10, 77),str("{0:03d}".format(midiCC1[midiCH])),  font=font, fill=(255, 255, 55))
       draw.text((xa-10, 91),str("{0:03d}".format(midiCC91[midiCH])), font=font, fill=(255, 255, 55))
       draw.text((xa-10, 105),str("{0:03d}".format(midiCC93[midiCH])),  font=font, fill=(255, 255, 55))
       draw.rectangle((xa*3, 21, 160, 128), (0,0,0))
       draw.text((xa*3, 21),str("{0:03d}".format(midiCC94[midiCH])), font=font, fill=(255, 255, 55))
       draw.text((xa*3, 35),str("{0:04d}".format(0x80*pb2[midiCH]+pb1[midiCH]-8192)), font=font, fill=(255, 255, 55))
       disp.display(img)
       while (GPIO.input(input_A)) == 0: 
             continue  
    if GPIO.input(input_B) == 0:  
       time.sleep(0.1)  
       midiCH +=1  
       if midiCH>15:
          midiCH=0
       #print(midiCH)
       draw.rectangle((xa-8, 0, 65, 20), (0,0,0))
       draw.text((xa-8, 0),str("{0:02}".format(midiCH + 1)),  font=fontl, fill=(255, 255, 55))
       draw.rectangle((xa-10, 21, 65, 128), (0,0,0))
       draw.text((xa-10, 21),str("{0:03d}".format(midiPROG[midiCH] + 1)), font=font, fill=(255, 255, 55))
       draw.text((xa-10, 35),str("{0:03d}".format(midiCC7[midiCH])),  font=font, fill=(255, 255, 55))
       draw.text((xa-10, 49),str("{0:03d}".format(midiCC11[midiCH])),  font=font, fill=(255, 255, 55))
       draw.text((xa-10, 63),str("{0:03d}".format(midiCC10[midiCH]-64)),  font=font, fill=(255, 255, 55))
       draw.text((xa-10, 77),str("{0:03d}".format(midiCC1[midiCH])),  font=font, fill=(255, 255, 55))
       draw.text((xa-10, 91),str("{0:03d}".format(midiCC91[midiCH])), font=font, fill=(255, 255, 55))
       draw.text((xa-10, 105),str("{0:03d}".format(midiCC93[midiCH])),  font=font, fill=(255, 255, 55))
       draw.rectangle((xa*3, 21, 160, 128), (0,0,0))
       draw.text((xa*3, 21),str("{0:03d}".format(midiCC94[midiCH])), font=font, fill=(255, 255, 55))
       draw.text((xa*3, 35),str("{0:04d}".format(0x80*pb2[midiCH]+pb1[midiCH]-8192)), font=font, fill=(255, 255, 55))
       disp.display(img)
       while (GPIO.input(input_B)) == 0: 
             continue
    if GPIO.input(input_C) == 0: 
       time.sleep(0.1)  
       subprocess.call('sudo shutdown -h now', shell=True)
    if msg is  None:         
       time.sleep(0.00001)  
##MIDI入力をディスプレイに反映する処理ここまで
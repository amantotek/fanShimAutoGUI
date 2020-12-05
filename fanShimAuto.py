#!/usr/bin/python3
# -*- coding: utf-8 -*-
VEERSION = "20201204_2117" #Add prog name to About & abort multiple start 

#On RaspberryPi4
# $ cd ~/fanshim-python/examples
# $ mousepad fanShimAuto.py &
# $ sudo python3 fanShimAuto.py

#Get below sourcefile from https://raw.githubusercontent.com/PySimpleGUI/PySimpleGUI/master/PySimpleGUI.py
import PySimpleGUI20201117 as sg
#--------------------------------------------------------------------------
#Part 1 Skeleton PySimpleGUI GUI
TAB16 = 'Courier 16' #was 14 Evenly spaced for tables
HEL12 = 'Helvetica 12' #Helvetica is not evenly spaced

iXmax = 100 #readings horizontal displayed
iYmaxDegC = 80

tbMain = [
  [sg.Multiline("Initialising Main display",size=(55,7),key='KYMMA',autoscroll=False,write_only=True,font=TAB16)],
  [sg.T('',size=(65,2),key='KYMTA',justification='center')]
  ]

tbPlot = [
 [sg.Graph(canvas_size=(800, 600), graph_bottom_left=(-15,-15), graph_top_right=(iXmax+20,iYmaxDegC+20),float_values=True,background_color='white',k='KYPGA',tooltip='Pi4degC')]
]

tbAbout = [[sg.Multiline(size=(65,20),key='KYAMA',autoscroll=False,write_only=True,font=HEL12)]]

#With key; 3rd char is C for Close, 4th char is B for Button, 5th char for function
tbClose = [
    [sg.B('Restart',key='KYCBR',enable_events=True,button_color=('black','orange'))],
    [sg.B('eXit',k='KYCBX',enable_events=True,button_color=('black','red'))]
  ]

# The TabgGroup layout - it must contain only Tabs
#See https://github.com/PySimpleGUI/PySimpleGUI/issues/2591
TXNMAIN = "Main"
TXNPLOT = "Plot"
TXNABOUT = "About"
TXNCLOSE = "Close"
sgTabName = TXNMAIN #Starts on this tab

laytopout = [
  [sg.TabGroup([[sg.Tab(TXNMAIN,tbMain),sg.Tab(TXNPLOT,tbPlot), \
  sg.Tab(TXNABOUT,tbAbout),sg.Tab(TXNCLOSE,tbClose)]],key='KYTAB',enable_events=True)]
    ]

#from fanshim import FanShim
from threading import Lock
import colorsys
#import psutil NOT AVAILABLE
#import argparse
#import signal
import sys

#--------------------------------------------------------------------------
#Part 2 Constants and Global Variables
iDegCMax = 50.0 #degC Above this turn on fan
iDegCMin = 40.0 #degC Below this turn off fan
argsDOTbrightness = 255.0 #LED brightness, from 0 to 255

#--------------------------------------------------------------------------
#Part 3 Functions

#Fanshim class begin
#Source: ~/fanshim-python/examples/egg/fanshim/
# https://sourceforge.net/p/raspberry-gpio-python/wiki/BasicUsage/
#Fanshim doesn't seem to install correctly on my RasPi4 running Ubuntu #58
# https://github.com/pimoroni/fanshim-python/issues/58
#For Xubuntu or other Ubuntu flavours or Mint the Pimoroni install, intended for Raspian OS, loads Python2.
#To keep control of what is loaded the below extracted class avoids needing the Pimoroni install 

# https://www.raspberrypi.org/forums/viewtopic.php?t=88861
#  I really would prefer not to have to sudo every time I use GPIO!
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")
import time
try:
    from plasma import legacy as plasma
except ImportError:
    import plasma
import atexit
from threading import Thread

__version__ = '0.0.4'

class FanShim():
    def __init__(self, pin_fancontrol=18, pin_button=17, button_poll_delay=0.05):
        """FAN Shim.

        :param pin_fancontrol: BCM pin for fan on/off
        :param pin_button: BCM pin for button

        """
        self._pin_fancontrol = pin_fancontrol
        self._pin_button = pin_button
        self._poll_delay = button_poll_delay
        self._button_press_handler = None
        self._button_release_handler = None
        self._button_hold_handler = None
        self._button_hold_time = 2.0
        self._t_poll = None

        atexit.register(self._cleanup)

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._pin_fancontrol, GPIO.OUT)
        GPIO.setup(self._pin_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        plasma.set_clear_on_exit(True)
        plasma.set_light_count(1)
        plasma.set_light(0, 0, 0, 0)

    '''def start_polling(self):
        """Start button polling."""
        if self._t_poll is None:
            self._t_poll = Thread(target=self._run)
            self._t_poll.daemon = True
            self._t_poll.start()'''

    def stop_polling(self):
        """Stop button polling."""
        if self._t_poll is not None:
            self._running = False
            self._t_poll.join()

    '''def on_press(self, handler=None):
        """Attach function to button press event."""
        def attach_handler(handler):
            self._button_press_handler = handler
            self.start_polling()

        if handler is not None:
            attach_handler(handler)
        else:
            return attach_handler

    def on_release(self, handler=None):
        """Attach function to button release event."""
        def attach_handler(handler):
            self._button_release_handler = handler
            self.start_polling()

        if handler is not None:
            attach_handler(handler)
        else:
            return attach_handler

    def on_hold(self, handler=None):
        """Attach function to button hold event."""
        def attach_handler(handler):
            self._button_hold_handler = handler
            self.start_polling()

        if handler is not None:
            attach_handler(handler)
        else:
            return attach_handler'''

    def set_hold_time(self, hold_time):
        """Set the button hold time in seconds.

        :param hold_time: Amount of time button must be held to trigger on_hold (in seconds)

        """
        self._button_hold_time = hold_time

    def get_fan(self):
        """Get current fan state."""
        return GPIO.input(self._pin_fancontrol)

    #def toggle_fan(self):
    #    """Toggle fan state."""
    #    return self.set_fan(False if self.get_fan() else True)

    def set_fan(self, fan_state):
        """Set the fan on/off.

        :param fan_state: True/False for on/off

        """
        GPIO.output(self._pin_fancontrol, True if fan_state else False)
        return True if fan_state else False

    def set_light(self, r, g, b):
        """Set LED.

        :param r: Red (0-255)
        :param g: Green (0-255)
        :param b: Blue (0-255)

        """
        plasma.set_light(0, r, g, b)
        plasma.show()

    def _cleanup(self):
        self.stop_polling()

    def _run(self):
        self._running = True
        last = 1

        while self._running:
            current = GPIO.input(self._pin_button)
            # Transition from 1 to 0
            if last > current:
                self._t_pressed = time.time()
                self._hold_fired = False

                if callable(self._button_press_handler):
                    self._t_repeat = time.time()
                    Thread(target=self._button_press_handler).start()

            if last < current:
                if callable(self._button_release_handler):
                    Thread(target=self._button_release_handler, args=(self._hold_fired,)).start()

            if current == 0:
                if not self._hold_fired and (time.time() - self._t_pressed) > self._button_hold_time:
                    if callable(self._button_hold_handler):
                        Thread(target=self._button_hold_handler).start()
                    self._hold_fired = True

            last = current

            time.sleep(self._poll_delay)
#Fanshim class end

def update_led_temperature(temp):
    led_busy.acquire() #Uses Lock()
    temp = float(temp)
    temp -= iDegCMin
    temp /= float(iDegCMax - iDegCMin)
    temp = max(0, min(1, temp))
    temp = 1.0 - temp
    temp *= 120.0
    temp /= 360.0
    r, g, b = [int(c * 255.0) for c in colorsys.hsv_to_rgb(temp, 1.0, argsDOTbrightness / 255.0)]
    fanshim.set_light(r, g, b)
    led_busy.release()

def get_cpu_temp():
  #DegC output e.g. 36.024 as integer
  fyx = open('/sys/class/thermal/thermal_zone0/temp', 'r')
  return int(fyx.read())/1000

def set_fan(status):
    global bgEnaable
    changed = False
    if status != bgEnaable:
        changed = True
        fanshim.set_fan(status)
    bgEnaable = status
    return changed

def set_automatic(status):
    global armed, iLast_change
    armed = status
    iLast_change = 0

def addAndGraph(fDeggc,i01):
  global lOfDegC
   
  lOfDegC.append("{} {}".format(fDeggc,i01))
  #Limit number of readings stored to those viewable
  while len(lOfDegC) > iXmax:
    #If iXmax is 3 lOfDegC can have indexes 0 1 2 3 where 0 not used. So keep len=4
    lOfDegC.pop(0) #remove 1st item
  #Display from list all points 
  iXpt = 1 #Index 0 is not used
  for sDegcBoo in lOfDegC:
    lDegcBoo = sDegcBoo.split(" ")
    fDegC = float(lDegcBoo[0]) #DegC
    iStaat = int(lDegcBoo[1]) #1 (on) or 0 (fan off)
    if iStaat == 1:
      sClr = 'red'
    else:
      sClr = 'green'
    ixoxd = lPtIndexs[iXpt] #Recover index of point (LIST INDEX OUT OF RANGE)
    graaf.RelocateFigure(ixoxd,iXpt,fDegC)
    graaf.TKCanvas.itemconfig(ixoxd,fill=sClr)  
    iXpt += 1

fanshim = FanShim()
fanshim.set_hold_time(1.0)
fanshim.set_fan(False) #If cold & True on startup it could stay below max threshold forever & never turn off
armed = True
led_busy = Lock()
bgEnaable = False
iLast_change = 0
#signal.signal(signal.SIGTERM, clean_exit)

#--------------------------------------------------------------------------
#Part 5 Use GUI
wiindow = sg.Window('fan shim auto',laytopout,finalize=True, return_keyboard_events=True)

import os

#Plot setup begin
# Draw graph axis  (x hor,y vert)
graaf = wiindow['KYPGA']

graaf.DrawLine((0,0), (0,iYmaxDegC)) #Vertical   
graaf.DrawText( "DegC", (-5,80), color='black')
for iDy in range(0, iYmaxDegC, 10):    
  graaf.DrawLine((-3,iDy), (0,iDy))    
  if iDy != 0:
    graaf.DrawText( iDy, (-5,iDy), color='blue') 

graaf.DrawLine((0,0), (iXmax,0)) #Horizontal   
graaf.DrawText( "x 10 sec", (100,-5), color='black') # **
for iDx in range(0, iXmax, 20):    
  graaf.DrawLine((iDx,-3), (iDx,0)) #-3 is below the axis tick   
  if iDx != 0:    
    graaf.DrawText( iDx, (iDx,-5), color='green')

#Draw max min threholds
graaf.DrawLine((0,iDegCMax), (iXmax,iDegCMax))   
graaf.DrawLine((0,iDegCMin), (iXmax,iDegCMin))  

#Draw all points at bottom of graph and store indexes to each point     
lPtIndexs = []
iPtSz = 1.4 #Size of points
#range(1, 6) gives 1 2 3 4 5
lPtIndexs.append(0) #Index 0 not used
for iZx in range(1, iXmax+1):
  iPtIndx = graaf.DrawPoint((iZx,0), iPtSz, color='pink')
  lPtIndexs.append(iPtIndx)

lOfDegC = []
#Plot setup end

#Fill in About multiline
sIinfo = "Version: {}\n\n".format(VEERSION)
sIinfo += "Raspberry Pi info:\n"
#GPIO.RPI_INFO is a dictionary item
for SKeey, sValuu in GPIO.RPI_INFO.items():
  sIinfo += "  {}  :  {}\n".format(SKeey,sValuu)
sIinfo += "\nUses parts of https://github.com/pimoroni/fanshim-python/tree/master/examples automatic.py and class FanShim\n\nPut fan on if >= {} degC\nPut fan off if <= {} degC".format(iDegCMax,iDegCMin)
wiindow["KYAMA"].Update(sIinfo) #Write into the About multiline

#Part 6 Periodically work here
iSecOld = 99
while True:  # Event Loop
  eveent, valuues = wiindow.read(timeout=100) #29Oct2020 https://www.reddit.com/r/learnpython/comments/fpve1e/pysimplegui_problem_with_event_loop/
  if eveent == sg.WIN_CLOSED or eveent == 'Exit':
    break
  
  #CLose
  if eveent == 'KYCBX':
    break #User selected exit
  if eveent == 'KYCBR':
    #Restart
    pzython = sys.executable #20200808
    os.execl(pzython, pzython, * sys.argv) 
  
  sWithHMS = os.popen('date +"%Y %b %m %d %H %M %S %Z"').read()
  #Above is like: 2020 Aug 08 26 15 16 45 BST
  lItms = sWithHMS.split(' ')
  iSecNow = int(lItms[6]) #secs 00 to 59
  if iSecNow == iSecOld:
    continue #back to top of while loop
  iSecOld = iSecNow #Keep current second
  #Here at start of a fresh second
  #if iSecNow != 0 and iSecNow != 30:  (every 30secs)
  #Below if clock second divided by 2nd number has non zero remainder then don't execute further
  if iSecNow % 10 != 0:
    continue #don't execute further.
  #Here periodically 10s **
  #DegC control begin
  #As https://github.com/pimoroni/fanshim-python/tree/master/examples automatic.py
  iDegCAct = get_cpu_temp()
  if iDegCAct >= iDegCMax:
    fanshim.set_fan(True) #Turn on fan as above max threshold
    bgEnaable = True
  elif iDegCAct <= iDegCMin:
    fanshim.set_fan(False) #Turn off fan as below min threshold
    bgEnaable = False
  #if set_fan(bgEnaable):
  #  iLast_change = iDegCAct
  iTmp = fanshim.get_fan() # (1=On, 0=Off)
  sOnOrOff = ("On" if iTmp == 1 else "Off")
  print("{} {:05.02f} {}".format(iSecNow,iDegCAct,sOnOrOff))
  update_led_temperature(iDegCAct)
  addAndGraph(iDegCAct,iTmp)
  #DegC control end

  if sgTabName == TXNMAIN:
    #Show temperature on main display
    sWrn = ("** WARN HI **" if iDegCAct > iDegCMax else "")
    wiindow["KYMMA"].Update("DegC\nMax   {}\nActual {} {} {}\nMin   {}".format(iDegCMax,iDegCAct,sOnOrOff,sWrn,iDegCMin))
  
  elif sgTabName == TXNPLOT:
    #----------------Refresh Graph page------------------
    #https://pysimplegui.readthedocs.io/en/latest/call%20reference/#graph-element
    pass
  
  elif sgTabName == TXNABOUT:
    pass #tab with fixed content not refreshed
  
  elif sgTabName == TXNCLOSE:
    pass #tab with fixed content not refreshed
  
  else:
    print("sgTabName bad, saw {}".format(sgTabName))

#Part 7 Closedown nicely    
wiindow.close()
del wiindow #https://www.reddit.com/r/learnpython/comments/dj1za4/tkinter_threading_error_in_nonthreaded_program/


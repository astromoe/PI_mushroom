#!/usr/bin/python

import urllib2
import re
import sys
import time
import rrdtool
import parseConfig
import argparse
import serial
import json

# TODO
# - Add serial to settings methods

#
# Define some global variables
#
rrdDir      = "/home/pi/mushroomPi/rrd/"
imagesDir   = "/home/pi/mushroomPi/htdocs/images/"
url         = "http://forecast.weather.gov/MapClick.php?CityName=Morrisville&state=VT&site=BTV&textField1=44.5586&textField2=-72.5964&e=0#.U0g-lVeyqRa"

#
# Methods
#

#
# Process the control functions
#
def processControl():
  configDict = parseConfig.parse()
  debug(3,"Current config: " + `configDict`)
  if configDict.get('control','manual')  == 'manual':
    manualControl(configDict)
  else:
    automaticControl(configDict)

#
# Process the manual control
#
def manualControl( configDict ):
  debug(3,"Processing manual control")

  # Check if foggers is different
  if configDict.get('manualFoggers') != lastPoll.get('foggers'):
    debug(2,'manualFoggers: ' + configDict.get('manualFoggers') + ' != ' + lastPoll.get('foggers'))
    setFoggers(configDict.get('manualFoggers'))

  # Check if fan is different
  if configDict.get('manualFan') != lastPoll.get('fan'):
    debug(2,'manualFan: ' + configDict.get('manualFan') + ' != ' + lastPoll.get('fan'))
    setFan(configDict.get('manualFan'))

#
# Process the automatic control
#
def automaticControl( configDict ):
  debug(3,"Processing automatic control")

  # Check humidity and foggers
  if lastPoll.get('humidity') < configDict.get('autoHumidity'):
    debug(2,'Humidity: current (' + lastPoll.get('humidity') + ') is below threshold (' + configDict.get('autoHumidity') + ')')
    if lastPoll.get('foggers') != configDict.get('autoFoggers'):
      setFoggers(configDict.get('autoFoggers'))
  else:
    debug(2,'Humidity: current (' + lastPoll.get('humidity') + ') is above/equal threshold (' + configDict.get('autoHumidity') + ')')
    if lastPoll.get('foggers') != '0':
      setFoggers('0')

  # Check CO2 and fan
  if lastPoll.get('co2') > configDict.get('autoCO2'):
    debug(2,'CO2: current (' + lastPoll.get('co2') + ') is above threshold (' + configDict.get('autoCO2') + ')')
    if lastPoll.get('fan') != configDict.get('autoFan'):
      setFan(configDict.get('autoFan'))
  else:
    debug(2,'CO2: current (' + lastPoll.get('co2') + ') is below threshold (' + configDict.get('autoCO2') + ')')
    if lastPoll.get('fan') != '0':
      setFan('0')

#
# Methods to set arduino settings via serial
#
def setFoggers(foggers):
  debug(1,"Setting foggers " + foggers)
  ser.write("set foggers " + foggers + "\n")
  debug(1,ser.readline().rstrip())

def setFan(perc):
  debug(1,"Setting fan " + perc)
  ser.write("set fan " + perc + "\n")
  debug(1,ser.readline().rstrip())

#
# Poll the serial
#
def poll():
  global lastPoll
  lastPoll = {
    'humidity'    : '0',
    'temperature' : '0',
    'co2'         : '0',
    'foggers'     : '0',
    'fan'         : '0',
  }

  # Polling sometimes fails so try 3 times to get a response
  for x in range(1,3):
    debug(2,"Polling try: "+`x`)
    # Humidity:F:C:CO2:Foggers:Fan
    ser.write("poll\n")
    polled = ser.readline().rstrip()
    debug(1,polled)
    if not polled: continue
    parts = polled.split(';')
    if ( len(parts) == 6 ): break
  if not polled or len(parts) != 6:
    debug(1,'Polling failed')
    return

  # Save the data for other methods to access
  lastPoll = {
    'humidity'    : parts[0],
    'temperature' : parts[2],
    'co2'         : parts[3],
    'foggers'     : parts[4],
    'fan'         : parts[5],
  }
  debug(3,'Poll: ' + `lastPoll`)

  # Write to the databases
  ret = rrdtool.update(rrdDir+'temperature.rrd','N:' + lastPoll.get('temperature'))
  ret = rrdtool.update(rrdDir+'humidity.rrd','N:'    + lastPoll.get('humidity'))
  ret = rrdtool.update(rrdDir+'co2.rrd','N:'         + lastPoll.get('co2'))
  ret = rrdtool.update(rrdDir+'foggers.rrd','N:'     + lastPoll.get('foggers'))
  ret = rrdtool.update(rrdDir+'fan.rrd','N:'         + lastPoll.get('fan'))
  return

#
# Read the outside temperature
#
def getOutside():
  debug(2,'Getting outside')

  f = urllib2.urlopen(url)
  content = f.read()

  temp = 0
  m = re.search('class="myforecast-current-lrg">(\d+)', content)
  if m:
    temp = int(m.group(1))

  hum = 0
  m = re.search('Humidity</span>(\d+)%', content)
  if m:
    hum = int(m.group(1))

  global lastOutside
  lastOutside = {'temperature':temp,'humidity':hum}
  debug(3,'Outside: ' + `lastOutside`)

  # Write to the database
  ret = rrdtool.update(rrdDir+'outsideTemp.rrd','N:' + `temp` + ':' + `hum`)

#
# Process graphs
#
def processGraphs():
  debug(1,'Processing Graphs')

  times = ['-8h','-2d','-1w','-1m','-1y']

  for t in times:
    time.sleep(0.5)
    ret = rrdtool.graph( imagesDir  + "outsideTemp" + t + ".png", "--start", t,
     "DEF:temperature="+rrdDir+"outsideTemp.rrd:temperature:AVERAGE",
     "DEF:humidity="+rrdDir+"outsideTemp.rrd:humidity:AVERAGE",
     "LINE1:temperature#00FF00:Temperature",
     "LINE2:humidity#0000FF:Humidity\\r",
     "GPRINT:temperature:LAST:Temperature Current\: %3.0lf",
     "GPRINT:temperature:AVERAGE:Avg\: %3.0lf",
     "GPRINT:temperature:MAX:Max\: %3.0lf",
     "GPRINT:temperature:MIN:Min\: %3.0lf \\r",
     "GPRINT:humidity:LAST:Humidity Current\: %3.0lf",
     "GPRINT:humidity:AVERAGE:Avg\: %3.0lf",
     "GPRINT:humidity:MAX:Max\: %3.0lf",
     "GPRINT:humidity:MIN:Min\: %3.0lf \\r")

    ret = rrdtool.graph( imagesDir  + "temperature" + t + ".png", "--start", t,
     "DEF:temperature="+rrdDir+"temperature.rrd:temperature:AVERAGE",
     "AREA:temperature#00FF00",
     "GPRINT:temperature:LAST:Temperature Current\: %3.0lf",
     "GPRINT:temperature:AVERAGE:Avg\: %3.0lf",
     "GPRINT:temperature:MAX:Max\: %3.0lf",
     "GPRINT:temperature:MIN:Min\: %3.0lf \\r")

    ret = rrdtool.graph( imagesDir  + "humidity" + t + ".png", "--start", t,
     "DEF:humidity="+rrdDir+"humidity.rrd:humidity:AVERAGE",
     "AREA:humidity#00FF00",
     "GPRINT:humidity:LAST:Humidity Current\: %3.0lf",
     "GPRINT:humidity:AVERAGE:Avg\: %3.0lf",
     "GPRINT:humidity:MAX:Max\: %3.0lf",
     "GPRINT:humidity:MIN:Min\: %3.0lf \\r")

    ret = rrdtool.graph( imagesDir  + "co2" + t + ".png", "--start", t,
     "DEF:co2="+rrdDir+"co2.rrd:co2:AVERAGE",
     "AREA:co2#00FF00",
     "GPRINT:co2:LAST:CO2 Current\: %3.0lf",
     "GPRINT:co2:AVERAGE:Avg\: %3.0lf",
     "GPRINT:co2:MAX:Max\: %3.0lf",
     "GPRINT:co2:MIN:Min\: %3.0lf \\r")

    ret = rrdtool.graph( imagesDir  + "foggers" + t + ".png", "--start", t,
     "DEF:foggers="+rrdDir+"foggers.rrd:foggers:AVERAGE",
     "AREA:foggers#00FF00",
     "GPRINT:foggers:LAST:Foggers Current\: %3.0lf",
     "GPRINT:foggers:AVERAGE:Avg\: %3.0lf",
     "GPRINT:foggers:MAX:Max\: %3.0lf",
     "GPRINT:foggers:MIN:Min\: %3.0lf \\r")

    ret = rrdtool.graph( imagesDir  + "fan" + t + ".png", "--start", t,
     "DEF:fan="+rrdDir+"fan.rrd:fan:AVERAGE",
     "AREA:fan#00FF00",
     "GPRINT:fan:LAST:Fan Current\: %3.0lf",
     "GPRINT:fan:AVERAGE:Avg\: %3.0lf",
     "GPRINT:fan:MAX:Max\: %3.0lf",
     "GPRINT:fan:MIN:Min\: %3.0lf \\r")

def writeLastRun():
  try:
    with open("/home/pi/mushroomPi/lastRun","w") as file:
      file.write(time.strftime("%c")+"\n")
      file.write('<div><b>Last Poll:</b> '+json.dumps(lastPoll)+'</div>')
      file.close()
  except IOError as e:
    error("Can not write lastRun file: " + e.strerror )

def error(message):
  sys.stderr.write("[" + time.strftime("%c") + "] ERROR: " + message + "\n")

def debug(level,message):
  if commandLineArgs.debug >= level :
    sys.stderr.write("[" + time.strftime("%c") + "] DEBUG: " + message + "\n")

#
# Begin the main loop
#

#
# parse the command line arguments
#
parser = argparse.ArgumentParser(description='Run the farm.')
parser.add_argument('-d','--debug',help='turn on debugging. Max level: 3',action='count')
global commandLineArgs
commandLineArgs = parser.parse_args()

#
# Open the serial to the arduino
#
ser = serial.Serial('/dev/ttyAMA0', 115200, timeout=2)
ser.open()
ser.write("\n")

#
# Run in an infinite loop
#
last_run_time = 0
while 1:
  # Poll every loop because control might need the data
  poll()

  # Only write data/graphs every 5 mins because the RRD expects a 300 second interval
  if time.time() - last_run_time > 300:
    getOutside()
    last_run_time = time.time()
    processGraphs()

  # run control routines
  processControl()

  # mark last run for web interface to show it is working
  writeLastRun()

  # sleep for a second to not clobber the CPU
  time.sleep(1)

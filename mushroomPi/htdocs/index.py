#!/usr/bin/python

import subprocess
import cgi
import sys
from datetime import timedelta
sys.path.append('..')
import parseConfig

lastRun = '../lastRun'

def uptime():
  uptime = subprocess.Popen('uptime', stdout=subprocess.PIPE)
  return uptime.stdout.read()

def readLastRun():
  try:
    with open(lastRun, "r") as file:
      return file.read()
  except IOError as e:
    return 'Not running!!!'

#
# Main
#
print "Content-type: text/html"
print

configDict = parseConfig.parse()

print """
<html>
  <head>
    <title>Mushroom Farm Control</title>
  </head>
  <body style="margin: 20px;">
    <div style="text-align: right;">
        <a href="shutdown.py">Shutdown Pi</a>
    </div>
    <div style="font-size: 24px; font-weight: bold; margin-bottom: 10px;">
      Mushroom Farm Control
    </div>

    <div style="margin-bottom: 10px; margin-left: 40px;">
      <b>Last mushControl.pl check:</b>
"""
print readLastRun()

print """
      <b>System uptime:</b>
"""
print uptime()

print """
    </div>
"""

print '<form action="/config.py" method="POST">'

print '<div style="float: left; width: 460px;">'
print '<input type="radio" id="manCtrl" name="control" value="manual"'
if configDict.get('control','manual') == 'manual':
  print ' checked="true"'
print '>'
print '<label for="manCtrl" style="font-weight: bold;">Manual Control</label>'
print '<div style="margin: 20px;">'
print '<div style="margin-bottom: 5px;">Turn on <input type="text" name="manualFoggers" size="2" value="' + configDict.get('manualFoggers') + '"> foggers</div>'
print '<div>Set fan to <input type="text" name="manualFan" size="3" value="' + configDict.get('manualFan') + '"> percent</div>'
print '</div>'
print '</div>'

print '<div style="float: left; width: 460px;">'
print '<input type="radio" id="autoCtrl" name="control" value="auto"'
if configDict.get('control') == 'auto':
  print ' checked="true"'
print '>'
print '<label for="autoCtrl" style="font-weight: bold;">Automatic Control</label>'
print '<div style="margin: 20px;">'
print '<div style="margin-bottom: 5px;">If humidity below <input type="text" name="autoHumidity" size="3" value="' + configDict.get('autoHumidity') + '"> turn on <input type="text" name="autoFoggers" size="2" value="' + configDict.get('autoFoggers') + '"> foggers</div>'
print '<div style="">If CO2 above <input type="text" name="autoCO2" size="3" value="' + configDict.get('autoCO2') + '"> set fan to <input type="text" name="autoFan" size="2" value="' + configDict.get('autoFan') + '"> percent</div>'
print '</div>'
print '</div>'

print '<div style="clear: both;">'

print '<div style="padding-bottom: 10px; margin-bottom: 10px; border-bottom: 1px dashed #CCCCCC;"><input type="submit" value="Save Settings"></div>'

print """
    <div style="font-size: 24px; font-weight: bold; margin-bottom: 20px;">
      Mushroom Farm Status
    </div>

    <div style="float: left; width: 500px;">
      <b>Indoor Temperature</b>
      <a href="/details.py?graph=temperature&title=Indoor Temperature"><img src="/images/temperature-8h.png"></a>
    </div>

    <div style="float: left; width: 500px;">
      <b>Outdoor Temperature And Humidity</b>
      <a href="/details.py?graph=outsideTemp&title=Outdoor Temperature And Humidity"><img src="/images/outsideTemp-8h.png"></a>
    </div>
    <div style="clear:both;">

    <div style="float: left; width: 500px; margin-top: 20px;">
      <b>Indoor Humidity</b>
      <a href="/details.py?graph=humidity&title=Indoor Humidity"><img src="/images/humidity-8h.png"></a>
    </div>

    <div style="float: left; width: 500px; margin-top: 20px;">
      <b>Number of Foggers</b>
      <a href="/details.py?graph=foggers&title=Number of Foggers"><img src="/images/foggers-8h.png"></a>
    </div>

    <div style="float: left; width: 500px; margin-top: 20px;">
      <b>CO2 Level</b>
      <a href="/details.py?graph=co2&title=CO2 Level"><img src="/images/co2-8h.png"></a>
    </div>

    <div style="float: left; width: 500px; margin-top: 20px;">
      <b>Fan Speed Percentage</b>
      <a href="/details.py?graph=fan&title=Fan Speed Percentage"><img src="/images/fan-8h.png"></a>
    </div>

    <div style="clear:both;">

  </body>
</html>
"""

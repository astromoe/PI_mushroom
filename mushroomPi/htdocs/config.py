#!/usr/bin/python

import sys
import cgi
import pprint
params = cgi.FieldStorage()

print "Content-type: text/html"
print # to end the CGI response headers.

if params.getvalue('control'):
  # Write the settings to the config file
  file = open("../config", "w")
  file.write( 'control:'        + params.getvalue('control')        + "\n");
  file.write( 'manualFoggers:'  + params.getvalue('manualFoggers')  + "\n");
  file.write( 'manualFan:'      + params.getvalue('manualFan')      + "\n");
  file.write( 'autoHumidity:'   + params.getvalue('autoHumidity')   + "\n");
  file.write( 'autoFoggers:'    + params.getvalue('autoFoggers')    + "\n");
  file.write( 'autoCO2:'        + params.getvalue('autoCO2')        + "\n");
  file.write( 'autoFan:'        + params.getvalue('autoFan')        + "\n");
  file.close()

  print 'Settings saved! This may take a few seconds to be changed on the farm.<br><br><a href="/">Return to Control/Status page</a>'

else:
  print "No form submitted";

#!/usr/bin/python

import cgi
params = cgi.FieldStorage()

times = ['-8h','-2d','-1w','-1m','-1y']
name  = {'-8h':'Last 8 Hours','-2d':'Last 2 days','-1w':'Last Week','-1m':'Last Month','-1y':'Last Year'}

print "Content-type: text/html"

print

print """
<html>
  <head>
    <title>Mushroom Farm - Details</title>
  </head>
  <body style="margin: 20px;">
"""

print '<div style="margin-bottom: 20px; font-weight: bold; font-size: 24px;">' + params.getvalue("title") + '</div>'

count = 0
for time in times:
  count += 1
  print '<div style="float: left; width: 500px;"><b>' + name[time] + '</b><br>'
  print '<img src="/images/' + params.getvalue("graph") + time + '.png">'
  print '</div>'
  if count % 2 == 0:
    count = 0
    print '<div style="clear: both"></div>'

print """
  </body>
</html>
"""


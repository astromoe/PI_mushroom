#!/usr/bin/env python

from subprocess import call
call(["/usr/bin/sudo","/sbin/shutdown", "-h", "now"])

print "Content-type: text/html\n\n"
print "<h1>Goodbye cruel world</h1>"

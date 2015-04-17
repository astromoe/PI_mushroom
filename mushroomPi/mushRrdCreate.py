#!/usr/bin/python

import sys
import rrdtool

rrdDir = "rrd/"

ret = rrdtool.create(rrdDir+"outsideTemp.rrd", "--step", "300", "--start", '0',
 "DS:temperature:GAUGE:600:-50:150",
 "DS:humidity:GAUGE:600:0:100",
 "RRA:AVERAGE:0.5:1:600",
 "RRA:AVERAGE:0.5:6:700",
 "RRA:AVERAGE:0.5:24:775",
 "RRA:AVERAGE:0.5:288:797")

if ret:
 print rrdtool.error()

ret = rrdtool.create(rrdDir+"temperature.rrd", "--step", "300", "--start", '0',
 "DS:temperature:GAUGE:600:U:U",
 "RRA:AVERAGE:0.5:1:600",
 "RRA:AVERAGE:0.5:6:700",
 "RRA:AVERAGE:0.5:24:775",
 "RRA:AVERAGE:0.5:288:797")

if ret:
 print rrdtool.error()

ret = rrdtool.create(rrdDir+"humidity.rrd", "--step", "300", "--start", '0',
 "DS:humidity:GAUGE:600:0:100",
 "RRA:AVERAGE:0.5:1:600",
 "RRA:AVERAGE:0.5:6:700",
 "RRA:AVERAGE:0.5:24:775",
 "RRA:AVERAGE:0.5:288:797")

if ret:
 print rrdtool.error()

ret = rrdtool.create(rrdDir+"co2.rrd", "--step", "300", "--start", '0',
 "DS:co2:GAUGE:600:U:U",
 "RRA:AVERAGE:0.5:1:600",
 "RRA:AVERAGE:0.5:6:700",
 "RRA:AVERAGE:0.5:24:775",
 "RRA:AVERAGE:0.5:288:797")

if ret:
 print rrdtool.error()

ret = rrdtool.create(rrdDir+"foggers.rrd", "--step", "300", "--start", '0',
 "DS:foggers:GAUGE:600:0:10",
 "RRA:AVERAGE:0.5:1:600",
 "RRA:AVERAGE:0.5:6:700",
 "RRA:AVERAGE:0.5:24:775",
 "RRA:AVERAGE:0.5:288:797")

if ret:
 print rrdtool.error()

ret = rrdtool.create(rrdDir+"fan.rrd", "--step", "300", "--start", '0',
 "DS:fan:GAUGE:600:0:100",
 "RRA:AVERAGE:0.5:1:600",
 "RRA:AVERAGE:0.5:6:700",
 "RRA:AVERAGE:0.5:24:775",
 "RRA:AVERAGE:0.5:288:797")

if ret:
 print rrdtool.error()


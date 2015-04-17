#!/usr/bin/python

import os
import time

config = os.path.dirname(__file__) + '/config'

defaultDict = {
  'control':        'manual',
  'manualFan':      '50',
  'manualFoggers':  '5',
  'autoFan':        '100',
  'autoFoggers':    '10',
  'autoHumidity':   '85',
  'autoCO2':        '30000'
}

lastConfigDict = None
lastRead = None

def parse():
  global lastRead
  global lastConfigDict

  # Check if the config file has changed since we last read
  # or if it doesn't exist
  reread = None
  try:
    stat = os.stat(config)
    if stat.st_mtime > lastRead:
      reread = 1
  except OSError as e:
    reread = 1

  if reread:
    lastRead = time.time()
    try:
      with open(config, "r") as file:
        configDict = {}
        for line in file:
          line = line.rstrip()
          parts = line.split(':')
          if parts[0]:
            configDict[parts[0]] = parts[1]
        file.close()
        if configDict.get('control') is None:
          lastConfigDict = writeDefault()
        else:
          lastConfigDict = configDict
        return lastConfigDict
    except IOError as e:
      lastConfigDict = writeDefault()
      return lastConfigDict
  else:
    return lastConfigDict

def writeDefault():
  # No config so create the default
  try:
    with open(config,"w") as file:
      for key, value in defaultDict.iteritems():
        file.write(key+':'+value+'\n')
      file.close()
      try:
        os.chmod(config,0777)
      except:
        pass
      return defaultDict
  except IOError as e:
    raise Exception('Can not write config file')

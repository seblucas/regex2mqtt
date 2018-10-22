#!/usr/bin/env python3
#
#  regex2mqtt.py
#
#  Copyright 2016 Sébastien Lucas <sebastien@slucas.fr>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.csv
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#


import os, re, time, json, argparse, sys
import paho.mqtt.publish as publish # pip install paho-mqtt
from datetime import datetime

verbose = False

def debug(msg):
  if verbose:
    print (msg + "\n")

def str2float(input):
  return float(input.replace(',', '.'))
    
def parseString(regexString, input):
  tstamp = int(time.time())
  debug ("Trying to parse this {0}".format(input))
  reg = re.compile(regexString)
  matches = reg.search(input)
  if matches is None:
    return (False, {"time": tstamp, "message": "no match found"})
  readingTime = int(time.mktime(datetime.strptime(
    matches.group('day') + '/' + matches.group('month') + '/' + matches.group('year') + ' ' + 
    matches.group('hour') + ':' + matches.group('minute'), '%d/%m/%Y %H:%M').timetuple()))
  newObject = {"time": readingTime, "temp": str2float(matches.group('temperature')),
                                    "hum": int(str2float(matches.group('humidity'))),
                                    "pres": str2float(matches.group('airpressure'))}
  return (True, newObject)


parser = argparse.ArgumentParser(description='Read current air pressure, temperature and humidity from any parsable source and send them to a MQTT broker.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-m', '--mqtt-host', dest='host', action="store", default="127.0.0.1",
                   help='Specify the MQTT host to connect to.')
parser.add_argument('-r', '--regex', dest='regex', action="store", required=True,
                   help='Specify the regular expression query with named groups to use (check the documentation).')
parser.add_argument('-n', '--dry-run', dest='dryRun', action="store_true", default=False,
                   help='No data will be sent to the MQTT broker.')
parser.add_argument('-o', '--last-time', dest='previousFilename', action="store", default="/tmp/regex_last",
                   help='The file where the last timestamp coming from the source will be saved')
parser.add_argument('-t', '--topic', dest='topic', action="store", default="sensor/regex",
                   help='The MQTT topic on which to publish the message (if it was a success).')
parser.add_argument('-T', '--topic-error', dest='topicError', action="store", default="error/sensor/regex", metavar="TOPIC",
                   help='The MQTT topic on which to publish the message (if it wasn\'t a success).')
parser.add_argument('-v', '--verbose', dest='verbose', action="store_true", default=False,
                   help='Enable debug messages.')


args = parser.parse_args()
verbose = args.verbose

standardInput = sys.stdin.read()

status, data = parseString(args.regex, standardInput)
jsonString = json.dumps(data)
if status:
  debug("Success with message <{0}>".format(jsonString))
  if os.path.isfile(args.previousFilename):
    oldTimestamp = open(args.previousFilename).read(10);
    if int(oldTimestamp) >= data["time"]:
      print ("No new data found")
      exit(0)

  # save the last timestamp in a file
  with open(args.previousFilename, 'w') as f:
    f.write(str(data["time"]))
  if not args.dryRun:
    publish.single(args.topic, jsonString, hostname=args.host)
else:
  debug("Failure with message <{0}>".format(jsonString))
  if not args.dryRun:
    publish.single(args.topicError, jsonString, hostname=args.host)


# regex2mqtt

Get data from a parsable string using a regular expression and send it to your MQTT broker 

# Why ?

I did not find anything as simple as this so I had to build it with python.

# Usage

## Prerequisite

You simply need Python3 (never tested with Python2.7) and the only dependency is `paho-mqtt` (for MQTT broker interaction) so this line should be enough  :

```bash
pip3 install paho-mqtt
```

## Using the script

Easy, first try a dry-run command :

```bash
cat mydata.txt | ./regex2mqtt.py -r "<MY REGEX>" -n -v
```

and then a real command to add to your crontab :

```bash
cat mydata.txt | ./regex2mqtt.py -r "<MY REGEX>"
```

As you can see the string to parse is read from `stdin` so you can also use it with `curl`, `wget` or any other tool to access the resources wherever it is.

## Help

```bash
/ # regex2mqtt.py --help
usage: regex2mqtt.py [-h] [-m HOST] -r REGEX [-n] [-o PREVIOUSFILENAME]
                     [-t TOPIC] [-T TOPIC] [-v]

Read current air pressure, temperature and humidity from any parsable source
and send them to a MQTT broker.

optional arguments:
  -h, --help            show this help message and exit
  -m HOST, --mqtt-host HOST
                        Specify the MQTT host to connect to. (default:
                        127.0.0.1)
  -r REGEX, --regex REGEX
                        Specify the regular expression query with named groups
                        to use (check the documentation). (default: None)
  -n, --dry-run         No data will be sent to the MQTT broker. (default:
                        False)
  -o PREVIOUSFILENAME, --last-time PREVIOUSFILENAME
                        The file where the last timestamp coming from the
                        source will be saved (default: /tmp/regex_last)
  -t TOPIC, --topic TOPIC
                        The MQTT topic on which to publish the message (if it
                        was a success). (default: sensor/regex)
  -T TOPIC, --topic-error TOPIC
                        The MQTT topic on which to publish the message (if it
                        wasn't a success). (default: error/sensor/regex)
  -v, --verbose         Enable debug messages. (default: False)
```

## Named groups / Regular expression

The genericity of this tool comes from the usage of named groups, so you have to use these names :

 * day
 * month
 * year
 * hour
 * minute
 * temperature
 * humidity
 * airpressure

 So if you want to extract data from an european CSV (so with `;` as a separator) you can use :

 ```
 ^(?P<day>\d{2})/(?P<month>\d{2})/(?P<year>\d{4});(?P<hour>\d{2})h(?P<minute>\d{2});(?P<temperature>.*?);(?P<humidity>.*?);.*?;.*?;.*?;(?P<airpressure>.*?);
 ```

 It will work with that string for example : 

 ```
 25/02/2017;17h49;8,9;77;8,9;6,7;5,0;1015,1;11;SW;221
 ```


## Other things to know

I personaly use cron to start this program so as I want to keep the latest timestamp received from the API, I store it by default in `/tmp/regex_last` (you can change it through a command line parameter).

## Docker

I added a sample Dockerfile, I personaly use it with a `docker-compose.yml` like this one :

```yml
version: '3'

services:
  regex:
    build: https://github.com/seblucas/regex2mqtt.git
    image: regex2mqtt-python3-cron:latest
    restart: always
    environment:
      REGEX_STRING: >-
        ^(?P<day>\d{2})/(?P<month>\d{2})/(?P<year>\d{4})#(?P<hour>\d{2})h(?P<minute>\d{2})#(?P<temperature>.*?)#(?P<humidity>.*?)#.*?#.*?#.*?#(?P<airpressure>.*?)#
      CRON_STRINGS: >-
        09 * * * * wget -qO- https://api.mysite.com | regex2mqtt.py -m localhost -r "$$REGEX_STRING" -v
      CRON_LOG_LEVEL: 8
```

As you can see, I prefer to store my regular expression in a separate environment variable to avoid any string interpolation / mismatch afterward.

# Limits

None, I hope at least ;). 

# License

This program is licenced with GNU GENERAL PUBLIC LICENSE version 2 by Free Software Foundation, Inc.

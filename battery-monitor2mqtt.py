#!/usr/bin/python3
# battery-monitor2mqtt - simple MQTT publishing of computer battery status
#
# Written and (C) 2018 by Lubomir Kamensky <lubomir.kamensky@gmail.com>
# Provided under the terms of the MIT license
#
# Requires:
# - Eclipse Paho for Python - http://www.eclipse.org/paho/clients/python/
#

import argparse
import logging
import logging.handlers
import time
import paho.mqtt.client as mqtt
import sys
import signal
import os
import subprocess
    
parser = argparse.ArgumentParser(description='Bridge between JSON file and MQTT')
parser.add_argument('--mqtt-host', default='localhost', help='MQTT server address. \
                     Defaults to "localhost"')
parser.add_argument('--mqtt-port', default='1883', type=int, help='MQTT server port. \
                    Defaults to 1883')
parser.add_argument('--mqtt-topic', default='json', help='Topic prefix to be used for \
                    subscribing/publishing. Defaults to "modbus/"')
parser.add_argument('--frequency', default='3', help='How often is the battery \
                    checked for the changes, in seconds. Only integers. Defaults to 1')

args=parser.parse_args()

logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

topic=args.mqtt_topic
if not topic.endswith("/"):
    topic+="/"
topic+="battery/"
frequency=int(args.frequency)

def signal_handler(signal, frame):
        print('Exiting ' + sys.argv[0])
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

lastValue = {}

class BatteryMonitor:
    raw_battery_info = ''
    processed_battery_info = {}
    remainingFlag = True

    def __init__(self):
        self.raw_battery_info = self.get_raw_battery_info()
        self.get_processed_battery_info()
        self.on_ac_power = subprocess.call(['on_ac_power'])

    def get_raw_battery_info(self):
        command = "acpi -b"
        raw_info = subprocess.check_output(command,
                                           stderr=subprocess.PIPE,
                                           shell=True)
        return raw_info

    def get_processed_battery_info(self):
        in_list = (self.raw_battery_info.decode("utf-8", "strict").lower().strip('\n')
                   .split(": ", 1)[1].split(", "))

        self.processed_battery_info["state"] = in_list[0]
        self.processed_battery_info["percentage"] = in_list[1]
        try:
            self.processed_battery_info["remaining"] = in_list[2]
        except Exception as exc:
            self.remainingFlag = False

        return self.processed_battery_info

class Element:
    def __init__(self,row):
        self.topic=row[0]
        self.value=row[1]

    def publish(self):
        try:
            if self.value!=lastValue.get(self.topic,0):
                lastValue[self.topic] = self.value
                fulltopic=topic+self.topic
                logging.info("Publishing " + fulltopic)
                mqc.publish(fulltopic,self.value,qos=0,retain=False)

        except Exception as exc:
            logging.error("Error reading "+self.topic+": %s", exc)

try:
    mqc=mqtt.Client()
    mqc.connect(args.mqtt_host,args.mqtt_port,10)
    mqc.loop_start()

    while True:
        monitor = BatteryMonitor()
        data = [("state",monitor.processed_battery_info["state"]),
                ("percentage",monitor.processed_battery_info["percentage"])]
        if monitor.remainingFlag:
            data.append(("remaining",monitor.processed_battery_info["remaining"]))
        if monitor.on_ac_power:
            data.append(("on_ac_power",monitor.on_ac_power))    
        elements=[]

        for row in data:
            e=Element(row)
            elements.append(e)

            for e in elements:
                e.publish()
        
        time.sleep(int(frequency))

except Exception as e:
    logging.error("Unhandled error [" + str(e) + "]")
    sys.exit(1)
    

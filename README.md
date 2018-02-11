battery-monitor2mqtt
=========
Simple MQTT publishing of computer battery status.


class BatteryMonitor is simpliefied version of the same class from project:
https://github.com/maateen/battery-monitor
by Maksudur Rahman Maateen

Dependencies
------------
sudo apt-get install acpi

* Eclipse Paho for Python - http://www.eclipse.org/paho/clients/python/


Command line options
--------------------
    usage: battery-monitor2mqtt.py [-h] [--mqtt-host MQTT_HOST]  [--mqtt-port MQTT_PORT]  [--mqtt-topic MQTT_TOPIC] [--frequency FREQUENCY ]
    
    optional arguments:
      -h, --help            show this help message and exit
      --mqtt-host MQTT_HOST
                            MQTT server address. Defaults to "localhost"
      --mqtt-port MQTT_PORT
                            MQTT server port. Defaults to 1883
      --mqtt-topic MQTT_TOPIC
                            Topic prefix to be used for subscribing/publishing.
                            Defaults to "json"
      --frequency FREQUENCY
                            How often is the battery status checked for the changes, in seconds. Only integers. Defaults to 3 


Example usage:
--------------
python3 battery-monitor2mqtt.py --mqtt-topic lubuntu


production usage with PM2:
--------------------------
PM2: https://www.npmjs.com/package/pm2

pm2 start /usr/bin/python3 --name "battery-monitor2mqtt" -- /home/luba/Git/battery-monitor2mqtt/battery-monitor2mqtt.py --mqtt-topic lubuntu

pm2 save


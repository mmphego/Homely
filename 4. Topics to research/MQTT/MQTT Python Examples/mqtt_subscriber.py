import paho.mqtt.client as mqtt
import logging

LOGGER = logging.getLogger(__name__)
Debug = True
#MQTT_host = 'localhost'
#MQTT_port = 1883
#MQTT_topic = 'lights/bedroom'

##MQTT_host = 'mqtt.dioty.co'
##MQTT_port = 1883
##MQTT_topic = '/mpho112@gmail.com/#'
##yourPassword = "d21475c0"
##yourUserName = 'mpho112@gmail.com'

MQTT_host = 'm12.cloudmqtt.com'
MQTT_port = 13103
MQTT_topic = 'owntracks/mpho112/golden'

yourPassword = "!nerd001"

yourUserName = 'mpho112'

def on_connect(mqtt, obj, rc):
    mqtt.subscribe(MQTT_topic)
    msg = ('Connected to: %s:%s' %(MQTT_host,MQTT_port))
    LOGGER.info(msg)
    if Debug:
        print msg

def on_subscribe(mqtt, obj, mid, granted_qos):
    msg = ('Subscribed to topic: %s' %MQTT_topic)
    LOGGER.info(msg)
    if Debug:
        print msg

def on_message(mqtt, obj, msg):
    LOGGER.info(msg.payload)
    if Debug:
        print msg.payload


client = mqtt.Client()
client.on_message = on_message
client.on_subscribe = on_subscribe
client.on_connect = on_connect

client.username_pw_set(yourUserName, yourPassword)
client.connect(MQTT_host, MQTT_port)
client.loop_forever()

import paho.mqtt.client as mqtt
import logging

LOGGER = logging.getLogger(__name__)
Debug = True
MQTT_host = 'localhost'
MQTT_port = 1883
MQTT_topic = 'lights/bedroom'
MQTT_message = 'Hello from mqtt'


def on_connect(client, userdata, rc):
    msg = ('Connected with result code: %s' %str(rc))
    LOGGER.info(msg)
    if Debug:
        print msg

def on_publish(client, userdata, mid):
    msg = ('Message published...')
    LOGGER.info(msg)
    if Debug:
        print msg

client = mqtt.Client()
client.on_publish = on_publish
client.on_connect = on_connect

client.connect(MQTT_host, MQTT_port)
client.publish(MQTT_topic, MQTT_message)
client.disconnect()

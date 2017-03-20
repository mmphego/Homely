import paho.mqtt.client as mqtt

# Define event callbacks

def on_connect(client, userdata, rc):
    if rc == 0:
         print("Connected successfully.")
    else:
         print("Connection failed. rc= "+str(rc))

def on_publish(client, userdata, mid):
    print("Message "+str(mid)+" published.")

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribe with mid "+str(mid)+" received.")

def on_message(client, userdata, msg):
    print("Message received on topic "+msg.topic+" with QoS "+str(msg.qos)+" and payload "+msg.payload)

mqttclient = mqtt.Client()

# Assign event callbacks
mqttclient.on_connect = on_connect
mqttclient.on_publish = on_publish
mqttclient.on_subscribe = on_subscribe
mqttclient.on_message = on_message

# Connect
yourPassword = "d21475c0"
yourRootTopic =  "/mpho112@gmail.com/#"
yourUserName = 'mpho112@gmail.com'
hostname = 'mqtt.dioty.co'
port = 1883
mqttclient.username_pw_set(yourUserName, yourPassword)
mqttclient.connect(hostname, port)

# Start subscription
mqttclient.subscribe(yourRootTopic)

# Publish a message
#mqttclient.publish(yourRootTopic, "Hello World Message!")

# Loop; exit on error
mqttclient.loop()


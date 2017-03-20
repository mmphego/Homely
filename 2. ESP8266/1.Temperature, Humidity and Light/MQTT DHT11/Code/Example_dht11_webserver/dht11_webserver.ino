#include <ESP8266WiFi.h>
//https://github.com/dancol90/ESP8266Ping
#include <ESP8266Ping.h>
#include <PubSubClient.h>
// http://osoyoo.com/wp-content/uploads/samplecode/DHT.zip
#include<dht.h>
// https://github.com/MajenkoLibraries/Average
#include <Average.h>
dht DHT;

// Connect to the WiFi
#define   ssid          "KATCPT"
#define   password      "katCPT#12"
#define   mqtt_server   "192.168.1.231"
// Testing broker
//const char* mqtt_server = "test.mosquitto.org";

// MQTT Topics
#define   mqtt_topic    "home/mainbedroom/temp"

// Define NodeMCU D5 pin to as temperature data pin of  DHT11
#define DHT11_PIN D5

Average<float> ave_temp(10);
Average<float> ave_hum(10);
int count = 0;
long lastMsg = 0;
char msg[50];
char message[58];

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  setup_WiFi();
  setup_MQTT();
  setup_DHT11();
}

void setup_DHT11(){
  DHT.read11(DHT11_PIN);
  }

void setup_WiFi(){
  // Connect to WiFi access point.
  delay(50);
  Serial.println();
  Serial.print("Connecting to WiFi access point: ");
  Serial.println(ssid);
  Serial.print("Connecting.");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  Serial.println();
}

void setup_MQTT(){
  delay(10);  
  Serial.print("Connecting to MQTT Server: ");
  Serial.println(mqtt_server);
  client.setServer(mqtt_server, 1883);
}

void reconnect() {
  Serial.println();
  Serial.print("Pinging MQTT BrokerIP: ");
  Serial.print(mqtt_server);
  
  if(Ping.ping(mqtt_server)){
    Serial.println(" Ok!!!");  
    // Loop until we're reconnected
    while (!client.connected()) {
      Serial.print("Attempting MQTT connection...");
      // Create a random client ID
      String clientId = "ESP8266Client-";
      clientId += String(random(0xffff), HEX);
      
      // Attempt to connect
      //if you MQTT broker has clientID,username and password
      //please change following line to    if (client.connect(clientId, userName, passWord))
      if (client.connect(clientId.c_str())){
        Serial.println("connected...");
        Serial.println("and subscribe to topic: ");
        Serial.print(mqtt_topic);
       //once connected to MQTT broker, subscribe command if any
        client.subscribe(mqtt_topic);
      } 
      else {
        Serial.print("failed, rc=");
        Serial.print(client.state());
        Serial.println(" try again in 5 seconds");
        // Wait 5 seconds before retrying
        delay(5000);
      }
    }
  } 
  else { 
    Serial.println();
    Serial.print(" Failed to establish a connection on MQTT Broker.");
    delay(10);
  }//end reconnect()
}

void loop() {
  if (!client.connected()) {
    reconnect();
  } 
  else if (WiFi.status() != 3) {
    Serial.println("WiFi disconnects, reconnecting.");
    delay(100);
    setup_WiFi();
  }
  
  client.loop();
  // sleep for 500ms
  delay(500);

  DHT.read11(DHT11_PIN);
  ave_temp.push(DHT.temperature);
  ave_hum.push(DHT.humidity);
  // calculate the average of samples
  for (int i = 0; i < 10; i++) {
      //Serial.print(ave_temp.get(i));
      ave_temp.get(i);
      //Serial.print(ave_hum.get(i));
      ave_hum.get(i);
  }

  count += 1;
  if (count > 10) {
      String msg = "Temperature: ";
      msg= msg + ave_temp.mean();
      msg = msg + " C ; Humidity: " ;
      msg= msg + ave_hum.mean() + "%";
      msg.toCharArray(message, 58);
      Serial.println(message);
      //publish sensor data to MQTT broker
      client.publish(mqtt_topic, message);
      count = 0;
   }
}

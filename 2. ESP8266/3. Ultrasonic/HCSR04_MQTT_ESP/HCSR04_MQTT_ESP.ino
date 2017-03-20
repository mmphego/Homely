#include <ESP8266WiFi.h>
//https://github.com/dancol90/ESP8266Ping
#include <ESP8266Ping.h>
#include <PubSubClient.h>
// https://github.com/MajenkoLibraries/Average
#include <Average.h>
#include<stdlib.h>

// Connect to the WiFi
#define   ssid_1          "KATCPT"
#define   password_1      "katCPT#12"
//#define   mqtt_server_1   "alexapi"
#define   mqtt_server_1   "192.168.1.232"
int mqtt_port = 1883;

// For Home
// #define   ssid_1          "GetUrOwnWiFi"
// #define   password_1      "Livhu300312"
// #define   mqtt_server_1   "192.168.1.9"
// Testing broker
//const char* mqtt_server_1 = "test.mosquitto.org";

// MQTT Topics
#define   mqtt_topic    "home/tvroom/tv_prox"

// Define NodeMCU D5 pin to as temperature data pin of  DHT11
#define   ECHO          D1
#define   TRIGGER       D2
#define   Statusled     D3
#define   WiFiLed       D5

// Define macros
#define Between(x, a, b)  (((a) <= (x)) && ((x) <= (b)))
#define Outside(x, a, b)  (((x) < (a)) || ((b) < (x)))
#define LessOrEqual(x, y) ((x) <= (y))
#define MoreOrEqual(x, y) ((x) >= (y))

// Variables

// Reserve space for 10 entries in the average bucket.
Average<float> ave_distance(10);

int Samples = 20;
int count = 0;
int sleep = 50;

int maximumRange = 200; // Maximum range
int minimumRange = 2; // Minimum range
float prohibitedDistance = 30.0; // Distance Alarm will be sounded

// long lastMsg = 0;
char msg[50];
char message[65];

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(115200);
  setup_GPIO();
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid_1, password_1);
  WiFi.softAPdisconnect(true);
  setup_WiFi();
  setup_MQTT();
}

void setup_GPIO(){
  pinMode(TRIGGER, OUTPUT);
  pinMode(ECHO, INPUT);
  pinMode(WiFiLed, OUTPUT);
  pinMode(Statusled, OUTPUT);
}

void setup_WiFi(){
  // Connect to WiFi access point.
  delay(50);
  Serial.println();
  Serial.print("Connecting to WiFi access point: ");
  Serial.println(ssid_1);
  Serial.print("Connecting.");
  while (WiFi.status() != WL_CONNECTED) {
    digitalWrite(WiFiLed, LOW);
    delay(250);
    digitalWrite(WiFiLed, HIGH);
    delay(250);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  digitalWrite(WiFiLed, HIGH);
  Serial.print("MAC Address: ");
  Serial.println(WiFi.macAddress());
  Serial.println();
}

void setup_MQTT(){
  delay(10);
  Serial.print("Connecting to MQTT Server: ");
  Serial.println(mqtt_server_1);
  client.setServer(mqtt_server_1, mqtt_port);
}

void reconnect() {
  Serial.println();
  Serial.print("Pinging MQTT BrokerIP: ");
  Serial.print(mqtt_server_1);

  if(Ping.ping(mqtt_server_1)){
    Serial.println(" Ok!!!");
    // Loop until we"re reconnected
    while (!client.connected()) {
      Serial.print("Attempting MQTT connection...");
      // Create a random client ID
      String clientId = "ESP8266Client-";
      clientId += String(random(0xffff), HEX);

      // Attempt to connect
      //if you MQTT broker has clientID,username and password_1
      //please change following line to    if (client.connect(clientId, userName, password_1))
      if (client.connect(clientId.c_str())){
        Serial.println("connected...");
        Serial.print("and subscribe to topic: ");
        Serial.println(mqtt_topic);
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
    Serial.print(":Failed to establish a connection on MQTT Broker.");
    delay(10);
  }//end reconnect()
}

float Proximity(){

  float duration, distance;
  digitalWrite(TRIGGER, LOW);
  delayMicroseconds(2);

  digitalWrite(TRIGGER, HIGH);
  delayMicroseconds(10);

  digitalWrite(TRIGGER, LOW);
  duration = pulseIn(ECHO, HIGH);
  //Serial.print(duration);
  distance = duration / 58.0;
  return distance;
}

// For Debug
// void loop(){
//   float raw_distance;
//   raw_distance = Proximity();
//   Serial.print("Raw distance: ");
//   Serial.println(raw_distance);
//   delay(1000);
// }

void loop() {
  delay(sleep);

  if (!client.connected()){
   reconnect();
  }
  else if(WiFi.status() != 3){
   Serial.println("WiFi Disconnects, reconnecting.");
   delay(100);
   setup_WiFi();
  }
  else{
    delayMicroseconds(1);
  }
  client.loop();
  float raw_distance, distance;
  raw_distance = Proximity();
  //Serial.print("Raw distance: ");
  //Serial.println(raw_distance);
  ave_distance.push(raw_distance);
  // calculate the average of samples
  for(int i = 0; i < Samples; i++){
    ave_distance.get(i);
  }
  count += 1;
  if(count > Samples){
    distance = ave_distance.mean();
    //Serial.print("Average Distance: ");
    //Serial.println(distance);

    if Between(distance, minimumRange, maximumRange){
    //if (distance >= maximumRange && distance <= minimumRange){
      //Serial.print(distance);
      //Serial.println(" Cm");
      String msg = "Distance (Cm): ";
      msg = msg + distance;
      msg.toCharArray(message, 65);
      Serial.println(message);
      client.publish(mqtt_topic, message);
    }

   if LessOrEqual(distance, prohibitedDistance){
      Serial.println("Alarm: You are too close!!!!");
      digitalWrite(Statusled, HIGH);
    }
   else{
      digitalWrite(Statusled, LOW);
    }
    count = 0;
  }
}

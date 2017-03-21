#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>
#include <ArduinoOTA.h>
//needed for library
#include <DNSServer.h>
#include <ESP8266WebServer.h>
//https://github.com/tzapu/WiFiManager
#include <WiFiManager.h>

//https://github.com/dancol90/ESP8266Ping
#include <ESP8266Ping.h>
#include <PubSubClient.h>
// http://osoyoo.com/wp-content/uploads/samplecode/DHT.zip
#include<dht.h>
// https://github.com/MajenkoLibraries/Average
#include <Average.h>
dht DHT;

#define   Hostname        "mainroom-temp-sensor"
#define   MasterPass      "ESP8266"

// MQTT 
#define   mqtt_topic    "home/mainbedroom/temp"
#define   mqtt_server_1   "alexapi"
#define   mqtt_server_1   "192.168.1.9"
// Testing broker
//const char* mqtt_server_1 = "test.mosquitto.org";

// Define NodeMCU D5 pin to as temperature data pin of  DHT11
#define   DHT11_PIN     D0
#define   Statusled     D1
#define   LDR           A0

// Define macros
#define Between(x, a, b)  (((a) <= (x)) && ((x) <= (b)))
#define Outside(x, a, b)  (((x) < (a)) || ((b) < (x)))
#define LessOrEqual(x, y) ((x) <= (y))
#define MoreOrEqual(x, y) ((x) >= (y))

// Variables
Average<float> ave_temp(10);
Average<float> ave_hum(10);
Average<float> ave_ldr(10);

int count = 0;
int wifi_reset = 0;
int Samples = 10;
int sensorValue = 0;
long lastMsg = 0;
char msg[50];
char message[65];

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(115200);
  pinMode(Statusled, OUTPUT);
  DHT.read11(DHT11_PIN);
  setup_OTA();
  setup_WiFi();
  setup_MQTT();
}

void setup_OTA() {
  // Port defaults to 8266
  ArduinoOTA.setPort(8266);
  // Hostname to Temp_Hum_Sensor-01
  ArduinoOTA.setHostname(Hostname);
  // Enable authentication
  ArduinoOTA.setPassword(MasterPass);
  //Sets if the device should be rebooted after successful update. 
  ArduinoOTA.setRebootOnSuccess(true);
  ArduinoOTA.onStart([]() {
    Serial.println("Start OTA");
  });
  ArduinoOTA.onEnd([]() {
    Serial.println("End OTA");
  });
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    Serial.printf("Progress: %u%%\n", (progress / (total / 100)));
  });

  ArduinoOTA.onError([](ota_error_t error) {
    Serial.printf("Error[%u]: ", error);
    if (error == OTA_AUTH_ERROR) Serial.println("Auth Failed");
    else if (error == OTA_BEGIN_ERROR) Serial.println("Begin Failed");
    else if (error == OTA_CONNECT_ERROR) Serial.println("Connect Failed");
    else if (error == OTA_RECEIVE_ERROR) Serial.println("Receive Failed");
    else if (error == OTA_END_ERROR) Serial.println("End Failed");
  });
  ArduinoOTA.begin();
}

void setup_WiFi() {
  // Connect to WiFi access point.
  WiFiManager wifiManager;
  Serial.print("WiFi Reset status: ");
  Serial.print(wifi_reset);
  if (wifi_reset == 1) {
    //reset settings - assign a button for this.
    wifiManager.resetSettings();
    wifi_reset = 0;
  }
  //sets timeout until configuration portal gets turned off
  //useful to make it all retry or go to sleep
  //in seconds
  wifiManager.setTimeout(180);
  // Connect to WiFi access point.
  if (!wifiManager.autoConnect(Hostname, MasterPass)) {
    Serial.println("failed to connect, we should reset as see if it connects");
    delay(3000);
    ESP.restart();
    delay(5000);
  }

  delay(50);
  Serial.println();
  Serial.print("Connecting to WiFi access point: ");
  //Serial.println(ssid_1);
  Serial.print("Connecting.");
  while (WiFi.status() != WL_CONNECTED) {
    digitalWrite(Statusled, HIGH);
    delay(50);
    digitalWrite(Statusled, LOW);
    delay(50);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  digitalWrite(Statusled, HIGH);
  Serial.print("MAC Address: ");
  Serial.println(WiFi.macAddress());
  Serial.println();
}

void setup_MQTT() {
  delay(10);
  Serial.print("Connecting to MQTT Server: ");
  Serial.println(mqtt_server_1);
  client.setServer(mqtt_server_1, 1883);
}

void reconnect() {
  Serial.println();
  Serial.print("Pinging MQTT BrokerIP: ");
  Serial.print(mqtt_server_1);

  if (Ping.ping(mqtt_server_1)) {
    Serial.println(" Ok!!!");
    // Loop until we're reconnected
    while (!client.connected()) {
      Serial.print("Attempting MQTT connection...");
      // Create a random client ID
      String clientId = "ESP8266Client-";
      clientId += String(random(0xffff), HEX);

      // Attempt to connect
      //if you MQTT broker has clientID,username and password_1
      //please change following line to    if (client.connect(clientId, userName, password_1))
      if (client.connect(clientId.c_str())) {
        //Serial.println(clientId.c_str());
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
  else if (WiFi.status() != 3) {
    Serial.println("");
    Serial.println("WiFi disconnects, reconnecting.");
    wifi_reset = 1;
    delay(1000);
    ESP.restart();
    delay(3000);
    Serial.print("WiFi Reset status: ");
    Serial.print(wifi_reset);
    setup_WiFi();
  }
  else {
    Serial.println();
    Serial.print(":Failed to establish a connection on MQTT Broker.");
    delay(1000);
    ESP.restart();
    delay(1000);
  }//end reconnect()
}

void loop() {
  ArduinoOTA.handle();
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  // sleep for 500ms
  delay(500);

  sensorValue = analogRead(LDR);
  //sSerial.println();
  //Serial.print("Sensor Value: ");
  //Serial.println(sensorValue);
  float voltage = sensorValue * (3.3 / 1023.0);
  //Serial.print("LDR Voltage: ");
  //Serial.println(voltage);

  DHT.read11(DHT11_PIN);
  ave_temp.push(DHT.temperature);
  ave_hum.push(DHT.humidity);
  ave_ldr.push(sensorValue);

  // calculate the average of samples
  for (int i = 0; i < Samples; i++) {
    //Serial.print(ave_temp.get(i));
    ave_temp.get(i);
    //Serial.print(ave_hum.get(i));
    ave_hum.get(i);
    //Serial.print(ave_ldr.get(i));
    ave_ldr.get(i);
  }

  count += 1;
  if (count > Samples) {
    String msg = "Temperature:";
    msg = msg + ave_temp.mean();
    msg = msg + ",Humidity:" ;
    msg = msg + ave_hum.mean();
    msg = msg + (",light:") + ave_ldr.mean();
    msg.toCharArray(message, 65);
    Serial.println(message);
    //publish sensor data to MQTT broker
    client.publish(mqtt_topic, message);
    count = 0;
  }
}


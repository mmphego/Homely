#include <EEPROM.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ESP8266Ping.h>

// Connect to the WiFi
//#define   ssid_1          "GetUrOwnWiFi"
//#define   password_1      "Livhu300312"
//#define   mqtt_server_1   "192.168.1.9"

#define   ssid_1          "KATCPT"
#define   password_1      "katCPT#12"
#define   mqtt_server_1   "alexapi"
// Testing broker
//const char* mqtt_server_1 = "test.mosquitto.org";

// MQTT Topics
#define   mqtt_topic    "home/mainbedroom/light"

// GPIO Pins
#define   ledPin          D5
#define   Statusled       D6
#define   PIRPin          D0

int counter = 0;
int previousReading = LOW;

byte mac[6];

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(115200);
  setup_GPIOs(); 
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid_1, password_1);
  WiFi.softAPdisconnect(true); 
  setup_WiFi();
  setup_MQTT();  
}


void setup_GPIOs(){
  // Setup GPIO pins
  pinMode(ledPin, OUTPUT);
  pinMode(Statusled, OUTPUT);
}


void setup_MQTT(){
  delay(10);  
  Serial.print("Connecting to MQTT Server: ");
  Serial.println(mqtt_server_1);
  client.setServer(mqtt_server_1, 1883);
  client.setCallback(callback);
}


void setup_WiFi(){
  // Connect to WiFi access point.
  delay(50);
  Serial.println();
  Serial.print("Connecting to WiFi access point: ");
  Serial.println(ssid_1);
  Serial.print("Connecting.");
  while (WiFi.status() != WL_CONNECTED) {
    digitalWrite(Statusled, LOW);  
    delay(250);       
    digitalWrite(Statusled, HIGH);      
    delay(250);       
    Serial.print(".");
  }
  Serial.println();
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  digitalWrite(Statusled, HIGH);
  Serial.println("Status LED ON"); 
  Serial.print("MAC Address: "); 
  Serial.println(WiFi.macAddress());     
  Serial.println();
}


void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived from topic [ ");
  Serial.print(topic);
  Serial.print(" ]: ");
  for (int i=0;  i<length; i++) {
    char receivedChar = (char)payload[i];
    Serial.print(receivedChar);
    if (receivedChar == '1'){
      client.publish(mqtt_topic, "LED ON");
      Serial.println(": LED ON");
      digitalWrite(ledPin, HIGH);      
    }else if (receivedChar == '0'){
        client.publish(mqtt_topic, "LED OFF");
        Serial.println(": LED OFF");
        digitalWrite(ledPin, LOW);      
    }
  }
  Serial.println();
}


void reconnectMQTT() {
  // Loop until we're reconnected
  Serial.println();
  Serial.print("Pinging MQTT BrokerIP: ");
  Serial.print(mqtt_server_1);
  
  if(Ping.ping(mqtt_server_1)){
    Serial.println(" Ok!!!");
    while (!client.connected()) {
      Serial.print("Attempting MQTT connection...");
    // Attempt to connect
      if (client.connect("ESP8266 Client")) {
        Serial.println("connected");
        Serial.print("... and subscribe to topic: ");
        Serial.println(mqtt_topic);
        client.subscribe(mqtt_topic);
      } else {
        Serial.print("failed, rc= ");
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
  }
}


void loop() {
  if (!client.connected()) {
    reconnectMQTT();
  } else if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnects, reconnecting.");
    delay(10);
    setup_WiFi();
  }
  client.loop();
  // delay to allow ESP8266 to rerun.
  int reading = digitalRead(PIRPin);
  Serial.println(reading);
  if (previousReading == LOW && reading == HIGH) {
    counter++;
    client.publish("outTopic", "Motion Detected");  
    Serial.print("Triggered ");
    Serial.print(counter);
    Serial.print("x Times! ");
    //delay(1000);

  }
  previousReading = reading;
  delay(10); 
}


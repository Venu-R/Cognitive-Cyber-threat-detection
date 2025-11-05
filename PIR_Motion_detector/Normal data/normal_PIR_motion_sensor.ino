#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoOTA.h>

// ====== WiFi ======
const char* ssid     = "Realme 8";      
const char* password = "qwertyuiop";  

// ====== Server ======
const char* serverName = "http://10.74.193.112:5001/pir"; // Flask endpoint for PIR logs

// ====== PIR ======
int pirPin = D5;       
int val = 0;           

// ====== Timing ======
unsigned long lastSendTime = 0;
const unsigned long sendInterval = 2000; // send every 1 second

void setup() {
  Serial.begin(115200);
  pinMode(pirPin, INPUT);

  // ====== Connect to WiFi ======
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  // ====== Setup OTA ======
  ArduinoOTA.setHostname("ESP12E_PIR");
  ArduinoOTA.begin();

  Serial.println("ESP12E PIR Spam Mode Started...");
}

void loop() {
  ArduinoOTA.handle();  // Check for OTA updates

  unsigned long now = millis();
  if (now - lastSendTime >= sendInterval) {
    val = digitalRead(pirPin);

    if (val == HIGH) {
      Serial.println("1"); // Motion detected
      sendToServer("1");
    } else {
      Serial.println("0"); // No motion
      sendToServer("0");
    }

    lastSendTime = now;
  }
}

// ====== Send PIR data to Flask server ======
void sendToServer(String motionStatus) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    WiFiClient client;

    http.begin(client, serverName);
    http.addHeader("Content-Type", "application/json");

    String jsonPayload = "{\"motion_detected\":\"" + motionStatus + "\"}";

    int httpResponseCode = http.POST(jsonPayload);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.print("Server Response: ");
      Serial.println(response);
    } else {
      Serial.print("Error sending POST: ");
      Serial.println(httpResponseCode);
    }

    http.end();
  } else {
    Serial.println("WiFi Disconnected");
  }
}

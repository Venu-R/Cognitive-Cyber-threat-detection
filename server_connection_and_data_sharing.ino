#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <DHT.h>

#define DHTPIN D4
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

const char* ssid = "Realme 8";
const char* password = "qwertyuiop";

// Replace with your laptop’s IP
const char* server = "http://10.79.169.112:5000/log";  

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("WiFi connected");
  dht.begin();
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;
    HTTPClient http;

    http.begin(client, server);
    http.addHeader("Content-Type", "application/json");

    float h = dht.readHumidity();
    float t = dht.readTemperature();

    String json = "{\"temperature\": " + String(t) + ", \"humidity\": " + String(h) + "}";

    int httpResponseCode = http.POST(json);
    Serial.println("Response: " + String(httpResponseCode));

    http.end();
  }
  delay(5000); // every 5s
}

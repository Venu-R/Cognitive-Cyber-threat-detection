#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

#define DHTPIN D2
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

const char* ssid = "Realme 8";
const char* password = "qwertyuiop";
const char* server = "http://10.34.221.112:5000/log";

// Configurable max queue size (adjust for your memory)
#define MAX_ERROR_QUEUE 20

struct ErrorLog {
  String error_type;
  unsigned long timestamp;
};

ErrorLog errorQueue[MAX_ERROR_QUEUE];
int errorQueueHead = 0;

void bufferError(const String &errType) {
  if (errorQueueHead < MAX_ERROR_QUEUE) {
    errorQueue[errorQueueHead].error_type = errType;
    errorQueue[errorQueueHead].timestamp = millis();
    errorQueueHead++;
  } else {
    Serial.println("Error buffer full; error lost!");
  }
}

void sendErrorToServer(const String &error_type, unsigned long error_time) {
  StaticJsonDocument<200> doc;
  doc["device_id"] = "weather_station_1";
  doc["temperature"] = -999;
  doc["humidity"] = -999;
  doc["status"] = "ERROR";
  doc["error_message"] = error_type;
  doc["timestamp"] = error_time;

  String jsonPayload;
  serializeJson(doc, jsonPayload);

  WiFiClient client;
  HTTPClient http;
  http.begin(client, server);
  http.addHeader("Content-Type", "application/json");
  int code = http.POST(jsonPayload);
  Serial.print("Buffered error log HTTP Response code: ");
  Serial.println(code);
  http.end();
}

void flushErrorQueue() {
  for (int i = 0; i < errorQueueHead; i++) {
    sendErrorToServer(errorQueue[i].error_type, errorQueue[i].timestamp);
    delay(100); // Small delay to avoid overwhelming the server
  }
  errorQueueHead = 0;
}

void setup() {
  Serial.begin(115200);
  dht.begin();
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Connected!");
}

void loop() {
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  String status = "OK";
  String error_message = "-";
  if (isnan(temperature) || isnan(humidity)) {
    status = "ERROR";
    error_message = "Sensor read fail";
    temperature = -999;
    humidity = -999;
  }

  StaticJsonDocument<300> doc;
  doc["device_id"] = "weather_station_1";
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  doc["status"] = status;
  doc["error_message"] = error_message;
  doc["timestamp"] = millis();

  String jsonPayload;
  serializeJson(doc, jsonPayload);

  if (WiFi.status() == WL_CONNECTED) {
    // If network is up, send all buffered error logs FIRST
    flushErrorQueue();

    // Now send the current reading (OK or error, depending on sensor)
    WiFiClient client;
    HTTPClient http;
    http.begin(client, server);
    http.addHeader("Content-Type", "application/json");
    int httpResponseCode = http.POST(jsonPayload);
    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);
    http.end();

    // If POST fails, buffer the error
    if ((httpResponseCode == -1) || (httpResponseCode == -11)) {
      Serial.println("Network fail, buffering error");
      bufferError("Network send fail");
    }
  } else {
    Serial.println("WiFi not connected! Cannot send data, buffering error.");
    bufferError("WiFi not connected");
  }

  delay(4000); // 4 seconds between readings and uploads
}

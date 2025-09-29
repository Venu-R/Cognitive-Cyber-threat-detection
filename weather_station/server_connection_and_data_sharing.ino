#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266mDNS.h>
#include <ArduinoOTA.h>
#include <DHT.h>
#include <time.h>

// DHT setup (as you requested)
#define DHTPIN D4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// WiFi / Server
const char* ssid = "Realme 8";
const char* password = "qwertyuiop";
const char* server = "http://10.68.44.112:5000/log";  

// Hostname for mDNS / OTA
const char* hostName = "esp-weather-01";

// NTP config (adjust timezone offsets as needed)
const long  gmtOffset_sec = 5 * 3600 + 30 * 60; // +05:30 for IST
const int   daylightOffset_sec = 0;

// Retry/backoff settings
const unsigned long WIFI_RECONNECT_INTERVAL_MS = 5000;
const unsigned long SEND_INTERVAL_MS = 5000;

unsigned long lastWifiAttempt = 0;
unsigned long lastSend = 0;

void setupWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED) {
    delay(150);
    Serial.print(".");
    // keep a simple timeout here to not hang forever (10s)
    if (millis() - start > 10000) break;
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.print("WiFi connected, IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println();
    Serial.println("WiFi connect attempt timed out (will retry in loop).");
  }
}

String getIsoTimestamp() {
  time_t now = time(nullptr);
  if (now <= 1000) {
    // time not set yet
    return String(millis()); // fallback to uptime ms
  }
  struct tm timeinfo;
  gmtime_r(&now, &timeinfo);
  char buf[30];
  // Format as e.g. 2025-09-27T19:20:30Z (UTC). Adjust if you want local time.
  strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%SZ", &timeinfo);
  return String(buf);
}

void setupOTA() {
  // Optional: set password with ArduinoOTA.setPassword("yourpw");
  ArduinoOTA.setHostname(hostName);

  ArduinoOTA.onStart([]() {
    Serial.println("OTA: Start");
  });
  ArduinoOTA.onEnd([]() {
    Serial.println("\nOTA: End");
  });
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    Serial.printf("OTA Progress: %u%%\r", (progress / (total / 100)));
  });
  ArduinoOTA.onError([](ota_error_t error) {
    Serial.printf("OTA Error[%u]: ", error);
    if (error == OTA_AUTH_ERROR) Serial.println("Auth Failed");
    else if (error == OTA_BEGIN_ERROR) Serial.println("Begin Failed");
    else if (error == OTA_CONNECT_ERROR) Serial.println("Connect Failed");
    else if (error == OTA_RECEIVE_ERROR) Serial.println("Receive Failed");
    else if (error == OTA_END_ERROR) Serial.println("End Failed");
  });

  ArduinoOTA.begin();
  Serial.println("OTA ready");
}

void setupTime() {
  configTime(gmtOffset_sec, daylightOffset_sec, "pool.ntp.org", "time.nist.gov");
  Serial.println("NTP init requested (may take a few seconds)...");
  // optionally wait a bit for time sync (non-blocking here)
}

void setup() {
  Serial.begin(115200);
  Serial.println();
  Serial.println("Starting ESP Weather Node");

  dht.begin();

  setupWiFi();

  // mDNS for easier OTA discovery
  if (MDNS.begin(hostName)) {
    Serial.println("mDNS responder started");
  } else {
    Serial.println("mDNS start failed");
  }

  setupOTA();
  setupTime();
}

void reconnectIfNeeded() {
  if (WiFi.status() == WL_CONNECTED) return;
  unsigned long now = millis();
  if (now - lastWifiAttempt < WIFI_RECONNECT_INTERVAL_MS) return;
  lastWifiAttempt = now;

  Serial.println("WiFi not connected. Attempting reconnect...");
  WiFi.disconnect();
  WiFi.begin(ssid, password);
  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < 8000) {
    delay(250);
    Serial.print(".");
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.print("Reconnected, IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println();
    Serial.println("Reconnect attempt failed.");
  }
}

void sendSensorData() {
  // Read DHT safely
  float h = dht.readHumidity();
  float t = dht.readTemperature(); // Celsius
  bool valid = true;
  if (isnan(h) || isnan(t)) {
    Serial.println("DHT read failed, skipping send.");
    valid = false;
  }

  if (!valid) return;

  // Build JSON
  String timestamp = getIsoTimestamp();
  String json = "{";
  json += "\"device_id\": \"" + String(hostName) + "\",";
  json += "\"timestamp\": \"" + timestamp + "\",";
  json += "\"temperature\": " + String(t, 2) + ",";
  json += "\"humidity\": " + String(h, 2);
  json += "}";

  Serial.println("Sending JSON: " + json);

  HTTPClient http;
  WiFiClient client;
  // begin with full URL (http://...)
  if (http.begin(client, server)) {
    http.addHeader("Content-Type", "application/json");
    int httpResponseCode = http.POST(json);
    if (httpResponseCode > 0) {
      String resp = http.getString();
      Serial.printf("HTTP %d, Response: %s\n", httpResponseCode, resp.c_str());
    } else {
      Serial.printf("HTTP POST failed, error: %s\n", http.errorToString(httpResponseCode).c_str());
    }
    http.end();
  } else {
    Serial.println("HTTP begin() failed");
  }
}

void loop() {
  // Handle OTA events always
  ArduinoOTA.handle();

  // Reconnect WiFi if dropped (non-blocking style)
  reconnectIfNeeded();

  // Send sensor data periodically
  unsigned long now = millis();
  if (now - lastSend >= SEND_INTERVAL_MS) {
    lastSend = now;
    if (WiFi.status() == WL_CONNECTED) {
      sendSensorData();
    } else {
      Serial.println("Not connected to WiFi — skipping data send.");
    }
  }

  // Let CPU breathe (small delay). Keep loop responsive to OTA/network.
  delay(10);
}

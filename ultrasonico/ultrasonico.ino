#include <WiFi.h>
#include <HTTPClient.h>
#include <math.h>
#include <WiFiUdp.h>

const char* ssid = "redeR";
const char* password = "--($_$)--";

const int trigPin = 14;
const int echoPin = 27;

const int ledPin = 33;

const int numReadings = 10;
//define sound speed in cm/uS
#define SOUND_SPEED 0.034
String macString = "";

void setup() {
  Serial.begin(115200); // Starts the serial communication
  
  pinMode(trigPin, OUTPUT); // Sets the trigPin as an Output
  pinMode(echoPin, INPUT); // Sets the echoPin as an Input

  pinMode(ledPin, OUTPUT);

  wifi_connect();

  uint8_t mac[6];
  WiFi.macAddress(mac);
  for (int i = 0; i < 6; i++) {
    if (mac[i] < 0x10) {
      macString += "0";
    }
    macString += String(mac[i], HEX);
  }
}

void wifi_connect(){
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    digitalWrite(ledPin, HIGH);
    delay(250);
    Serial.print(".");
    digitalWrite(ledPin, LOW);
    delay(250);
  }
  digitalWrite(ledPin, LOW);

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}


void loop() {
  float distanceCm = calculate_distance();
 
  Serial.print("Distance (cm): ");
  Serial.println(distanceCm);  
  Serial.println("");
  if (WiFi.status() == WL_CONNECTED) {
    send_message(distanceCm);
  }else {
    Serial.println("Erro na conexão WiFi");
  }
  delay(5000);
}

float calculate_distance(){
  long durations[numReadings];
  float total = 0.0;
  digitalWrite(ledPin, HIGH);

  for (int i = 0; i < numReadings; i++) {
    durations[i] = get_reading();
    total += durations[i];
    delay(1000);
  }
  float mean = total / numReadings;

  // Compute standard deviation
  float variance = 0.0;
  for (int i = 0; i < numReadings; i++) {
      variance += pow(durations[i] - mean, 2);
  }
  float stddev = sqrt(variance / numReadings);

  // Filter out values beyond 2 standard deviations
  float filteredTotal = 0.0;
  int count = 0;
  for (int i = 0; i < numReadings; i++) {
      if (fabs(durations[i] - mean) <= 2 * stddev) { // Within 2 standard deviations
          filteredTotal += durations[i];
          count++;
      }
  }

  // Compute the final average distance
  float average_duration = (count > 0) ? (filteredTotal / count) : mean; // Avoid division by zero
  digitalWrite(ledPin, LOW);
  return average_duration * SOUND_SPEED / 2; // Convert duration to distance
}


long get_reading(){
  // Clears the trigPin
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  // Sets the trigPin on HIGH state for 10 micro seconds
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  // Reads the echoPin, returns the sound wave travel time in microseconds
  long duration = pulseIn(echoPin, HIGH);
  Serial.println(duration * SOUND_SPEED / 2);
  return duration;
}


void send_message(float distancia){
  HTTPClient http;
  http.begin("http://192.168.102.88:81/leituras");
  http.addHeader("Content-Type", "application/json");
 
  String payload = "{\"distancia\": " + String(distancia) + 
                 ", \"latitude\": -16.67109000902933, \"longitude\": -49.23881052883575, \"mac\": \"" + 
                 macString + "\"}";

  Serial.println(payload);

  int httpResponseCode = http.POST(payload);

  if (httpResponseCode > 0) {
      Serial.print("Código de resposta HTTP: ");
      Serial.println(httpResponseCode);
    } else {
      Serial.print("Erro na requisição: ");
      Serial.println(httpResponseCode);
    }

    // Fecha a conexão HTTP
    http.end();
  
}




















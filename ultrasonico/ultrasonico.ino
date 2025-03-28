#include <WiFi.h>
#include <HTTPClient.h>
#include <NTPClient.h>
#include <math.h>
#include <WiFiUdp.h>

const char* ssid = "redeR";
const char* password = "--($_$)--";

const int trigPin = 14;
const int echoPin = 27;

const int numReadings = 10;
//define sound speed in cm/uS
#define SOUND_SPEED 0.034
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", 0, 3600000);

void setup() {
  Serial.begin(115200); // Starts the serial communication
  wifi_connect();
  pinMode(trigPin, OUTPUT); // Sets the trigPin as an Output
  pinMode(echoPin, INPUT); // Sets the echoPin as an Input
  timeClient.begin();
}

void wifi_connect(){
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

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
  http.begin("http://192.168.205.88:81/");
  http.addHeader("Content-Type", "application/json");
 
  timeClient.update();
  String horario = timeClient.getFormattedTime();
  String payload = "{\"distancia\": " + String(distancia) + ", \"horario\": \""+ String(horario) + "\", \"latitude\": 12.345, \"longitude\": 67.890}";
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




















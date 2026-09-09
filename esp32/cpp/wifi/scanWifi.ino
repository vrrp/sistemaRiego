#include "WiFi.h"

void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_STA); // Configurar en modo Estación
  WiFi.disconnect();
  delay(100);
}

void loop() {
  Serial.println("Iniciando escaneo Wi-Fi...");
  int n = WiFi.scanNetworks();
  
  if (n == 0) {
    Serial.println("No se encontraron redes.");
  } else {
    Serial.print(n);
    Serial.println(" redes encontradas:");
    for (int i = 0; i < n; ++i) {
      Serial.print(i + 1);
      Serial.print(": ");
      Serial.print(WiFi.SSID(i));
      Serial.print(" (");
      Serial.print(WiFi.RSSI(i));
      Serial.println(" dBm)");
      delay(10);
    }
  }
  Serial.println("-----------------------");
  delay(5000);
}


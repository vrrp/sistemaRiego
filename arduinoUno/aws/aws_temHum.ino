#include <SPI.h>
#include <SD.h>
#include <DHT.h>

// Configuración del DHT22
#define DHTPIN 2
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

// Configuración de la MicroSD
const int chipSelect = 4;

// Control de tiempo por software (Medición cada hora)
unsigned long tiempoAnterior = 0;
const unsigned long intervaloHora = 3600000UL; // 1 hora en milisegundos
int horasTranscurridas = 0; // Registro de tiempo simulado

void setup() {
  Serial.begin(9600);
  dht.begin();

  Serial.print("Iniciando tarjeta SD...");
  if (!SD.begin(chipSelect)) {
    Serial.println("Error: Fallo en la inicializacion de la MicroSD.");
    return;
  }
  Serial.println("MicroSD lista.");

  // Crear encabezado en el archivo si es nuevo
  File dataFile = SD.open("log.txt", FILE_WRITE);
  if (dataFile) {
    dataFile.println("--- Nueva Sesion de Monitoreo ---");
    dataFile.println("Tiempo(Horas),Temperatura(C),Humedad(%)");
    dataFile.close();
  }
  
  // Realizar una primera medición al encender
  registrarDatos();
}

void loop() {
  unsigned long tiempoActual = millis();

  // Verifica si ha pasado una hora
  if (tiempoActual - tiempoAnterior >= intervaloHora) {
    tiempoAnterior = tiempoActual;
    horasTranscurridas++;
    registrarDatos();
  }
}

void registrarDatos() {
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  if (isnan(h) || isnan(t)) {
    Serial.println("Error al leer el sensor DHT22");
    return;
  }

  // Abrir archivo en la MicroSD
  File dataFile = SD.open("log.txt", FILE_WRITE);

  if (dataFile) {
    // Grabar en la MicroSD en formato CSV (Separado por comas)
    dataFile.print(horasTranscurridas);
    dataFile.print(",");
    dataFile.print(t);
    dataFile.print(",");
    dataFile.println(h);
    dataFile.close(); // Siempre cerrar el archivo al terminar

    // Mostrar también en el monitor serie para validar
    Serial.print("Guardado - Hora: ");
    Serial.print(horasTranscurridas);
    Serial.print(" | Temp: ");
    Serial.print(t);
    Serial.print(" C | Hum: ");
    Serial.print(h);
    Serial.println(" %");
  } else {
    Serial.println("Error al abrir el archivo log.txt");
  }
}
        
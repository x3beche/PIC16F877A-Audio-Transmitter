#include <WiFi.h>

void setup()
{
  // Start the serial communication
  Serial.begin(115200);

  // Wait for the serial communication to be established
  while (!Serial)
  {
    delay(10);
  }

  // Get the MAC address
  String macAddress = WiFi.macAddress();

  // Print the MAC address to the Serial Monitor
  Serial.print("MAC Address: ");
  Serial.println(macAddress);
}

void loop()
{
  // Empty loop
}


#include <Arduino.h>
#include <WiFi.h>
#include <esp_wifi.h>
#include <QuickEspNow.h>
#include <HardwareSerial.h>

// MAC addresses for communication
// MIC TX MAC = 40:22:D8:04:49:98
// HOP RX MAC = E8:DB:84:12:55:F0
static uint8_t hop_rx_mac[] = {0xE8, 0xDB, 0x84, 0x12, 0x55, 0xF0};
static uint8_t mic_tx_mac[] = {0x40, 0x22, 0xD8, 0x04, 0x49, 0x98};

// Initialize a HardwareSerial object for serial communication on UART2
HardwareSerial SerialPort(2);

// Callback function to handle received data
void dataReceived(uint8_t *address, uint8_t *data, uint8_t len, signed int rssi, bool broadcast)
{
  // Write the received data to the serial port
  Serial.write(data, len);
}

void setup()
{
  // Initialize serial communication at 125000 baud
  Serial.begin(125000);

  // Set WiFi mode to station and disconnect from any networks
  WiFi.mode(WIFI_MODE_STA);
  WiFi.disconnect(false, true);

  // Register the data received callback function with QuickEspNow
  quickEspNow.onDataRcvd(dataReceived);

  // Initialize QuickEspNow with channel 1
  quickEspNow.begin(1);

  // Print a message to indicate the setup is complete
  Serial.println("Ready to serve!");
}

// Buffer to store data for sending
uint8_t data[250];

// Counter to keep track of the number of bytes read
unsigned int counter;

void loop()
{
  // Wait until data is available on the serial port
  while (Serial.available() == 0)
    ;

  // Read a byte from the serial port and store it in the buffer
  data[counter] = Serial.read();

  // Increment the counter
  counter++;

  // If the buffer is full (250 bytes)
  if (counter == 250)
  {
    // Send the data using QuickEspNow to the HOP RX MAC address
    quickEspNow.send(hop_rx_mac, data, 250);

    // Clear the buffer by setting all elements to 0
    memset(data, 0, 250);

    // Reset the counter
    counter = 0;
  }
}

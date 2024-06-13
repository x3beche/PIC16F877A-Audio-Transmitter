#include <Arduino.h>
#include <WiFi.h>
#include <esp_wifi.h>
#include <QuickEspNow.h>
#include <HardwareSerial.h>

// MIC TX MAC = 40:22:D8:04:49:98
// HOP RX MAC = E8:DB:84:12:55:F0

// Define MAC addresses for communication
static uint8_t hop_rx_mac[] = {0xE8, 0xDB, 0x84, 0x12, 0x55, 0xF0};
static uint8_t mic_tx_mac[] = {0x40, 0x22, 0xD8, 0x04, 0x49, 0x98};

// Initialize a HardwareSerial object for serial communication on UART2
HardwareSerial SerialPort(2);

// Initialize a counter to keep track of RSSI measurements
int rssi_counter;

// Callback function to handle received data
void dataReceived(uint8_t *address, uint8_t *data, uint8_t len, signed int rssi, bool broadcast)
{
  rssi_counter++;

  // Every 10th received packet, send the RSSI value
  if (rssi_counter % 10 == 0)
  {
    // Convert RSSI to positive and set the highest bit to indicate RSSI
    signed int negRssi = -rssi;
    uint8_t rssiByte = static_cast<uint8_t>(negRssi);
    rssiByte |= 0b10000000;
    Serial.write(rssiByte); // Send the RSSI byte over serial
  }

  // Send the received data over serial
  Serial.write(data, len);
}

void setup()
{
  // Initialize serial communication at 115200 baud
  Serial.begin(115200);

  // Set WiFi mode to station and disconnect from any networks
  WiFi.mode(WIFI_MODE_STA);
  WiFi.disconnect(false, true);

  // Register the data received callback function with QuickEspNow
  quickEspNow.onDataRcvd(dataReceived);

  // Initialize QuickEspNow with channel 1
  quickEspNow.begin(1);
}

// Buffer to store data for sending
uint8_t data[1];

void loop()
{
  // If there is data available to read from serial
  if (Serial.available() > 0)
  {
    // Read one byte from serial
    data[0] = Serial.read();

    // Send the data using QuickEspNow to the MIC TX MAC address
    quickEspNow.send(mic_tx_mac, data, 1);

    // Reset the data buffer
    data[0] = 0;
  }
}

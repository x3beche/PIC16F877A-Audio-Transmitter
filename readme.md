# Communication System with PIC16F877A

## Overview

This project implements a communication system using the PIC16F877A microcontroller. The system integrates various modules to facilitate both audio and text data transmission, reception, and processing. The following features are included:

- **Audio Data Acquisition**: Analog values from the MAX9814 microphone amplifier are converted to digital values using the PIC16F877A's ADC unit.
- **Data Transmission**: Digitized audio data is transmitted wirelessly via a UART protocol to a receiver module.
- **Data Processing**: Received data is processed on a computer, where it can be converted back to an audio waveform in real-time or stored for later use.
- **Text Data Transmission**: Text data can be transmitted from the computer to the PIC16F877A via the wireless module (UART protocol).
- **OLED Display**: The system can display received text data on an OLED display using the I2C protocol.
- **LED Notifications**: LEDs are used for status notifications and alerts.

## Use Case

In scenarios such as missions where audio communication may not be feasible, this system allows for text data reception on an OLED display while simultaneously performing ambient listening for station communication.

## System Components

### Hardware

1. **PIC16F877A Microcontroller**: Central processing unit for data acquisition, processing, and communication.
2. **MAX9814 Microphone Amplifier**: Captures audio signals and amplifies them for the ADC.
3. **Wireless Module**: Facilitates wireless communication using UART protocol.
4. **OLED Display**: Displays text data using I2C protocol.
5. **LEDs**: Provide visual notifications and status indicators.

### Software

- **UART Communication**: For data transmission and reception.
- **I2C Protocol**: For interfacing with the OLED display.
- **ADC Conversion**: For converting analog audio signals to digital values.
- **Digital-to-Audio Conversion**: For real-time audio playback on a computer.

## Workflow

1. **Audio Data Acquisition**
   - The MAX9814 captures analog audio signals.
   - These signals are fed into the PIC16F877A's ADC unit, where they are converted into digital values.

2. **Data Transmission**
   - The digitized audio data is transmitted to a wireless module via UART.
   - The wireless module sends the data to a receiver, which is connected to a computer.

3. **Data Processing**
   - The computer receives the data, processes it, and converts it back into an audio waveform in real-time.
   - Alternatively, the data can be stored in memory for future playback.

4. **Text Data Transmission**
   - Text data can be sent from the computer to the PIC16F877A using the wireless module.
   - The microcontroller receives the text data via UART.

5. **OLED Display**
   - Received text data is displayed on the OLED display using the I2C protocol.
   - This allows for silent communication during sensitive operations.

6. **LED Notifications**
   - LEDs are used to indicate the status of various operations, such as data transmission, reception, and processing.

## Installation and Setup

1. **Hardware Setup**
   - Connect the MAX9814 microphone amplifier to the PIC16F877A's ADC input.
   - Interface the wireless module with the UART pins of the PIC16F877A.
   - Connect the OLED display to the I2C pins.
   - Attach LEDs to the appropriate GPIO pins for notifications.

2. **Software Setup**
   - Program the PIC16F877A with the provided firmware, which includes ADC reading, UART communication, I2C display control, and LED notification handling.
   - Install the required software on the computer to receive, process, and playback audio data.

## Images

| PCB Mounted | PCB Schematic | PCB Layout |
|-------------|---------------|------------|
| <img src="https://raw.githubusercontent.com/x3beche/PIC16F877A-Audio-Transmitter/main/images/pcb_mounted.jpg" height="500"> | <img src="https://raw.githubusercontent.com/x3beche/PIC16F877A-Audio-Transmitter/main/images/pcb_schematic.png" height="500"> | <img src="https://raw.githubusercontent.com/x3beche/PIC16F877A-Audio-Transmitter/main/images/pcb.png" height="500"> |
| **Description:** Image showing a physical PCB mounted with components. | **Description:** Schematic diagram of the PCB layout. | **Description:** Detailed layout design of the PCB including traces and components placement. |

| Software Interface |
|--------------------|
| <img src="https://raw.githubusercontent.com/x3beche/PIC16F877A-Audio-Transmitter/main/images/software.png" height="700"> |
| **Description:** Screenshot of the software interface used to interact with the Hardware. |



## Usage

- Start the system and ensure all components are powered and connected.
- The PIC16F877A will begin capturing audio data and transmitting it via the wireless module.
- On the computer, run the receiving software to process the incoming data.
- Send text data from the computer to the PIC16F877A as needed.
- Monitor the OLED display for incoming text messages.
- Observe the LED indicators for the status of operations.

## Conclusion

This communication system provides a robust solution for scenarios requiring both audio and text data transmission, reception, and processing. By integrating various modules, the system is well-suited for operations where reliable communication is essential.
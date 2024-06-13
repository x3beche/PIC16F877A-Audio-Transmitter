#include <xc.h>
#include <stdint.h>
#define _XTAL_FREQ 4000000

void I2C_Initialize(const unsigned long feq_K) {
    TRISC3 = 1;  // Set SCL (RC3) as input
    TRISC4 = 1;  // Set SDA (RC4) as input

    SSPCON  = 0b00101000;    // Enable SSP and set I2C master mode
    SSPCON2 = 0b00000000;    // Clear MSSP control register 2
    SSPADD = (_XTAL_FREQ/(4*feq_K*100))-1; // Setting Clock Speed
    SSPSTAT = 0b00000000;    // Clear MSSP status register
}

void I2C_Hold() {
    while ((SSPCON2 & 0b00011111) || (SSPSTAT & 0b00000100));
}

void I2C_Begin() {
    I2C_Hold();  
    SEN = 1;     // Initiate Start condition
}

void I2C_End() {
    I2C_Hold(); 
    PEN = 1;    // Initiate Stop condition
}

void I2C_Write(unsigned data) {
    I2C_Hold(); 
    SSPBUF = data; // Write data to SSPBUF
}

unsigned short I2C_Read(unsigned short ack) {
    unsigned short incoming;
    I2C_Hold();
    RCEN = 1; // Enable receive mode
    I2C_Hold();
    incoming = SSPBUF; // Read data from SSPBUF
    I2C_Hold();
    ACKDT = (ack)?0:1; // Acknowledge bit
    ACKEN = 1; // Initiate Acknowledge sequence
    return incoming;
}

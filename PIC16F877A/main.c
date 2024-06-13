#pragma config FOSC = HS  // Oscillator Selection bits (HS oscillator)
#pragma config WDTE = OFF // Watchdog Timer Enable bit (WDT disabled)
#pragma config PWRTE = ON // Power-up Timer Enable bit (PWRT enabled)
#pragma config BOREN = ON // Brown-out Reset Enable bit (BOR enabled)
#pragma config LVP = OFF  // Low-Voltage (Single-Supply) In-Circuit Serial Programming Enable bit (RB3 is digital I/O, HV on MCLR must be used for programming)
#pragma config CPD = OFF  // Data EEPROM Memory Code Protection bit (Data EEPROM code protection off)
#pragma config WRT = OFF  // Flash Program Memory Write Enable bits (Write protection off; all program memory may be written to by EECON control)
#pragma config CP = OFF   // Flash Program Memory Code Protection bit (Code protection off)

#include <xc.h>
#include "PIC16F877a_I2C.h"
#include "ssd1306_unbuffered.h"
#include <stdint.h> // Include standard integer types
#include <stdio.h>  // Include standard I/O for sprintf,
#include <string.h> // Include string handling

#define _XTAL_FREQ 16000000 // Specify the XTAL crystal frequency
#define Baud_rate 125000    // Baud rate for UART communication

unsigned char msb, lsb, rx_chr, rx_counter, rx_chr; // Variables for UART communication and counters
unsigned char date[50];                             // Buffer for date
unsigned char RSSI[50];                             // Buffer for RSSI
unsigned char text[50];                             // Buffer for received text
unsigned int flag = 0;                              // General purpose flag

// Interrupt service routine (ISR)
void __interrupt() ISR(void)
{
    if (TMR0IF == 1)
    {               // Check if Timer 0 interrupt flag is set
        TMR0IF = 0; // Clear the flag
        TMR0IE = 1; // Re-enable the interrupt
        TMR0 = 170; // Reset the timer preset count

        // Start ADC conversion
        while (GO_nDONE)
            ; // Wait for ADC conversion to complete

        // Transmit ADC result via UART
        while (!TXIF)
            ;
        TXREG = (ADRESL & 0b00011111) << 1; // Transmit lower 5 bits of ADC result
        while (!TXIF)
            ;
        TXREG = (((ADRESH & 0b00000011) << 4) | ((ADRESL & 0b11100000) >> 4)) + 1; // Transmit upper bits

        // Reconfigure ADC for next conversion
        ADCON0 = 0b10100101; // ADC ON and Fosc/2 is selected
        ADCON1 = 0b11001000; // VDD is set to AN3 pin and VSS is set to AN2
    }
}

// Initialize UART for serial communication
void Initialize_UART(void)
{
    TRISC6 = 0; // TX Pin set as output
    TRISC7 = 1; // RX Pin set as input

    BRGH = 1;                                    // Set for high baud rate
    SPBRG = ((_XTAL_FREQ / 16) / Baud_rate) - 1; // Baud rate calculation

    SYNC = 0; // Asynchronous mode
    SPEN = 1; // Enable serial port pins

    TXEN = 1;           // Enable transmission
    RCSTA = 0b10010000; // Enable serial port, 8-bit reception
    TXIF = RCIF = 0;    // Clear interrupt flags
}

// Initialize ADC (Analog-to-Digital Converter)
void ADC_Initialize()
{
    ADCON0 = 0b10100101; // ADC ON and Fosc/2 is selected
    ADCON1 = 0b10001000; // VDD is set to AN3 pin and VSS is set to AN2
}

// Function to print a string on the OLED display
void oled_puts(const char *c, uint8_t size)
{
    while (*c != '\0')
    {
        SSD1306_PutStretchC(*c, size);
        c++;
    }
}

// Display function to handle different types of messages
void display(void)
{
    // Check if text starts with "RTC" for date/time display
    if (strncmp(text, "RTC", 3) == 0)
    {
        char *dateTimePart = strchr(text, ' ');
        if (dateTimePart != NULL)
        {
            dateTimePart++; // Skip the space
            SSD1306_GotoXY(1, 1);
            oled_puts(dateTimePart, 1);
        }
    }

    // Check if text starts with "RSSI" for RSSI display
    if (strncmp(text, "RSSI", 4) == 0)
    {
        char *rssiPart = strchr(text, ' ');
        if (rssiPart != NULL)
        {
            rssiPart++; // Skip the space
            SSD1306_GotoXY(17, 1);
            oled_puts(rssiPart, 1);
        }
    }

    // Check if text starts with "MSG" for general message display
    if (strncmp(text, "MSG", 3) == 0)
    {
        char *msgPart = strchr(text, ' ');
        if (msgPart != NULL)
        {
            msgPart++; // Skip the space
            SSD1306_GotoXY(1, 4);
            oled_puts(msgPart, 1);
        }
    }
}

// Function to receive a character via UART
unsigned char rx()
{
    while (!RCIF)
        ;
    RCIF = 0;
    return RCREG;
}

void main(void)
{
    // Timer0 configuration
    T0CS = 0; // Internal Clock (CLKO)
    T0SE = 0; // Low/high edge select
    PSA = 0;  // Prescaler assigned to Timer0
    PS2 = 0;  // Prescaler rate select bits
    PS1 = 1;
    PS0 = 0;
    TMR0 = 167; // Preset timer count

    // Interrupt configuration
    INTCON = 0; // Clear interrupt control register
    TMR0IE = 1; // Enable Timer0 interrupt
    TMR0IF = 0; // Clear Timer0 interrupt flag
    GIE = 1;    // Enable global interrupts

    Initialize_UART();   // Initialize UART
    ADC_Initialize();    // Initialize ADC
    I2C_Initialize(100); // Initialize I2C

    __delay_ms(100);                                         // Short delay
    SSD1306_Init(SSD1306_SWITCHCAPVCC, SSD1306_I2C_ADDRESS); // Initialize OLED
    SSD1306_ClearDisplay();                                  // Clear OLED display

    TRISB &= 0b11110111; // Configure RB3 as output
    PORTB &= 0b11110111; // Set RB3 low

    while (1)
    {
        rx_chr = rx();     // Receive character via UART
        PORTBbits.RB3 = 1; // Set RB3 high

        if (rx_chr == '\n')
        {                      // If end of message (newline)
            PORTBbits.RB3 = 0; // Set RB3 low
            display();         // Call display function
            rx_counter = 0;    // Reset counter

            // Clear text buffer
            for (int i = 0; i < 50; i++)
            {
                text[i] = 0;
            }
        }
        else
        {
            text[rx_counter] = rx_chr; // Store received character
            rx_counter++;              // Increment counter
        }
    }
}
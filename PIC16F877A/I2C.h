/* 
 * File:   I2C.h
 * Author: yeozel
 *
 * Created on 28 May?s 2024 Sal?, 14:56
 */

#ifndef I2C_H
#define I2C_H

#include <xc.h>
#include <stdint.h>

// Function prototypes
void I2C_Initialize(const unsigned long feq_K);
void I2C_Hold();
void I2C_Begin();
void I2C_End();
void I2C_Write(unsigned data);
unsigned short I2C_Read(unsigned short ack);

#endif // I2C_H


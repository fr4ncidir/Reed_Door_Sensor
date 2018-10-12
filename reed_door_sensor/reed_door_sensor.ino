/*
 * reed_door_sensor
 * 
 * Copyright 2018 Francesco Antoniazzi <francesco.antoniazzi1991@gmail.com>
 * 
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 * MA 02110-1301, USA.
 * 
 */

// Comment the board you are not using.
#define NUCLEO_32
//#define HUZZAH

//------------------------------------
// Hyperterminal configuration
// 9600 bauds, 8-bit data, no parity
//------------------------------------

/*
 * The communication protocol of this system is the following:
 * Every second, the Nucleo board sends
 *   U
 * to certify it's alive.
 * When the sensor switches from closed to open, it sends
 *   O
 * Otherwise, switching from open to closed
 *   C
 */

#ifdef HUZZAH
#define SENSOR_IN   5
#define SENSOR_OUT  4
/*
 * https://learn.adafruit.com/assets/46249
 * Physical pin 14 = SENSOR_IN
 * Physical pin 13 = SENSOR_OUT
 * Notice: lack of pull down resistor in Huzzah makes the 
 * difference between this project and the Nucleo32 project on mbed.
 */

int old_s,new_s,mod4=0,led=LOW;
 
void setup() {
  Serial.begin(9600);
  pinMode(SENSOR_IN,INPUT_PULLUP);
  pinMode(SENSOR_OUT,OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(SENSOR_OUT,LOW);
  digitalWrite(LED_BUILTIN,led);
  old_s = digitalRead(SENSOR_IN);
}

void loop() {
  delay(250);
  new_s = digitalRead(SENSOR_IN);
  if (new_s!=old_s) {
    if (old_s==LOW) Serial.print("O");
    else Serial.print("C");
    old_s = new_s;
  }
  if (led==HIGH) led = LOW;
  else led = HIGH;
  digitalWrite(LED_BUILTIN,led);
  if (mod4%4==0) {
    Serial.print("U");
    mod4=0;
  }
  mod4++;
}
#endif


#ifdef NUCLEO_32
#include "mbed.h"

Serial pc(USBTX, USBRX, 9600);
DigitalIn sensor_in(PB_6,PullDown);
DigitalOut sensor_out(PB_7,1);
DigitalOut myled(LED1);

int main() {
    int old_s,new_s;
    uint8_t mod4=0;
    old_s = sensor_in.read();
    pc.baud(9600);
    pc.format(8,SerialBase::None,1);
    while (1) {
        wait(0.25);
        new_s = sensor_in.read();
        if (new_s!=old_s) {
            if (old_s==1) pc.putc('O');
            else pc.putc('C');
            old_s = new_s;
        }
        myled = !myled;
        if (mod4%4==0) {
            pc.putc('U');
            mod4 = 0;
        }
        mod4++;
    }
}
#endif

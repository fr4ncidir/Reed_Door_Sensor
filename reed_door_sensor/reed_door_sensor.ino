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
 * 
 */

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

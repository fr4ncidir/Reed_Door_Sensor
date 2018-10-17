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
//#define NUCLEO_32
#define HUZZAH

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
 
int examine(int new_status,int old_status,char *variant);
 
#ifdef HUZZAH
#define SENSOR_1_IN   	5
#define SENSOR_1_OUT  	4
#define SENSOR_2_IN		14
#define SENSOR_2_OUT	12

#define print_on_serial(x) 	Serial.print(x)
/*
 * https://learn.adafruit.com/assets/46249
 * Physical pin 14 = SENSOR_IN
 * Physical pin 13 = SENSOR_OUT
 * Notice: lack of pull down resistor in Huzzah makes the 
 * difference between this project and the Nucleo32 project on mbed.
 *
 * USE pins 4/5 for FRONT DOOR
 * USE pins 14/12 for REAR DOOR
 */

int old_s_1,old_s_2,mod4=0,led=LOW;
char outputs_1[2] = {'c','o'};
char outputs_2[2] = {'C','O'};
 
void setup() {
	Serial.begin(9600);
	pinMode(SENSOR_1_IN,INPUT_PULLUP);
	pinMode(SENSOR_1_OUT,OUTPUT);
	pinMode(SENSOR_2_IN,INPUT_PULLUP);
	pinMode(SENSOR_2_OUT,OUTPUT);
	pinMode(LED_BUILTIN, OUTPUT);
	digitalWrite(SENSOR_1_OUT,LOW);
	digitalWrite(SENSOR_2_OUT,LOW);
	digitalWrite(LED_BUILTIN,led);
	old_s_1 = digitalRead(SENSOR_1_IN);
	old_s_2 = digitalRead(SENSOR_2_IN);
}

void loop() {
	delay(250);
	old_s_1 = examine(digitalRead(SENSOR_1_IN),old_s_1,outputs_1);
	old_s_2 = examine(digitalRead(SENSOR_2_IN),old_s_2,outputs_2);
	if (led==HIGH) led = LOW;
	else led = HIGH;
	digitalWrite(LED_BUILTIN,led);
	if (mod4%4==0) {
		print_on_serial("U");
		mod4=0;
	}
	mod4++;
}
#endif


#ifdef NUCLEO_32
#include "mbed.h"

#define LOW		0
#define HIGH	1

#define print_on_serial(x) 	pc.putc(x)

Serial pc(USBTX, USBRX, 9600);
DigitalIn sensor_1_in(PB_6,PullDown);
DigitalOut sensor_1_out(PB_7,HIGH);
DigitalIn sensor_2_in(PB_4,PullDown);
DigitalOut sensor_2_out(PB_5,HIGH);
DigitalOut myled(LED1);

char outputs_1[2] = {'o','c'}; // here it's pulldown, not pullup as in huzzah's code
char outputs_2[2] = {'O','C'}; // here it's pulldown, not pullup as in huzzah's code

int main() {
	int old_s_1,old_s_2;
	uint8_t mod4=0;
	old_s_1 = sensor_1_in.read();
	old_s_2 = sensor_2_in.read();
	pc.baud(9600);
	pc.format(8,SerialBase::None,1);
	while (1) {
		wait(0.25);
		
		old_s_1 = examine(sensor_1_in.read(),old_s_1,outputs_1);
		old_s_2 = examine(sensor_2_in.read(),old_s_2,outputs_2);
		myled = !myled;
		if (mod4%4==0) {
			print_on_serial('U');
			mod4 = 0;
		}
		mod4++;
	}
}
#endif

int examine(int new_status,int old_status,char *variant) {
	if (new_status != old_status) {
		if (old_status == HIGH) print_on_serial(variant[0]);
		else print_on_serial(variant[1]);
	}
	return new_status;
}
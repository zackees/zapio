/**
 * Teensy 4.0 Test Project - LED Blink
 *
 * This simple sketch tests basic Teensy 4.0 functionality:
 * - GPIO (LED on pin 13)
 * - Serial output
 * - Core Arduino functions (delay, millis, digitalWrite)
 */

#include <Arduino.h>

void setup() {
  // Initialize LED pin
  pinMode(LED_BUILTIN, OUTPUT);

  // Initialize serial communication
  Serial.begin(9600);
  delay(1000);

  Serial.println("Teensy 4.0 Test - LED Blink");
  Serial.println("MCU: NXP i.MX RT1062");
  Serial.println("Core: ARM Cortex-M7 @ 600MHz");
}

void loop() {
  // Turn LED on
  digitalWrite(LED_BUILTIN, HIGH);
  Serial.println("LED ON");
  delay(500);

  // Turn LED off
  digitalWrite(LED_BUILTIN, LOW);
  Serial.println("LED OFF");
  delay(500);
}

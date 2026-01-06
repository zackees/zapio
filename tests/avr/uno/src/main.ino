// Blink LED example for Arduino Uno
// This is the minimal test case for validating the build system

void setup() {
  // Initialize built-in LED pin as output
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  // Turn LED on
  digitalWrite(LED_BUILTIN, HIGH);
  delay(1000);

  // Turn LED off
  digitalWrite(LED_BUILTIN, LOW);
  delay(1000);
}

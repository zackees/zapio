// ESP32-P4 test sketch - no LED_BUILTIN available
// Just test Serial functionality

// Wrapper for log_printf to satisfy --wrap=log_printf linker flag
// This is needed for ESP32-P4 builds
extern "C" {
  #include <stdarg.h>

  // Forward declaration of log_printfv (not wrapped, defined in esp32-hal-uart.c)
  extern int log_printfv(const char *format, va_list arg);

  // Wrapper function that the linker will call instead of log_printf
  // The real log_printf is renamed to __real_log_printf by the linker
  int __wrap_log_printf(const char *format, ...) {
    va_list args;
    va_start(args, format);

    // Call log_printfv which handles the va_list
    int result = log_printfv(format, args);

    va_end(args);
    return result;
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000);  // wait for host to connect
  Serial.println("ESP32-P4 TEST PASSED");
}

void loop() {
  Serial.println("ESP32-P4 Running...");
  delay(1000);
}

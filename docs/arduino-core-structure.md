# Arduino Core AVR Architecture

## Overview
ArduinoCore-avr is the official Arduino platform support for AVR microcontrollers (Uno, Mega, Nano, etc.). It provides the core libraries, board definitions, and build configurations needed to compile Arduino sketches for AVR targets.

**Repository**: https://github.com/arduino/ArduinoCore-avr
**Latest Version**: 1.8.6 (November 4, 2022)
**Language Composition**: C (91.5%), C++ (4.2%), Makefile (2.7%)

## Directory Structure

```
ArduinoCore-avr/
├── cores/
│   └── arduino/           # Core library implementation
│       ├── Arduino.h      # Main Arduino API header
│       ├── main.cpp       # Entry point (main() function)
│       ├── wiring.c       # millis(), delay(), etc.
│       ├── wiring_digital.c  # pinMode(), digitalWrite()
│       ├── wiring_analog.c   # analogRead(), analogWrite()
│       ├── wiring_pulse.c    # pulseIn()
│       ├── wiring_shift.c    # shiftOut(), shiftIn()
│       ├── HardwareSerial.cpp # Serial communication
│       ├── Print.cpp      # Print class (Serial.print)
│       ├── Stream.cpp     # Stream class
│       ├── WString.cpp    # String class
│       ├── WMath.cpp      # Math functions
│       ├── hooks.c        # Weak function hooks
│       └── ... (~25 total files)
├── variants/
│   ├── standard/          # Arduino Uno variant
│   │   └── pins_arduino.h # Pin definitions for Uno
│   ├── mega/              # Arduino Mega variant
│   ├── leonardo/          # Arduino Leonardo variant
│   └── ... (other board variants)
├── libraries/
│   ├── SPI/               # SPI communication library
│   ├── Wire/              # I2C/TWI communication library
│   ├── EEPROM/            # EEPROM access library
│   ├── SoftwareSerial/    # Software serial implementation
│   └── ... (other built-in libraries)
├── bootloaders/           # Bootloader binaries for different boards
├── firmwares/             # Additional firmware files
├── drivers/               # USB drivers (Windows)
├── boards.txt             # Board definitions and specifications
├── platform.txt           # Build recipes and toolchain configuration
└── programmers.txt        # Programmer configurations
```

## Critical Files for Zapio Build System

### 1. boards.txt
Defines board-specific configurations. Each board has multiple properties:

```ini
# Arduino Uno Definition
uno.name=Arduino Uno
uno.vid.0=0x2341
uno.pid.0=0x0043

# Build properties
uno.build.mcu=atmega328p
uno.build.f_cpu=16000000L
uno.build.board=AVR_UNO
uno.build.core=arduino
uno.build.variant=standard

# Upload settings
uno.upload.tool=avrdude
uno.upload.protocol=arduino
uno.upload.maximum_size=32256
uno.upload.maximum_data_size=2048
uno.upload.speed=115200

# Bootloader
uno.bootloader.tool=avrdude
uno.bootloader.low_fuses=0xFF
uno.bootloader.high_fuses=0xDE
uno.bootloader.extended_fuses=0xFD
uno.bootloader.unlock_bits=0x3F
uno.bootloader.lock_bits=0x0F
uno.bootloader.file=optiboot/optiboot_atmega328.hex
```

**Key Board Properties for Build System**:
- `uno.build.mcu` → `-mmcu=atmega328p` compiler flag
- `uno.build.f_cpu` → `-DF_CPU=16000000L` define
- `uno.build.board` → `-DARDUINO_AVR_UNO` define
- `uno.build.core` → Path to core: `cores/arduino`
- `uno.build.variant` → Path to variant: `variants/standard`
- `uno.upload.maximum_size` → Flash size (32256 bytes)
- `uno.upload.maximum_data_size` → RAM size (2048 bytes)

### 2. platform.txt
Contains build recipes (command templates) for compilation and linking.

**Critical Recipe Variables**:
```properties
# Compiler paths
compiler.path={runtime.tools.avr-gcc.path}/bin/
compiler.c.cmd=avr-gcc
compiler.cpp.cmd=avr-g++
compiler.ar.cmd=avr-gcc-ar
compiler.objcopy.cmd=avr-objcopy
compiler.elf2hex.cmd=avr-objcopy
compiler.size.cmd=avr-size

# C Compiler flags
compiler.c.flags=-c -g -Os -w -std=gnu11 -ffunction-sections -fdata-sections -MMD -flto -fno-fat-lto-objects

# C++ Compiler flags
compiler.cpp.flags=-c -g -Os -w -std=gnu++11 -fpermissive -fno-exceptions -ffunction-sections -fdata-sections -fno-threadsafe-statics -Wno-error=narrowing -MMD -flto

# Linker flags
compiler.c.elf.flags={compiler.warning_flags} -Os -g -flto -fuse-linker-plugin -Wl,--gc-sections -mmcu={build.mcu}

# Size flags
compiler.size.flags=-A

# Build recipes
recipe.c.o.pattern="{compiler.path}{compiler.c.cmd}" {compiler.c.flags} -mmcu={build.mcu} -DF_CPU={build.f_cpu} -DARDUINO={runtime.ide.version} -DARDUINO_{build.board} -DARDUINO_ARCH_{build.arch} {compiler.c.extra_flags} {build.extra_flags} {includes} "{source_file}" -o "{object_file}"

recipe.cpp.o.pattern="{compiler.path}{compiler.cpp.cmd}" {compiler.cpp.flags} -mmcu={build.mcu} -DF_CPU={build.f_cpu} -DARDUINO={runtime.ide.version} -DARDUINO_{build.board} -DARDUINO_ARCH_{build.arch} {compiler.cpp.extra_flags} {build.extra_flags} {includes} "{source_file}" -o "{object_file}"

recipe.ar.pattern="{compiler.path}{compiler.ar.cmd}" {compiler.ar.flags} {compiler.ar.extra_flags} "{archive_file_path}" "{object_file}"

recipe.c.combine.pattern="{compiler.path}{compiler.c.cmd}" {compiler.c.elf.flags} -mmcu={build.mcu} {compiler.c.elf.extra_flags} -o "{build.path}/{build.project_name}.elf" {object_files} "{build.path}/{archive_file}" "-L{build.path}" -lm

recipe.objcopy.eep.pattern="{compiler.path}{compiler.objcopy.cmd}" {compiler.objcopy.eep.flags} {compiler.objcopy.eep.extra_flags} "{build.path}/{build.project_name}.elf" "{build.path}/{build.project_name}.eep"

recipe.objcopy.hex.pattern="{compiler.path}{compiler.objcopy.cmd}" {compiler.objcopy.hex.flags} {compiler.objcopy.hex.extra_flags} "{build.path}/{build.project_name}.elf" "{build.path}/{build.project_name}.hex"

recipe.size.pattern="{compiler.path}{compiler.size.cmd}" {compiler.size.flags} -mmcu={build.mcu} "{build.path}/{build.project_name}.elf"
```

### 3. cores/arduino/
The heart of the Arduino framework implementation.

**Essential Core Files** (~25 files total):
```
cores/arduino/
├── Arduino.h          # Main header with all Arduino APIs
├── main.cpp           # Entry point with main() calling setup()/loop()
├── wiring.c           # Timing functions: millis(), micros(), delay()
├── wiring_digital.c   # Digital I/O: pinMode(), digitalWrite(), digitalRead()
├── wiring_analog.c    # Analog I/O: analogRead(), analogWrite() (PWM)
├── wiring_pulse.c     # pulseIn(), pulseInLong()
├── wiring_shift.c     # shiftOut(), shiftIn()
├── wiring_private.h   # Internal definitions
├── hooks.c            # Weak hooks for setup(), loop()
├── HardwareSerial.h/cpp        # Serial communication class
├── HardwareSerial0.cpp/1/2/3   # Serial port instances
├── Print.h/cpp        # Print base class
├── Stream.h/cpp       # Stream base class
├── WString.h/cpp      # Arduino String class
├── WMath.cpp          # Math utilities: random(), map()
├── IPAddress.h/cpp    # IP address class
├── Printable.h        # Printable interface
├── USBAPI.h           # USB API (for Leonardo, etc.)
├── PluggableUSB.h/cpp # USB device support
├── abi.cpp            # C++ ABI support
├── new.h/cpp          # C++ new/delete operators
└── WCharacter.h       # Character classification functions
```

**main.cpp** (Entry Point):
```cpp
#include <Arduino.h>

int main(void)
{
    init();  // Initialize timers, PWM, ADC

    initVariant();  // Board-specific initialization (weak)

#if defined(USBCON)
    USBDevice.attach();
#endif

    setup();  // User setup function

    for (;;) {
        loop();  // User loop function
        if (serialEventRun) serialEventRun();
    }

    return 0;
}
```

### 4. variants/standard/ (Arduino Uno)
Board-specific pin mappings and definitions.

**pins_arduino.h** key definitions:
```cpp
#define NUM_DIGITAL_PINS            20
#define NUM_ANALOG_INPUTS           6

#define LED_BUILTIN                 13

#define PIN_SPI_SS    (10)
#define PIN_SPI_MOSI  (11)
#define PIN_SPI_MISO  (12)
#define PIN_SPI_SCK   (13)

#define PIN_WIRE_SDA        (18)
#define PIN_WIRE_SCL        (19)

#define PIN_A0   (14)
#define PIN_A1   (15)
// ... etc

// Digital pin to port/pin mappings
const uint8_t PROGMEM digital_pin_to_port_PGM[] = {
    // D0-D7
    PD, PD, PD, PD, PD, PD, PD, PD,
    // D8-D13
    PB, PB, PB, PB, PB, PB,
    // D14-D19 (A0-A5)
    PC, PC, PC, PC, PC, PC
};
```

## Compilation Requirements

### Include Paths (-I flags)
Must include these paths for successful compilation:
1. `{core_path}/cores/arduino` - Core Arduino.h and implementation
2. `{core_path}/variants/standard` - Uno pin definitions
3. Project source directory (for local headers)
4. Library paths (if lib_deps specified)

### Required Defines (-D flags)
```bash
-DARDUINO=10819                # Arduino version (1.8.19)
-DARDUINO_AVR_UNO              # Board identifier
-DARDUINO_ARCH_AVR             # Architecture identifier
-DF_CPU=16000000L              # CPU frequency (16 MHz)
-D__AVR_ATmega328P__           # MCU type (set by avr-gcc)
```

### MCU Flag
```bash
-mmcu=atmega328p               # Target microcontroller
```

## Build Process Flow

### Step 1: Compile Core Sources
Compile all .c and .cpp files in `cores/arduino/`:
```bash
avr-gcc -c -g -Os -w -std=gnu11 -ffunction-sections -fdata-sections \
  -mmcu=atmega328p -DF_CPU=16000000L -DARDUINO=10819 \
  -DARDUINO_AVR_UNO -DARDUINO_ARCH_AVR \
  -I{core}/cores/arduino -I{core}/variants/standard \
  cores/arduino/wiring.c -o build/core/wiring.o
```

Repeat for all ~25 core files.

### Step 2: Create Core Archive
```bash
avr-ar rcs build/core.a build/core/*.o
```

### Step 3: Preprocess .ino Files
Convert .ino to .cpp:
- Add `#include <Arduino.h>` at top
- Extract function prototypes
- Add forward declarations

### Step 4: Compile Sketch Sources
```bash
avr-g++ -c -g -Os -w -std=gnu++11 -fpermissive -fno-exceptions \
  -ffunction-sections -fdata-sections -fno-threadsafe-statics \
  -mmcu=atmega328p -DF_CPU=16000000L -DARDUINO=10819 \
  -DARDUINO_AVR_UNO -DARDUINO_ARCH_AVR \
  -I{core}/cores/arduino -I{core}/variants/standard \
  src/main.cpp -o build/src/main.o
```

### Step 5: Link
```bash
avr-gcc -Os -g -flto -fuse-linker-plugin -Wl,--gc-sections \
  -mmcu=atmega328p \
  -o build/firmware.elf \
  build/src/*.o \
  build/core.a \
  -lm
```

### Step 6: Generate HEX
```bash
avr-objcopy -O ihex -R .eeprom build/firmware.elf build/firmware.hex
```

### Step 7: Display Size
```bash
avr-size -A build/firmware.elf
```

## Arduino Uno Specifications

| Property | Value |
|----------|-------|
| **Microcontroller** | ATmega328P |
| **Operating Voltage** | 5V |
| **Clock Speed** | 16 MHz |
| **Flash Memory** | 32 KB (0.5 KB bootloader) |
| **SRAM** | 2 KB |
| **EEPROM** | 1 KB |
| **Digital I/O Pins** | 14 (6 PWM) |
| **Analog Input Pins** | 6 |
| **Max Flash for Sketch** | 32,256 bytes |
| **Max SRAM for Variables** | 2,048 bytes |

## Implementation Strategy for Zapio

### Phase 1: Download & Cache
1. Download ArduinoCore-avr-1.8.6.tar.gz from GitHub
2. Extract to `.zap/cache/platforms/arduino-avr-1.8.6/`
3. Parse `boards.txt` to extract Uno configuration
4. Parse `platform.txt` for build recipes (future)

### Phase 2: Source Discovery
1. Find all .c/.cpp files in `cores/arduino/`
2. Find variant files in `variants/standard/`
3. Scan project `src/` directory for .ino/.cpp/.c files
4. Preprocess .ino files to .cpp

### Phase 3: Compilation
1. Compile core sources → `build/core/*.o`
2. Create `core.a` archive
3. Compile sketch sources → `build/src/*.o`
4. Link all objects → `firmware.elf`
5. Convert to `firmware.hex`

### Phase 4: Validation
1. Check firmware size vs. flash limit (32,256 bytes)
2. Check SRAM usage vs. RAM limit (2,048 bytes)
3. Report build results

## References
- Arduino AVR Core: https://github.com/arduino/ArduinoCore-avr
- boards.txt format: https://arduino.github.io/arduino-cli/dev/platform-specification/
- Arduino Build Process: https://github.com/arduino/arduino-builder
- AVR-GCC Manual: https://gcc.gnu.org/onlinedocs/gcc/AVR-Options.html

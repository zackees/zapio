# PlatformIO.ini Configuration Specification

## Overview
The `platformio.ini` file is the main configuration file for embedded projects. It defines build environments, platforms, boards, and compilation settings.

## File Format
- Uses INI file format with sections and key-value pairs
- Comments start with `;` or `#`
- Multi-line values are indented with spaces or tabs
- Variable substitution: `${section.key}`

## Basic Structure

```ini
[env:environment_name]
platform = platform_name
board = board_name
framework = framework_name
```

## Section Types

### [env] - Common Environment Settings
Settings defined in `[env]` are inherited by all `[env:*]` sections.

```ini
[env]
build_flags = -DDEBUG
monitor_speed = 9600
```

### [env:name] - Specific Environment
Each `[env:name]` section defines a build environment/target.

```ini
[env:uno]
platform = atmelavr
board = uno
framework = arduino
```

## Required Fields for Arduino Uno

### platform
Specifies the hardware platform. For Arduino Uno:
```ini
platform = atmelavr
```

For fbuild with URL-based approach (future):
```ini
platform_url = https://github.com/arduino/ArduinoCore-avr/archive/refs/tags/1.8.6.tar.gz
```

### board
Identifies the specific board. For Arduino Uno:
```ini
board = uno
```

Common AVR boards:
- `uno` - Arduino Uno (ATmega328P)
- `mega2560` - Arduino Mega 2560 (ATmega2560)
- `nano` - Arduino Nano (ATmega328P)
- `leonardo` - Arduino Leonardo (ATmega32U4)

### framework
Specifies the development framework:
```ini
framework = arduino
```

## Optional Configuration Fields

### build_flags
Compiler and linker flags:
```ini
build_flags =
    -DDEBUG
    -DVERSION=1.0
    -Os
    -Wall
```

### lib_deps
Library dependencies (for future implementation):
```ini
lib_deps =
    SPI
    Wire
    https://github.com/user/library.git
```

### upload_port
Serial port for uploading firmware:
```ini
upload_port = COM3        ; Windows
upload_port = /dev/ttyUSB0  ; Linux
upload_port = /dev/cu.usbserial ; macOS
```

### monitor_speed
Serial monitor baud rate:
```ini
monitor_speed = 9600
monitor_speed = 115200
```

### board_build.* - Board Overrides
Override board-specific settings:
```ini
board_build.mcu = atmega328p
board_build.f_cpu = 16000000L
```

## Variable Substitution

Reference values from other sections:
```ini
[common]
build_flags = -DDEBUG

[env:uno]
platform = atmelavr
board = uno
framework = arduino
build_flags = ${common.build_flags} -DUNO
```

## Arduino Uno Complete Example

```ini
; Minimal Arduino Uno configuration
[env:uno]
platform = atmelavr
board = uno
framework = arduino

; Complete Arduino Uno configuration with optional settings
[env:uno_full]
platform = atmelavr
board = uno
framework = arduino
upload_port = COM3
monitor_speed = 9600
lib_deps =
    SPI
    Wire
build_flags =
    -DDEBUG
    -Wall
```

## Multiple Environments

```ini
[env:uno]
platform = atmelavr
board = uno
framework = arduino

[env:mega]
platform = atmelavr
board = mega2560
framework = arduino

[env:nano]
platform = atmelavr
board = nano
framework = arduino
```

## Board Configuration Details (boards.txt mapping)

When `board = uno` is specified, the following settings are derived from `boards.txt`:

| Key | Value | Description |
|-----|-------|-------------|
| `uno.name` | Arduino Uno | Board display name |
| `uno.build.mcu` | atmega328p | Microcontroller type |
| `uno.build.f_cpu` | 16000000L | CPU frequency (16 MHz) |
| `uno.build.board` | AVR_UNO | Board macro for Arduino.h |
| `uno.build.core` | arduino | Core library to use |
| `uno.build.variant` | standard | Pin mapping variant |
| `uno.upload.protocol` | arduino | Upload protocol |
| `uno.upload.maximum_size` | 32256 | Flash size (32KB - bootloader) |
| `uno.upload.speed` | 115200 | Upload baud rate |

## Implementation Notes

### Phase 1 (Current)
- Support minimal configuration: `platform`, `board`, `framework`
- Parse INI file using Python's `configparser`
- Validate required fields are present
- Extract environment configurations

### Future Enhancements
- Variable substitution (`${section.key}`)
- Library dependency resolution (`lib_deps`)
- Build flag customization
- Multiple environment builds
- URL-based platform specification

## References
- PlatformIO Documentation: https://docs.platformio.org/en/latest/projectconf/
- Arduino boards.txt format: https://github.com/arduino/Arduino/wiki/Arduino-IDE-1.5-3rd-party-Hardware-specification

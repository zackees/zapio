# Teensy 4.0 Test Project

This is a test project for validating Teensy 4.0 platform support in fbuild.

## Board Specifications

- **Board**: Teensy 4.0
- **MCU**: NXP i.MX RT1062 (ARM Cortex-M7 @ 600MHz)
- **Flash**: 2MB
- **RAM**: 1MB (512KB TCM)
- **Platform**: teensy
- **Framework**: Arduino

## Test Code

The test code implements a simple LED blink example that:
- Blinks the built-in LED (pin 13) at 1Hz
- Outputs status messages via Serial at 9600 baud
- Tests basic Arduino API functions (pinMode, digitalWrite, delay, millis, Serial)

## Building

```bash
# Clean build
uv run fbuild build tests/teensy40 -e teensy40 --clean

# Incremental build
uv run fbuild build tests/teensy40 -e teensy40

# Verbose build
uv run fbuild build tests/teensy40 -e teensy40 -v
```

## Expected Output

The build should:
1. Download and cache ARM GCC toolchain (arm-none-eabi-gcc)
2. Download and cache Teensy cores from PaulStoffregen/cores
3. Compile source files with Cortex-M7 flags
4. Link with Teensy 4.0 linker script
5. Generate firmware.hex file

## Hardware Testing

After successful build:

```bash
# Deploy to Teensy 4.0 board
uv run fbuild deploy tests/teensy40 -e teensy40

# Deploy and monitor serial output
uv run fbuild deploy tests/teensy40 -e teensy40 --monitor
```

Expected behavior:
- LED blinks at 1Hz
- Serial output shows "LED ON" and "LED OFF" messages
- No compilation or runtime errors

## Differences from Teensy 4.1

- **Flash**: 2MB (vs 8MB on Teensy 4.1)
- **Board Definition**: TEENSY40 (vs TEENSY41)
- **Variant**: teensy40 (vs teensy41)
- **Physical**: No Ethernet, SD card slot, or additional pins

## Status

Based on Teensy 4.1 support. Shares the same core infrastructure:
- ToolchainTeensy module with ARM GCC support
- FrameworkTeensy module for Teensy cores
- PlatformTeensy module for platform coordination
- Build orchestrator integration (detection and routing)

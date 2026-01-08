# Teensy 4.1 Test Project

This is a test project for validating Teensy 4.1 platform support in Zapio.

## Board Specifications

- **Board**: Teensy 4.1
- **MCU**: NXP i.MX RT1062 (ARM Cortex-M7 @ 600MHz)
- **Flash**: 8MB
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
uv run zap build tests/teensy41 -e teensy41 --clean

# Incremental build
uv run zap build tests/teensy41 -e teensy41

# Verbose build
uv run zap build tests/teensy41 -e teensy41 -v
```

## Expected Output

The build should:
1. Download and cache ARM GCC toolchain (arm-none-eabi-gcc)
2. Download and cache Teensy cores from PaulStoffregen/cores
3. Compile source files with Cortex-M7 flags
4. Link with Teensy 4.1 linker script
5. Generate firmware.hex file

## Hardware Testing

After successful build:

```bash
# Deploy to Teensy 4.1 board
uv run zap deploy tests/teensy41 -e teensy41

# Deploy and monitor serial output
uv run zap deploy tests/teensy41 -e teensy41 --monitor
```

Expected behavior:
- LED blinks at 1Hz
- Serial output shows "LED ON" and "LED OFF" messages
- No compilation or runtime errors

## Status

**Current Implementation Status**: Phase 2 Complete (Module Foundation)

### ✅ Completed
- Board configuration (teensy41 in board_config.py)
- Platform detection (imxrt* -> teensy)
- ToolchainTeensy module with ARM GCC support
- FrameworkTeensy module for Teensy cores
- PlatformTeensy module for platform coordination
- Build orchestrator integration (detection and routing)
- Test project structure and example code

### 🚧 In Progress
- Build orchestrator implementation (OrchestratorTeensy)
- Compilation with Cortex-M7 flags
- Linking with Teensy linker scripts
- Firmware generation (.hex format)

### ⏳ Pending
- Deployment support (teensy_loader_cli integration)
- Library dependency management
- Serial monitor integration
- Documentation updates

## Implementation Notes

### Module Structure
```
src/zapio/packages/
├── toolchain_teensy.py    # ARM GCC toolchain management
├── framework_teensy.py    # Teensy cores framework
└── platform_teensy.py     # Platform coordination

src/zapio/config/
└── board_config.py        # Added teensy41 board definition
```

### Compiler Flags
```
-mcpu=cortex-m7           # Target CPU
-mthumb                   # Thumb instruction set
-mfloat-abi=hard          # Hardware FPU
-mfpu=fpv5-d16            # FPU version
-O2                       # Optimization level
-DF_CPU=600000000L        # CPU frequency
-DARDUINO_TEENSY41        # Board definition
-D__IMXRT1062__           # MCU definition
```

### Linker Script
- Location: `cores/teensy4/imxrt1062_t41.ld`
- Defines memory layout for RT1062 with TCM

## Next Steps (Iteration 3+)

1. Implement OrchestratorTeensy class
2. Integrate ConfigurableCompiler with Teensy flags
3. Integrate ConfigurableLinker with Teensy linker script
4. Test compilation end-to-end
5. Implement deployment support
6. Validate on hardware

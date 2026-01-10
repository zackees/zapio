# AVR Toolchain Packages

## Overview
The AVR toolchain provides the compiler, linker, and utilities needed to build firmware for AVR microcontrollers (Arduino Uno, Mega, Nano, etc.). Arduino uses a customized version of the GNU AVR toolchain.

## Required Toolchain Version
**Version**: avr-gcc 7.3.0-atmel3.6.1-arduino7
- This is Arduino's recommended version for Arduino AVR Boards 1.8.6
- Based on GCC 7.3.0 with Atmel-specific patches
- Arduino-specific modifications (version 7)

## Toolchain Components

The toolchain includes these essential executables:

| Tool | Purpose | Usage |
|------|---------|-------|
| `avr-gcc` | C compiler | Compiles .c files to .o objects |
| `avr-g++` | C++ compiler | Compiles .cpp files to .o objects |
| `avr-ar` | Archiver | Creates .a library archives (core.a) |
| `avr-objcopy` | Object converter | Converts .elf to .hex/.eep formats |
| `avr-objdump` | Object dumper | Disassembles binaries (debugging) |
| `avr-size` | Size analyzer | Reports flash/RAM usage |
| `avr-nm` | Symbol lister | Lists symbols in binaries |
| `avr-ranlib` | Archive indexer | Indexes .a archives (rarely needed) |
| `avr-strip` | Symbol stripper | Removes debug symbols |

## Download URLs

### Windows (x86)
**URL**: http://downloads.arduino.cc/tools/avr-gcc-7.3.0-atmel3.6.1-arduino7-i686-w64-mingw32.zip

**Format**: ZIP archive
**Platform**: Windows 32-bit (works on 64-bit Windows)
**Executable Extension**: `.exe`
**Typical Size**: ~45 MB

**Path Structure**:
```
avr-gcc-7.3.0-atmel3.6.1-arduino7-i686-w64-mingw32/
├── bin/
│   ├── avr-gcc.exe
│   ├── avr-g++.exe
│   ├── avr-ar.exe
│   ├── avr-objcopy.exe
│   ├── avr-size.exe
│   └── ... (other tools)
├── lib/
├── libexec/
├── avr/
│   ├── include/     # AVR libc headers
│   └── lib/         # AVR libc libraries
└── share/
```

### Linux x86_64 (64-bit)
**URL**: http://downloads.arduino.cc/tools/avr-gcc-7.3.0-atmel3.6.1-arduino7-x86_64-pc-linux-gnu.tar.bz2

**Format**: tar.bz2 archive
**Platform**: Linux 64-bit (Intel/AMD)
**Typical Size**: ~40 MB

### Linux i686 (32-bit)
**URL**: http://downloads.arduino.cc/tools/avr-gcc-7.3.0-atmel3.6.1-arduino7-i686-pc-linux-gnu.tar.bz2

**Format**: tar.bz2 archive
**Platform**: Linux 32-bit

### Linux ARM (Raspberry Pi)
**URL**: http://downloads.arduino.cc/tools/avr-gcc-7.3.0-atmel3.6.1-arduino7-arm-linux-gnueabihf.tar.bz2

**Format**: tar.bz2 archive
**Platform**: Linux ARM 32-bit (Raspberry Pi 2/3/4)

### Linux ARM64 (64-bit ARM)
**URL**: http://downloads.arduino.cc/tools/avr-gcc-7.3.0-atmel3.6.1-arduino7-aarch64-pc-linux-gnu.tar.bz2

**Format**: tar.bz2 archive
**Platform**: Linux ARM 64-bit

### macOS x86_64
**URL**: http://downloads.arduino.cc/tools/avr-gcc-7.3.0-atmel3.6.1-arduino7-x86_64-apple-darwin14.tar.bz2

**Format**: tar.bz2 archive
**Platform**: macOS (Intel Macs)
**Target**: darwin14 (macOS 10.10+)
**Typical Size**: ~42 MB

**Note**: Apple Silicon (M1/M2) Macs can use this via Rosetta 2.

## Platform Detection Strategy

### Python Implementation
```python
import platform
import sys

def get_toolchain_url() -> str:
    """Return appropriate toolchain URL for current platform."""
    system = platform.system()
    machine = platform.machine()

    if system == "Windows":
        return "http://downloads.arduino.cc/tools/avr-gcc-7.3.0-atmel3.6.1-arduino7-i686-w64-mingw32.zip"

    elif system == "Linux":
        if machine == "x86_64":
            return "http://downloads.arduino.cc/tools/avr-gcc-7.3.0-atmel3.6.1-arduino7-x86_64-pc-linux-gnu.tar.bz2"
        elif machine == "i686" or machine == "i386":
            return "http://downloads.arduino.cc/tools/avr-gcc-7.3.0-atmel3.6.1-arduino7-i686-pc-linux-gnu.tar.bz2"
        elif machine.startswith("arm") and "64" in machine:
            return "http://downloads.arduino.cc/tools/avr-gcc-7.3.0-atmel3.6.1-arduino7-aarch64-pc-linux-gnu.tar.bz2"
        elif machine.startswith("arm"):
            return "http://downloads.arduino.cc/tools/avr-gcc-7.3.0-atmel3.6.1-arduino7-arm-linux-gnueabihf.tar.bz2"

    elif system == "Darwin":  # macOS
        return "http://downloads.arduino.cc/tools/avr-gcc-7.3.0-atmel3.6.1-arduino7-x86_64-apple-darwin14.tar.bz2"

    raise RuntimeError(f"Unsupported platform: {system} {machine}")

def get_archive_format() -> str:
    """Return archive format for current platform."""
    return "zip" if platform.system() == "Windows" else "tar.bz2"
```

## Arduino AVR Platform Package

### Platform Core (ArduinoCore-avr)
**URL**: https://downloads.arduino.cc/cores/staging/avr-1.8.6.tar.bz2

**Version**: 1.8.6
**Size**: 7,127,080 bytes (6.8 MB)
**Checksum**: SHA-256:ff1d17274b5a952f172074bd36c3924336baefded0232e10982f8999c2f7c3b6
**Format**: tar.bz2

**Contents**:
- cores/arduino/ - Arduino core library
- variants/ - Board-specific pin definitions
- libraries/ - Built-in libraries (SPI, Wire, EEPROM, etc.)
- bootloaders/ - Bootloader binaries
- boards.txt - Board configurations
- platform.txt - Build recipes

**Alternative (GitHub)**:
```bash
# Get from GitHub releases
https://github.com/arduino/ArduinoCore-avr/archive/refs/tags/1.8.6.tar.gz
```

## Verification & Checksums

### SHA-256 Checksums
For security and integrity, verify downloads:

**Platform Package**:
```
avr-1.8.6.tar.bz2
SHA-256: ff1d17274b5a952f172074bd36c3924336baefded0232e10982f8999c2f7c3b6
```

**Toolchain Checksums**: Available in package_index.json

### Verification Command
```bash
# Linux/macOS
sha256sum avr-1.8.6.tar.bz2

# Windows (PowerShell)
Get-FileHash avr-1.8.6.tar.bz2 -Algorithm SHA256
```

## Installation & Cache Strategy

### Recommended Cache Structure
```
.fbuild/
└── cache/
    ├── packages/
    │   └── avr-gcc-7.3.0-atmel3.6.1-arduino7/
    │       ├── bin/
    │       │   ├── avr-gcc
    │       │   ├── avr-g++
    │       │   ├── avr-ar
    │       │   ├── avr-objcopy
    │       │   └── avr-size
    │       ├── lib/
    │       ├── libexec/
    │       └── avr/
    └── platforms/
        └── arduino-avr-1.8.6/
            ├── cores/
            ├── variants/
            ├── libraries/
            ├── boards.txt
            └── platform.txt
```

### Download & Installation Flow
1. **Detect Platform**: Determine OS and architecture
2. **Select URL**: Choose appropriate toolchain URL
3. **Check Cache**: Look for existing installation in `.fbuild/cache/`
4. **Download**: If not cached, download with progress bar
5. **Verify**: Check SHA-256 checksum (if available)
6. **Extract**: Unpack archive to cache directory
7. **Validate**: Verify `avr-gcc` executable exists and runs
8. **Store Metadata**: Save version info for future checks

### Python Download Example
```python
import requests
import tarfile
import zipfile
from pathlib import Path
from tqdm import tqdm

def download_toolchain(url: str, dest_dir: Path) -> Path:
    """Download and extract toolchain."""
    # Determine filename from URL
    filename = url.split('/')[-1]
    download_path = dest_dir / filename

    # Download with progress bar
    response = requests.get(url, stream=True)
    response.raise_for_status()

    total_size = int(response.headers.get('content-length', 0))

    with open(download_path, 'wb') as f:
        with tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                pbar.update(len(chunk))

    # Extract archive
    extract_dir = dest_dir / "avr-gcc-7.3.0-atmel3.6.1-arduino7"

    if filename.endswith('.zip'):
        with zipfile.ZipFile(download_path, 'r') as zip_ref:
            zip_ref.extractall(dest_dir)
    elif filename.endswith('.tar.bz2'):
        with tarfile.open(download_path, 'r:bz2') as tar_ref:
            tar_ref.extractall(dest_dir)

    return extract_dir
```

## Tool Version Verification

### Check Toolchain Version
```bash
# Check avr-gcc version
avr-gcc --version
# Output: avr-gcc (GCC) 7.3.0

# Check included tools
avr-g++ --version
avr-ar --version
avr-objcopy --version
avr-size --version
```

### Python Verification
```python
import subprocess
from pathlib import Path

def verify_toolchain(toolchain_dir: Path) -> bool:
    """Verify toolchain is functional."""
    avr_gcc = toolchain_dir / "bin" / "avr-gcc"

    if not avr_gcc.exists():
        return False

    try:
        result = subprocess.run(
            [str(avr_gcc), "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        return "7.3.0" in result.stdout
    except subprocess.CalledProcessError:
        return False
```

## Additional Tools (Future Support)

### avrdude (Upload Tool)
**Version**: 6.3.0-arduino17
**Purpose**: Upload firmware to Arduino boards
**Note**: Not required for Phase 1 (build only)

### arduinoOTA (Over-The-Air Upload)
**Version**: 1.3.0
**Purpose**: Wireless firmware updates
**Note**: Not required for Phase 1

## Compiler Flags Reference

### Common C Flags
```bash
-c                      # Compile only, don't link
-g                      # Include debug symbols
-Os                     # Optimize for size
-w                      # Suppress warnings (used by Arduino)
-std=gnu11              # C11 standard with GNU extensions
-ffunction-sections     # Put functions in separate sections (for linker GC)
-fdata-sections         # Put data in separate sections
-MMD                    # Generate dependency files
-flto                   # Link-time optimization
```

### Common C++ Flags
```bash
-std=gnu++11            # C++11 standard with GNU extensions
-fpermissive            # Downgrade errors to warnings
-fno-exceptions         # Disable C++ exceptions (save space)
-fno-threadsafe-statics # Disable thread-safe static initialization
-Wno-error=narrowing    # Don't error on narrowing conversions
```

### AVR-Specific Flags
```bash
-mmcu=atmega328p        # Target microcontroller
-DF_CPU=16000000L       # CPU frequency (16 MHz)
-DARDUINO=10819         # Arduino version (1.8.19)
-DARDUINO_AVR_UNO       # Board identifier
-DARDUINO_ARCH_AVR      # Architecture identifier
```

### Linker Flags
```bash
-Wl,--gc-sections       # Garbage collect unused sections
-flto                   # Link-time optimization
-fuse-linker-plugin     # Use LTO linker plugin
-lm                     # Link math library
```

## Troubleshooting

### Windows: Missing DLL Errors
If you see missing DLL errors on Windows, ensure:
- Microsoft Visual C++ Redistributables are installed
- Windows Defender isn't blocking executables

### Linux: Permission Denied
```bash
# Make executables runnable
chmod +x .fbuild/cache/packages/avr-gcc-7.3.0-atmel3.6.1-arduino7/bin/*
```

### macOS: "Cannot be opened because the developer cannot be verified"
```bash
# Remove quarantine attribute
xattr -r -d com.apple.quarantine .fbuild/cache/packages/avr-gcc-7.3.0-atmel3.6.1-arduino7/
```

### Verification Failure
If toolchain doesn't work:
1. Delete cache directory
2. Re-download and extract
3. Check disk space
4. Verify internet connection didn't corrupt download

## References
- Arduino Package Index: https://downloads.arduino.cc/packages/package_index.json
- AVR GCC Documentation: https://gcc.gnu.org/wiki/avr-gcc
- AVR Libc Manual: https://www.nongnu.org/avr-libc/
- Arduino Build Process: https://github.com/arduino/arduino-builder

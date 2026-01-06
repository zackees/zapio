# Zapio

A modern, reliable replacement for PlatformIO that fixes all the bugs and simplifies embedded development.

[![Linting](../../actions/workflows/lint.yml/badge.svg)](../../actions/workflows/lint.yml)

[![MacOS_Tests](../../actions/workflows/push_macos.yml/badge.svg)](../../actions/workflows/push_macos.yml)
[![Ubuntu_Tests](../../actions/workflows/push_ubuntu.yml/badge.svg)](../../actions/workflows/push_ubuntu.yml)
[![Win_Tests](../../actions/workflows/push_win.yml/badge.svg)](../../actions/workflows/push_win.yml)

## What is Zapio?

Zapio is a next-generation embedded development tool designed to replace PlatformIO with a cleaner, more reliable architecture. Built from the ground up to address the pain points developers face with existing tools.

## Key Features

- **URL-based Platform & Toolchain Management**: Instead of named packages, Zapio uses direct URLs to platform files and toolchains for complete transparency and control
- **Bug-free Architecture**: Rebuilt to eliminate the common issues found in PlatformIO
- **Simplified Configuration**: Cleaner, more intuitive project setup
- **Cross-platform Support**: Works seamlessly on Windows, macOS, and Linux

## Installation

```bash
pip install zapio
```

## Quick Start

```bash
zap init my-project
cd my-project
zap build
zap upload
```

## Why Zapio over PlatformIO?

- **No more dependency hell**: Direct URL references mean you always know exactly what you're using
- **Faster builds**: Optimized build pipeline
- **Better error messages**: Clear, actionable feedback when things go wrong
- **Modern Python**: Built with current best practices and type safety

## Development

To develop Zapio, run `. ./activate.sh`

### Windows

This environment requires you to use `git-bash`.

### Linting

Run `./lint.sh` to find linting errors using `pylint`, `flake8` and `mypy`.

## License

BSD 3-Clause License

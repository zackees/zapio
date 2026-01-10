# fbuild Daemon Test Plan

## Overview

This document provides a comprehensive test plan for the fbuild daemon system, which enables concurrent deploy and monitor operations across multiple projects and devices.

**Test Status:** ⏸️ Requires physical ESP32 hardware
**Version:** 1.0
**Last Updated:** 2026-01-08

---

## Test Environment Setup

### Hardware Requirements
- 2x ESP32-C6 development boards (for concurrent testing)
- 2x USB cables
- Host computer (Windows/Linux/macOS)

### Software Requirements
- Python 3.10+
- fbuild installed (`pip install -e .`)
- ESP32 toolchains (auto-downloaded)
- Serial port access permissions

### Test Projects
- `tests/esp32c6/` - Primary test project
- `tests/esp32c6-2/` - Secondary test project (for concurrent operations)

---

## Test Categories

### 1. Basic Daemon Operations

#### Test 1.1: Daemon Auto-Start
**Objective:** Verify daemon starts automatically on first operation

**Steps:**
1. Ensure no daemon is running: `fbuild daemon status`
2. Run: `fbuild build tests/esp32c6 -e esp32c6`
3. Check daemon status: `fbuild daemon status`

**Expected Results:**
- Daemon starts transparently
- Build completes successfully
- Status shows daemon running with PID

**Success Criteria:**
- ✅ No manual daemon start required
- ✅ Daemon PID file created in `~/.fbuild/daemon.pid`
- ✅ Build operation succeeds

---

#### Test 1.2: Daemon Status Command
**Objective:** Verify daemon status reporting

**Steps:**
1. Start daemon (if not running): `fbuild build tests/esp32c6 -e esp32c6`
2. Check status: `fbuild daemon status`
3. Note PID and uptime

**Expected Results:**
- Status shows "Daemon is running" with PID
- Uptime is reasonable (< 1 hour for new daemon)

**Success Criteria:**
- ✅ Correct PID displayed
- ✅ Uptime calculation correct
- ✅ Status file contains valid JSON

---

#### Test 1.3: Daemon Stop Command
**Objective:** Verify graceful daemon shutdown

**Steps:**
1. Ensure daemon is running
2. Run: `fbuild daemon stop`
3. Wait 2 seconds
4. Check status: `fbuild daemon status`

**Expected Results:**
- Daemon stops gracefully
- Status shows "Daemon is not running"
- No orphaned processes

**Success Criteria:**
- ✅ Daemon exits within 2 seconds
- ✅ PID file removed
- ✅ No zombie processes

---

#### Test 1.4: Daemon Restart Command
**Objective:** Verify daemon restart functionality

**Steps:**
1. Start daemon (if needed)
2. Note original PID
3. Run: `fbuild daemon restart`
4. Check new status: `fbuild daemon status`
5. Compare PIDs

**Expected Results:**
- Old daemon stops
- New daemon starts
- New PID differs from old PID

**Success Criteria:**
- ✅ New PID assigned
- ✅ Daemon restarts within 5 seconds
- ✅ No orphaned processes from old daemon

---

### 2. Single Deploy Operations

#### Test 2.1: Basic Deploy
**Objective:** Verify single project deploy works

**Steps:**
1. Connect ESP32-C6 to USB port
2. Run: `fbuild deploy tests/esp32c6 -e esp32c6`
3. Wait for completion

**Expected Results:**
- Project builds successfully
- Firmware uploads to device
- Operation completes without errors

**Success Criteria:**
- ✅ Build phase succeeds
- ✅ Upload phase succeeds
- ✅ Device resets and runs firmware

---

#### Test 2.2: Deploy with Port Specification
**Objective:** Verify explicit port selection

**Steps:**
1. Connect ESP32-C6 to specific port (e.g., COM3)
2. Run: `fbuild deploy tests/esp32c6 -e esp32c6 --port COM3`

**Expected Results:**
- Deploy uses specified port
- No port auto-detection performed

**Success Criteria:**
- ✅ Deploy succeeds on specified port
- ✅ No "detecting port" messages
- ✅ Correct port shown in logs

---

#### Test 2.3: Deploy with Monitor
**Objective:** Verify deploy + monitor workflow

**Steps:**
1. Connect ESP32-C6
2. Run: `fbuild deploy tests/esp32c6 -e esp32c6 --monitor --timeout=10`
3. Observe serial output for 10 seconds

**Expected Results:**
- Deploy completes
- Monitor starts automatically
- Serial output displayed
- Monitor stops after 10 seconds

**Success Criteria:**
- ✅ Deploy phase succeeds
- ✅ Monitor phase starts immediately
- ✅ Serial output visible
- ✅ Monitor times out at ~10 seconds

---

### 3. Single Monitor Operations

#### Test 3.1: Basic Monitor
**Objective:** Verify serial monitoring works

**Steps:**
1. Ensure device is running
2. Run: `fbuild monitor tests/esp32c6 -e esp32c6 --timeout=5`
3. Observe output

**Expected Results:**
- Serial port opens
- Device output displayed
- Monitor stops after 5 seconds

**Success Criteria:**
- ✅ Port opens successfully
- ✅ Output is readable
- ✅ Timeout enforced

---

#### Test 3.2: Monitor with Pattern Matching
**Objective:** Verify monitor can detect patterns

**Steps:**
1. Deploy firmware that prints "TEST_SUCCESS"
2. Run: `fbuild monitor tests/esp32c6 -e esp32c6 --halt-on-success --timeout=30`

**Expected Results:**
- Monitor starts
- Pattern detected
- Monitor exits early (before timeout)

**Success Criteria:**
- ✅ Pattern detection works
- ✅ Early exit on match
- ✅ Exit code indicates success

---

#### Test 3.3: Monitor with Error Detection
**Objective:** Verify monitor detects error patterns

**Steps:**
1. Deploy firmware that prints "ERROR" or "FAILED"
2. Run: `fbuild monitor tests/esp32c6 -e esp32c6 --halt-on-error --timeout=30`

**Expected Results:**
- Monitor starts
- Error pattern detected
- Monitor exits early with error code

**Success Criteria:**
- ✅ Error detection works
- ✅ Early exit on error
- ✅ Exit code indicates failure

---

### 4. Concurrent Operations

#### Test 4.1: Concurrent Builds (Different Projects)
**Objective:** Verify multiple projects can build simultaneously

**Steps:**
1. Terminal 1: `fbuild build tests/esp32c6 -e esp32c6`
2. Terminal 2 (immediately): `fbuild build tests/esp32c6-2 -e esp32c6`
3. Wait for both to complete

**Expected Results:**
- Both builds run concurrently
- Both complete successfully
- No file corruption

**Success Criteria:**
- ✅ Both builds succeed
- ✅ Build times overlap
- ✅ No build conflicts

---

#### Test 4.2: Concurrent Builds (Same Project) - SHOULD FAIL
**Objective:** Verify project lock prevents concurrent builds of same project

**Steps:**
1. Terminal 1: `fbuild build tests/esp32c6 -e esp32c6`
2. Terminal 2 (immediately): `fbuild build tests/esp32c6 -e esp32c6`

**Expected Results:**
- First build proceeds
- Second build fails with "project locked" error

**Success Criteria:**
- ✅ First build succeeds
- ✅ Second build reports lock error
- ✅ No build corruption

---

#### Test 4.3: Concurrent Deploys (Different Ports)
**Objective:** Verify multiple devices can be flashed simultaneously

**Steps:**
1. Connect ESP32-C6 #1 to port COM3
2. Connect ESP32-C6 #2 to port COM4
3. Terminal 1: `fbuild deploy tests/esp32c6 -e esp32c6 --port COM3 --monitor --timeout=7`
4. Terminal 2 (immediately): `fbuild deploy tests/esp32c6-2 -e esp32c6 --port COM4 --monitor --timeout=4`
5. Wait for both to complete

**Expected Results:**
- Both deploys run concurrently
- Both monitors run after respective deploys
- No port conflicts

**Success Criteria:**
- ✅ Both deploys succeed
- ✅ Both monitors work
- ✅ No serial port conflicts
- ✅ Each uses correct port

---

#### Test 4.4: Concurrent Monitors (Different Ports)
**Objective:** Verify multiple devices can be monitored simultaneously

**Steps:**
1. Connect ESP32-C6 #1 to port COM3
2. Connect ESP32-C6 #2 to port COM4
3. Terminal 1: `fbuild monitor tests/esp32c6 -e esp32c6 --port COM3 --timeout=10`
4. Terminal 2 (immediately): `fbuild monitor tests/esp32c6-2 -e esp32c6 --port COM4 --timeout=10`

**Expected Results:**
- Both monitors run concurrently
- Each shows output from respective device
- No cross-contamination

**Success Criteria:**
- ✅ Both monitors succeed
- ✅ Output is device-specific
- ✅ No port conflicts

---

#### Test 4.5: Concurrent Monitor (Same Port) - SHOULD FAIL
**Objective:** Verify port lock prevents concurrent access to same port

**Steps:**
1. Connect ESP32-C6 to port COM3
2. Terminal 1: `fbuild monitor tests/esp32c6 -e esp32c6 --port COM3 --timeout=20`
3. Terminal 2 (immediately): `fbuild monitor tests/esp32c6-2 -e esp32c6 --port COM3 --timeout=10`

**Expected Results:**
- First monitor proceeds
- Second monitor fails with "port locked" error

**Success Criteria:**
- ✅ First monitor succeeds
- ✅ Second monitor reports lock error
- ✅ No serial port corruption

---

### 5. Signal Handling

#### Test 5.1: Ctrl-C During Deploy (Detach)
**Objective:** Verify Ctrl-C can detach from ongoing deploy

**Steps:**
1. Run: `fbuild deploy tests/esp32c6 -e esp32c6 --monitor --timeout=30`
2. Press Ctrl-C after 5 seconds
3. When prompted, type 'y' (keep running)
4. Check daemon status: `fbuild daemon status`

**Expected Results:**
- Prompt appears: "Keep operation running in background? (y/n)"
- Client exits
- Daemon continues operation
- Status shows operation still running

**Success Criteria:**
- ✅ Client detaches cleanly
- ✅ Daemon continues operation
- ✅ Operation completes successfully

---

#### Test 5.2: Ctrl-C During Deploy (Cancel)
**Objective:** Verify Ctrl-C can signal cancellation

**Steps:**
1. Run: `fbuild deploy tests/esp32c6 -e esp32c6 --monitor --timeout=30`
2. Press Ctrl-C after 5 seconds
3. When prompted, type 'n' (cancel)
4. Wait for operation to complete

**Expected Results:**
- Prompt appears
- Cancel signal file created
- Daemon detects signal
- Operation cleanup performed

**Success Criteria:**
- ✅ Cancel signal created
- ✅ Daemon logs "cancel signal detected"
- ✅ Cleanup performed
- ✅ Signal file removed after detection

---

#### Test 5.3: Ctrl-C During Monitor (Detach)
**Objective:** Verify Ctrl-C detach works during monitor

**Steps:**
1. Run: `fbuild monitor tests/esp32c6 -e esp32c6 --timeout=60`
2. Press Ctrl-C after 10 seconds
3. Type 'y' (keep running)
4. Check daemon status

**Expected Results:**
- Client exits
- Daemon continues monitoring
- Monitor times out after full duration

**Success Criteria:**
- ✅ Client detaches
- ✅ Monitor continues
- ✅ Full timeout honored

---

#### Test 5.4: Multiple Ctrl-C (Rapid)
**Objective:** Verify rapid Ctrl-C doesn't cause issues

**Steps:**
1. Run: `fbuild deploy tests/esp32c6 -e esp32c6 --monitor --timeout=30`
2. Press Ctrl-C 3 times rapidly
3. Respond to prompt

**Expected Results:**
- Only one prompt appears
- Subsequent Ctrl-C ignored or queued
- Operation handles signal cleanly

**Success Criteria:**
- ✅ No duplicate prompts
- ✅ Clean signal handling
- ✅ No corruption

---

### 6. Error Scenarios

#### Test 6.1: Deploy with No Device Connected
**Objective:** Verify graceful failure when device missing

**Steps:**
1. Disconnect all ESP32 devices
2. Run: `fbuild deploy tests/esp32c6 -e esp32c6`

**Expected Results:**
- Deploy fails with clear error message
- Error indicates no device found
- No daemon crash

**Success Criteria:**
- ✅ Clear error message
- ✅ Daemon remains stable
- ✅ Client exits cleanly

---

#### Test 6.2: Monitor with Invalid Port
**Objective:** Verify handling of invalid port specification

**Steps:**
1. Run: `fbuild monitor tests/esp32c6 -e esp32c6 --port INVALID_PORT`

**Expected Results:**
- Monitor fails with error
- Error indicates port invalid/unavailable

**Success Criteria:**
- ✅ Clear error message
- ✅ Daemon stable
- ✅ No crash

---

#### Test 6.3: Deploy with Build Errors
**Objective:** Verify handling of compilation failures

**Steps:**
1. Introduce syntax error in `tests/esp32c6/src/main.cpp`
2. Run: `fbuild deploy tests/esp32c6 -e esp32c6`
3. Fix syntax error

**Expected Results:**
- Build fails with compiler error
- Error message shows compilation issue
- No upload attempted

**Success Criteria:**
- ✅ Build fails gracefully
- ✅ Compiler errors visible
- ✅ No firmware upload

---

#### Test 6.4: Stale PID File Recovery
**Objective:** Verify daemon recovers from stale PID file

**Steps:**
1. Start daemon
2. Kill daemon process forcefully (SIGKILL)
3. Run: `fbuild build tests/esp32c6 -e esp32c6`

**Expected Results:**
- Stale PID detected
- New daemon starts
- Build succeeds

**Success Criteria:**
- ✅ Stale PID detection works
- ✅ New daemon starts
- ✅ PID file updated

---

#### Test 6.5: Corrupt Status File Recovery
**Objective:** Verify handling of corrupted status file

**Steps:**
1. Start daemon and begin operation
2. Manually corrupt status file (invalid JSON)
3. Check status: `fbuild daemon status`

**Expected Results:**
- Corruption detected
- Error message indicates corruption
- System recovers on next operation

**Success Criteria:**
- ✅ Corruption detected
- ✅ Error logged
- ✅ Recovery possible

---

### 7. Performance Tests

#### Test 7.1: Incremental Build Performance
**Objective:** Measure incremental build time

**Steps:**
1. Clean build: `fbuild build tests/esp32c6 -e esp32c6 --clean`
2. Note time
3. No-change rebuild: `fbuild build tests/esp32c6 -e esp32c6`
4. Note time
5. Change one line in main.cpp
6. Rebuild: `fbuild build tests/esp32c6 -e esp32c6`
7. Note time

**Expected Results:**
- Clean build: ~10-20 seconds
- No-change rebuild: < 1 second
- Single-file rebuild: < 2 seconds

**Success Criteria:**
- ✅ No-change build very fast (< 1s)
- ✅ Incremental build fast (< 3s)
- ✅ Full build reasonable (< 30s)

---

#### Test 7.2: Daemon Memory Usage
**Objective:** Verify daemon doesn't leak memory

**Steps:**
1. Start daemon
2. Note memory usage (via task manager/htop)
3. Run 10 deploy operations
4. Check memory usage again

**Expected Results:**
- Memory stable or grows minimally
- No significant memory leak

**Success Criteria:**
- ✅ Memory < 100MB total
- ✅ Memory growth < 10MB per 10 operations
- ✅ No zombie processes

---

#### Test 7.3: Concurrent Operation Performance
**Objective:** Measure performance impact of concurrency

**Steps:**
1. Sequential: Deploy two projects one after another, note total time
2. Concurrent: Deploy two projects simultaneously (different ports), note total time

**Expected Results:**
- Concurrent time < sequential time
- Both operations complete successfully

**Success Criteria:**
- ✅ Concurrent faster than sequential
- ✅ No performance degradation
- ✅ Both succeed

---

### 8. Long-Running Operations

#### Test 8.1: Long Monitor Session
**Objective:** Verify monitor can run for extended periods

**Steps:**
1. Run: `fbuild monitor tests/esp32c6 -e esp32c6 --timeout=300` (5 minutes)
2. Let run to completion

**Expected Results:**
- Monitor runs for full 5 minutes
- Output continuously displayed
- Clean exit after timeout

**Success Criteria:**
- ✅ Monitor runs full duration
- ✅ No connection drops
- ✅ Clean timeout exit

---

#### Test 8.2: Daemon Idle Timeout
**Objective:** Verify daemon auto-exits after idle period

**Steps:**
1. Start daemon
2. Wait 12 hours (or modify timeout for testing)
3. Check status

**Expected Results:**
- Daemon exits after idle timeout
- Status shows "not running"

**Success Criteria:**
- ✅ Daemon exits at configured timeout
- ✅ Clean shutdown
- ✅ No orphaned processes

---

#### Test 8.3: Cancel Signal Cleanup
**Objective:** Verify stale cancel signals are cleaned up

**Steps:**
1. Start operation
2. Press Ctrl-C and cancel (create signal file)
3. Manually prevent daemon from cleaning up (pause daemon)
4. Wait 6 minutes
5. Resume daemon
6. Check signal directory

**Expected Results:**
- Stale signals (> 5 minutes) removed
- Recent signals (< 5 minutes) kept

**Success Criteria:**
- ✅ Stale signals cleaned up
- ✅ Cleanup runs periodically
- ✅ No accumulation

---

## Test Execution Checklist

### Pre-Test Setup
- [ ] Install fbuild (`pip install -e .`)
- [ ] Install dependencies (`pip install -r requirements.txt`)
- [ ] Connect ESP32 devices
- [ ] Verify serial port permissions
- [ ] Stop any running daemon (`fbuild daemon stop`)

### Test Execution
- [ ] Run Basic Daemon Operations (Tests 1.1-1.4)
- [ ] Run Single Deploy Operations (Tests 2.1-2.3)
- [ ] Run Single Monitor Operations (Tests 3.1-3.3)
- [ ] Run Concurrent Operations (Tests 4.1-4.5)
- [ ] Run Signal Handling (Tests 5.1-5.4)
- [ ] Run Error Scenarios (Tests 6.1-6.5)
- [ ] Run Performance Tests (Tests 7.1-7.3)
- [ ] Run Long-Running Operations (Tests 8.1-8.3)

### Post-Test Cleanup
- [ ] Stop daemon (`fbuild daemon stop`)
- [ ] Remove test artifacts
- [ ] Document any failures
- [ ] Log performance metrics

---

## Test Results Template

```
Test ID: [e.g., 4.3]
Test Name: [e.g., Concurrent Deploys (Different Ports)]
Date: [YYYY-MM-DD]
Tester: [Name]
Hardware: [Device models, ports]

Steps Executed:
1. [Step 1]
2. [Step 2]
...

Actual Results:
[Describe what happened]

Pass/Fail: [PASS/FAIL]

Notes:
[Any observations, issues, or recommendations]
```

---

## Known Limitations

1. **Hardware Dependency:** All deploy/monitor tests require physical devices
2. **Port Availability:** Some tests require multiple serial ports
3. **Timing Sensitivity:** Concurrent tests may have race conditions
4. **Platform Differences:** Windows/Linux/macOS may behave differently

---

## Test Automation Potential

### High Priority for Automation
- Basic daemon operations (1.1-1.4)
- Build-only operations
- Status file validation
- Lock mechanism unit tests

### Difficult to Automate
- Serial port operations (hardware required)
- Concurrent deploy tests (multiple devices)
- Signal handling (interactive prompts)

### Mock Testing Opportunities
- Deploy operations (mock esptool)
- Monitor operations (mock serial port)
- Port detection (mock serial.tools.list_ports)

---

## Success Metrics

### Overall Success Criteria
- ✅ 100% of basic operations pass
- ✅ 90%+ of concurrent operations pass
- ✅ All error scenarios handled gracefully
- ✅ No memory leaks or crashes
- ✅ Performance meets targets

### Performance Targets
- No-change rebuild: < 1 second
- Incremental rebuild: < 3 seconds
- Daemon memory: < 100MB
- Concurrent overhead: < 20%

---

## Appendix: Troubleshooting

### Common Issues

**Issue:** Daemon won't start
- Check PID file: `~/.fbuild/daemon.pid`
- Check daemon logs
- Verify Python installation

**Issue:** Port locked error
- Check for stale daemon: `fbuild daemon status`
- Restart daemon: `fbuild daemon restart`
- Check for other programs using port

**Issue:** Operation hangs
- Press Ctrl-C to detach
- Check daemon status
- Stop daemon if needed

**Issue:** Concurrent test fails
- Verify devices on different ports
- Check port names in commands
- Ensure proper USB connections

---

## Document Revision History

- **v1.0** (2026-01-08): Initial test plan created

# UNIBOS Platform Detection

**Created:** 2025-11-15
**Status:** Implemented
**Version:** v533+
**Phase:** 1.2

## Overview

UNIBOS platform detection system provides comprehensive cross-platform identification for OS, hardware, device type, and capabilities. Built with `psutil` for robust system monitoring.

## Features

### OS Detection
- **OS Type:** darwin, linux, windows
- **OS Name:** macOS, Ubuntu, Debian, Raspbian, Windows
- **Version:** Detailed OS version information
- **Architecture:** x86_64, arm64, aarch64, armv7l

### Device Classification
- **server:** High-spec Linux systems (4GB+ RAM)
- **desktop:** macOS, Windows workstations
- **raspberry_pi:** Raspberry Pi devices (auto-detected)
- **edge:** Low-spec Linux devices

### Hardware Specifications
- CPU cores (physical and logical)
- CPU frequency (MHz)
- RAM (total and available in GB)
- Disk space (total and free in GB)

### Capabilities Detection
- **GPU:** NVIDIA (nvidia-smi), macOS (integrated), Raspberry Pi (VideoCore)
- **Camera:** Video devices (/dev/video*), macOS detection
- **GPIO:** Raspberry Pi only
- **LoRa:** SPI device detection (Phase 5 enhancement planned)

### Network Information
- Hostname
- Local IP address

### Raspberry Pi Detection

Special detection for Raspberry Pi models:
- Reads `/proc/device-tree/model` for model identification
- Fallback to `/proc/cpuinfo` for BCM detection
- Model extraction: 4B, 5, Zero 2W, etc.

## CLI Usage

### Basic Information
```bash
# Production CLI
unibos platform

# Developer CLI
unibos-dev platform
```

### Verbose Mode
```bash
unibos platform --verbose

# Shows additional information:
# - CPU frequency
# - Server suitability check
# - Edge device suitability check
```

### JSON Output
```bash
unibos platform --json

# Returns complete platform info as JSON
# Useful for automation and scripting
```

## Example Output

### Standard Output
```
🖥️  Platform Information

System:
  OS: macOS 24.6.0
  Architecture: arm64
  Device Type: desktop
  Hostname: mbp16m4max.local
  Local IP: 192.168.0.124

Hardware:
  CPU Cores: 14 physical, 14 logical
  RAM: 15.8 GB / 36.0 GB available
  Disk: 48.3 GB / 926.4 GB free

Capabilities:
  GPU: Yes
  Camera: Yes
```

### Verbose Output
```
🖥️  Platform Information

System:
  OS: macOS 24.6.0
  Architecture: arm64
  Device Type: desktop
  Hostname: mbp16m4max.local
  Local IP: 192.168.0.124

Hardware:
  CPU Cores: 14 physical, 14 logical
  CPU Frequency: 4056 MHz
  RAM: 15.8 GB / 36.0 GB available
  Disk: 48.3 GB / 926.4 GB free

Capabilities:
  GPU: Yes
  Camera: Yes

Suitability:
  Server: ✓
  Edge Device: ✓
```

### JSON Output
```json
{
  "os_type": "darwin",
  "os_name": "macOS",
  "os_version": "24.6.0",
  "architecture": "arm64",
  "device_type": "desktop",
  "is_raspberry_pi": false,
  "cpu_count": 14,
  "cpu_count_logical": 14,
  "cpu_freq_mhz": 4056,
  "ram_total_gb": 36.0,
  "ram_available_gb": 15.8,
  "disk_total_gb": 926.4,
  "disk_free_gb": 48.3,
  "has_gpu": true,
  "has_camera": true,
  "has_gpio": false,
  "has_lora": false,
  "hostname": "mbp16m4max.local",
  "raspberry_pi_model": null,
  "local_ip": "192.168.0.124"
}
```

## Raspberry Pi Example

```
🖥️  Platform Information

System:
  OS: Raspbian GNU/Linux 11
  Architecture: aarch64
  Device Type: raspberry_pi
  Hostname: raspberrypi.local
  Local IP: 192.168.0.50

Raspberry Pi:
  Model: 4 Model B
  GPIO: Available

Hardware:
  CPU Cores: 4 physical, 4 logical
  RAM: 2.8 GB / 3.8 GB available
  Disk: 15.2 GB / 29.7 GB free

Capabilities:
  GPU: Yes
  Camera: Yes
  LoRa: No
```

## Python API

```python
from core.platform import PlatformDetector

# Detect platform
info = PlatformDetector.detect()

# Access properties
print(f"OS: {info.os_name} {info.os_version}")
print(f"Device Type: {info.device_type}")
print(f"Is Raspberry Pi: {info.is_raspberry_pi}")

# Check suitability
if info.is_suitable_for_server():
    print("This device can run as a server")

if info.is_suitable_for_edge():
    print("This device can run as an edge node")

# Export to dict/JSON
data = info.to_dict()
import json
print(json.dumps(data, indent=2))
```

## Suitability Checks

### Server Suitability
Device is suitable for server deployment if:
- RAM ≥ 2.0 GB
- Free disk ≥ 10.0 GB
- CPU cores ≥ 2

### Edge Device Suitability
Device is suitable for edge deployment if:
- RAM ≥ 1.0 GB
- Free disk ≥ 5.0 GB

## Implementation Details

### File Structure
```
core/platform/
├── __init__.py          # Module exports
└── detector.py          # PlatformDetector and PlatformInfo classes
```

### Dependencies
- **psutil>=5.9.0** - System and process monitoring
- Built-in: platform, subprocess, pathlib

### Detection Methods

#### OS Detection
1. `platform.system()` - OS type (Darwin, Linux, Windows)
2. `/etc/os-release` - Linux distribution name (Ubuntu, Debian, etc.)
3. `platform.release()` - OS version

#### Raspberry Pi Detection
1. Primary: Read `/proc/device-tree/model`
2. Fallback: Check `/proc/cpuinfo` for "Raspberry Pi" or "BCM"
3. Model extraction from model string

#### GPU Detection
1. **NVIDIA:** Run `nvidia-smi` command
2. **macOS:** Assume integrated GPU
3. **Raspberry Pi:** Check for `/dev/vchiq` (VideoCore)

#### Camera Detection
1. **Linux:** Glob `/dev/video*` devices
2. **macOS:** Assume camera exists

#### LoRa Detection
1. Check for SPI devices: `/dev/spidev*`
2. Phase 5 enhancement: Specific SX1276/SX1278 detection

## Future Enhancements (Phase 5)

- [ ] Detailed Raspberry Pi hardware detection (RAM size, model revision)
- [ ] LoRa module specific detection (SX1276, SX1278)
- [ ] GPIO capability verification
- [ ] Sensor detection (DHT22, BME280)
- [ ] Camera model identification
- [ ] Storage device type (SD card, SSD, HDD)
- [ ] Network interface capabilities (WiFi, Ethernet, 4G/5G)

## Related Documentation

- [Three-Tier CLI Architecture](../cli/three-tier-architecture.md)
- [TODO.md - Phase 1.2](../../../TODO.md#phase-12-platform-detection-foundation)
- [Raspberry Pi Integration Plan](../../deployment/raspberry-pi-guide.md) (planned)

---

**Last Updated:** 2025-11-15
**Next Review:** After Phase 2 completion

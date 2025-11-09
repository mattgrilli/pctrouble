# BF6 Crash Monitor - Enhanced Edition

**AMD & NVIDIA GPU + Windows 11 Edition with Real-Time Monitoring**

A comprehensive diagnostic tool to help troubleshoot Battlefield 6 crashes, with special focus on AMD GPU issues, NVIDIA GPU monitoring, EA Javelin anticheat, and Windows 11 compatibility.

## ✨ Features

### Real-Time Monitoring Dashboard
- 🎮 **BF6 Process Detection** - Auto-detects when game starts/crashes
- 🛡️ **EA Javelin Anticheat Monitoring** - Tracks anticheat status
- 🎨 **GPU Detection** - AMD and NVIDIA support with driver info
- 📊 **Live System Stats** - CPU, RAM usage with color-coded warnings
- 💥 **Crash Counter** - Tracks number of crashes per session

### Advanced Diagnostics
- ⚡ **HAGS Detection** - Warns if Hardware-Accelerated GPU Scheduling is enabled (major crash cause for AMD)
- 🔍 **Windows Event Log Analysis** - Scans for TDR timeouts, driver crashes
- 🎯 **Instant Crash Analysis** - Immediate recommendations after each crash
- 📝 **Detailed JSON Reports** - Complete crash data saved for deeper analysis

### Smart Analysis
- 🔴 **GPU TDR Detection** - Identifies timeout/recovery issues
- 🟡 **Driver Crash Detection** - AMD (amduw, atikmdag) and NVIDIA (nvlddmkm) specific
- 🟢 **Anticheat Issue Detection** - EA Javelin conflicts
- 🔵 **Memory/CPU Warnings** - High resource usage alerts

## 📦 Quick Start

### For End Users (Easiest)

1. **Run the executable**: `BF6CrashMonitor.exe`
   - Right-click → "Run as Administrator" recommended

2. **Click "▶ Start Monitoring"**

3. **Launch BF6** and play normally

4. **When crash occurs**, check the Activity Log for:
   - Issues found
   - Instant recommendations
   - Full report location

### For Developers

```bash
# Install dependencies
pip install psutil

# Run the monitor
python crash_monitor.py
```

## 🔨 Building the Executable

```bash
# One-line build
build.bat

# Manual build
pip install psutil pyinstaller
pyinstaller --onefile --windowed --name "BF6CrashMonitor" crash_monitor.py
```

The executable will be in `dist\BF6CrashMonitor.exe`

## 📊 What You'll See

### System Status Panel
```
BF6 Status:         🟢 Running / ⚫ Not Running
EA Javelin:         ✓ Running / ✗ Not Running
GPU:                AMD Radeon RX 6800 XT
CPU Usage:          45.2%
RAM Usage:          68.5% (10.9GB)
Crashes Detected:   2
```

### Activity Log Sample
```
[14:30:15] [INFO] 🚀 Monitor started - waiting for BF6...
[14:30:15] [INFO] GPU: AMD Radeon RX 6800 XT
[14:30:15] [INFO] Driver: 31.0.14057.5006
[14:30:16] [WARNING] ⚠️ WARNING: HAGS is enabled - may cause crashes!
[14:31:42] [INFO] 🎮 BF6 DETECTED - Monitoring active!
[14:45:33] [CRITICAL] 💥 BF6 CRASHED!
[14:45:34] [WARNING] ⚠️ HAGS is ENABLED - disable it!
[14:45:34] [WARNING] ⚠️ GPU Timeout (TDR) detected
[14:45:34] [INFO] 💡 AMD + HAGS = frequent crashes
[14:45:34] [INFO] 💡 Increase TDR timeout in registry
```

## 🔧 Common Issues & Fixes

### AMD GPU Crashes

**#1 Issue: HAGS Enabled**
- ⚠️ Most common cause for AMD crashes
- Fix: Settings → Display → Graphics → Turn OFF "Hardware-accelerated GPU scheduling"
- Restart required

**#2 Issue: GPU TDR (Timeout)**
- Symptom: "Display driver stopped responding"
- Fix: Increase TDR timeout via registry
- Alternative: Lower graphics settings

**#3 Issue: Driver Version**
- Try latest AMD drivers (clean install with DDU)
- Or rollback to stable version (23.11.1)
- Disable AMD overlay, Anti-Lag, Boost, Enhanced Sync

### NVIDIA GPU Crashes

**Check:**
- Latest NVIDIA drivers installed
- Shader cache cleared
- No overclocking conflicts

### Anticheat Issues

**If EA Javelin shows "✗ Not Running":**
- Verify game files
- Reinstall anticheat from game folder
- Close RGB software (iCue, SignalRGB)
- Close monitoring tools

## 📁 Output Files

### Crash Reports Location
`crash_logs/crash_report_YYYYMMDD_HHMMSS.json`

### Report Contents
```json
{
  "crash_number": 1,
  "crash_time": "20251108_143045",
  "pre_crash_snapshot": {
    "cpu_percent": 72.5,
    "memory": { "percent": 68.2, "used_gb": 10.9 },
    "gpu_info": {
      "Name": "AMD Radeon RX 6800 XT",
      "DriverVersion": "31.0.14057.5006",
      "Vendor": "AMD"
    },
    "hags_enabled": true,
    "anticheat_process": { "name": "JavelinAC.exe", "pid": 12345 }
  },
  "windows_event_logs": [...],
  "quick_analysis": {
    "issues": [
      "⚠️ HAGS is ENABLED - disable it!",
      "⚠️ GPU Timeout (TDR) detected"
    ],
    "recommendations": [
      "AMD + HAGS = frequent crashes",
      "Increase TDR timeout in registry",
      "AMD: Disable Anti-Lag, Boost, Enhanced Sync"
    ]
  }
}
```

## 🎯 What Gets Detected

### Process Monitoring
- `bf6.exe` (custom builds)
- `bf2042.exe` (standard)
- `Battlefield2042.exe` (alternate)

### Anticheat Monitoring
- `JavelinAC.exe`
- `Javelin.exe`
- `EAAntiCheat.GameService.exe`
- `EAAntiCheat.GameServiceLauncher.exe`

### GPU Vendors
- AMD (Radeon, RX series)
- NVIDIA (GeForce, RTX, GTX)

### Event Log Keywords
- TDR (Timeout Detection Recovery)
- Driver crashes (amduw, atikmdag, nvlddmkm)
- Javelin errors
- Application crashes

## 💡 Tips

1. **Run as Administrator** - Required for full Event Log access
2. **Keep monitoring during gaming** - Don't close it
3. **Check HAGS first** - #1 fix for AMD users
4. **Save crash reports** - Share with support if needed
5. **Look for patterns** - Multiple crashes with same issue = clear cause

## 🐛 Troubleshooting

### "Not getting any data"
- Make sure BF6 is running
- Try running as Administrator
- Check if psutil is installed

### "GPU not detected"
- Tool uses WMIC - should work on all Windows
- Will continue monitoring even if GPU info fails

### "Anticheat shows not running but game works"
- Some versions may use different process names
- Check crash reports for actual process list

## 📋 Technical Details

### Dependencies
- `psutil` - System monitoring
- `tkinter` - GUI (built into Python)
- `winreg` - HAGS detection
- Standard library: json, subprocess, threading, pathlib

### System Requirements
- Windows 10/11
- Python 3.7+ (for running from source)
- Administrator rights (recommended)

### Performance
- Updates every 2 seconds
- Low CPU overhead (<1%)
- Minimal memory footprint (~50MB)

## 📤 Sharing with Friends

Send these files:
1. `BF6CrashMonitor.exe` - The program
2. `QUICK_START.txt` - Simple instructions

They don't need Python installed!

## 🆘 Support

If crashes continue after trying all fixes:
1. Share the JSON crash reports
2. Include GPU model and driver version
3. Note if HAGS was enabled
4. List any recent changes (drivers, Windows updates)

## 📜 License

Free to use and modify. Provided as-is with no warranty.

---

**Note**: This tool is for diagnostic purposes. Always keep your drivers and game updated, and verify game files regularly.

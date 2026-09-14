# CSK4 - WiFi Deauthentication Tool

A complete WiFi deauthentication tool for authorized security testing and network administration on Kali Linux.

![Version](https://img.shields.io/badge/version-1.0-blue)
![Python](https://img.shields.io/badge/python-3-green)
![License](https://img.shields.io/badge/license-MIT-orange)

> ⚠️ **WARNING**: This tool is designed for authorized security testing and network administration only. Unauthorized access to computer systems is illegal. Use responsibly and only on networks you own or have explicit permission to test.

## Features

✨ **Auto-Scan**: Automatically detects and lists all available WiFi networks  
🎯 **Smart Selection**: Easy network selection from scanned results  
🔌 **Automatic Monitor Mode**: Enables monitor mode automatically on your wireless interface  
⚡ **Flexible Deauth**: Send single or continuous deauth packets  
🧹 **Auto Cleanup**: Automatically cleans up temporary files and restores network settings  
🌈 **Colored Output**: Beautiful terminal interface with color-coded signal strength  
✅ **Dependency Check**: Verifies all required tools are installed  

## Prerequisites

### Required Tools
- **aircrack-ng suite**:
  - `aireplay-ng` - For sending deauth packets
  - `airmon-ng` - For monitor mode management
  - `airodump-ng` - For network scanning
- **wireless-tools**:
  - `iwconfig` - Wireless interface configuration

### System Requirements
- Linux-based OS (Kali Linux recommended)
- Root/sudo privileges
- Wireless adapter capable of monitor mode
- Python 3.6+

## Installation

### 1. Install Dependencies

**On Kali Linux / Debian-based systems:**
```bash
sudo apt-get update
sudo apt-get install aircrack-ng wireless-tools -y
```

**On Arch Linux:**
```bash
sudo pacman -S aircrack-ng wireless_tools -y
```

### 2. Clone and Run

```bash
git clone https://github.com/cryptixshadowkernel-org/csk4_wifi_deauth.git
cd csk4_wifi_deauth
sudo python3 csk4.py
```

## Usage

### Basic Usage
```bash
sudo python3 csk4.py
```

### Workflow

1. **Auto Detection**: The tool automatically detects your wireless interface
2. **Scan Networks**: Scans for available WiFi networks (7 seconds by default)
3. **Select Target**: Choose the network to test from the displayed list
4. **Set Deauth Count**: 
   - Enter a number (1-10000) for specific packet count
   - Enter `0` for continuous deauth (press Ctrl+C to stop)
   - Press Enter for default (100 packets)
5. **Confirm Attack**: Review settings and confirm before starting
6. **Continue or Exit**: After attack, choose to rescan, attack again, or exit

### Example Session

```
╔═══════════════════════════════════════════╗
║                                           ║
║     ██████ ███████ ██   ██ ██   ██      ║
║    ██      ██      ██  ██  ██   ██      ║
║    ██      ███████ █████   ███████      ║
║    ██           ██ ██  ██       ██      ║
║     ██████ ███████ ██   ██      ██      ║
║                                           ║
╚═══════════════════════════════════════════╝

[*] Detecting wireless interface...
[✓] Interface: wlan0

[*] Enabling monitor mode on wlan0...
[✓] Monitor mode: wlan0mon

[*] Scanning for WiFi networks... (please wait 7 sec)
[✓] Scan complete!

╔═══════════════════════════════════════════════════════════════════════════╗
║ #    BSSID              CH   PWR   ENC          ESSID                     ║
║═══════════════════════════════════════════════════════════════════════════║
║ 1    AA:BB:CC:DD:EE:FF  6    -35  WPA2         MyRouter                   ║
║ 2    11:22:33:44:55:66  11   -42  Open         Guest Network              ║
║ 3    FF:EE:DD:CC:BB:AA  1    -67  WPA2         <Hidden SSID>              ║
╚═══════════════════════════════════════════════════════════════════════════╝

[?] Select network number (1-3): 1
[✓] Selected: MyRouter (AA:BB:CC:DD:EE:FF)

How many deauth packets to send?
  • Enter a number (1-10000)
  • Enter 0 for continuous (infinite)
  • Press Enter for default: 100

[?] Count: 0

═══════════════════════════════════════════
  Target BSSID : AA:BB:CC:DD:EE:FF
  Deauth Mode  : CONTINUOUS (Ctrl+C to stop)
  Interface    : wlan0mon
═══════════════════════════════════════════

[!] Start attack? (y/N): y

[+] Starting deauth attack...
[*] Sending deauth continuously. Press Ctrl+C to stop.
```

## Configuration

### Environment Variables
None currently used. Modify settings directly in the code:

- **Monitor Scan Duration**: Line 159 `def scan_networks(iface, duration=7):`
- **Default Deauth Count**: Line 345 `return 100`
- **Color Codes**: Lines 19-27

### Important Constants

| Variable | Purpose |
|----------|---------|
| `VERSION` | Tool version string |
| `MON_INTERFACE` | Current monitor mode interface |
| `ORIGINAL_INTERFACE` | Original WiFi adapter name |
| `MON_CLEANUP_NEEDED` | Flag for cleanup operations |

## Signal Strength Indicators

The tool color-codes signal strength for easy identification:

- 🟢 **Green** (-50 dBm or higher): Excellent signal
- 🟡 **Yellow** (-50 to -70 dBm): Good signal
- 🔴 **Red** (Below -70 dBm): Weak signal

## Troubleshooting

### "Root privileges required!"
```bash
# Run with sudo
sudo python3 csk4.py
```

### "Missing tools: aireplay-ng, airmon-ng, airodump-ng"
```bash
# Install aircrack-ng suite
sudo apt-get install aircrack-ng -y
```

### "No wireless interface found!"
- Verify your wireless adapter is connected: `iwconfig`
- Check if adapter supports monitor mode: `sudo airmon-ng`
- Try a USB WiFi adapter if built-in adapter doesn't work

### Deauth packets not working
- Verify target network is in range
- Check if monitor mode is active: `iwconfig | grep Monitor`
- Try increasing the packet count
- Some modern devices may filter excessive deauth frames

### "Scan failed - no CSV output generated"
- Check if monitor mode is properly enabled
- Restart the tool
- Kill interfering processes: `sudo airmon-ng check kill`

## How It Works

### 1. **Interface Detection**
- Detects wireless interface using `iw dev` or `iwconfig`
- Identifies the primary WiFi adapter

### 2. **Monitor Mode Activation**
- Kills interfering processes with `airmon-ng check kill`
- Enables monitor mode using `airmon-ng start`
- Verifies monitor mode is active

### 3. **Network Scanning**
- Runs `airodump-ng` in background
- Outputs results to CSV format
- Parses CSV to extract network details (BSSID, channel, power, encryption, ESSID)
- Removes duplicates and sorts by signal strength

### 4. **Deauthentication**
- Builds `aireplay-ng` command with target BSSID
- Sends deauth frames (802.11 deauthentication packets)
- Supports fixed count or continuous mode

### 5. **Cleanup**
- Restores monitor interface to managed mode
- Removes temporary CSV files
- Restarts NetworkManager
- Restores system to original state

## Key Functions

| Function | Purpose |
|----------|---------|
| `check_root()` | Verifies root privileges |
| `check_deps()` | Validates required tools |
| `detect_interface()` | Finds wireless adapter |
| `enable_monitor()` | Activates monitor mode |
| `scan_networks()` | Scans for WiFi networks |
| `display_networks()` | Shows formatted network list |
| `get_selection()` | Gets user's target choice |
| `send_deauth()` | Performs deauth attack |
| `cleanup()` | Restores system state |

## Legal & Ethical Use

### Permitted Uses ✅
- Testing your own networks and devices
- Authorized penetration testing (with written permission)
- Educational purposes in controlled environments
- Network administration and troubleshooting

### Prohibited Uses ❌
- Unauthorized access to networks you don't own
- Disrupting services without permission
- Malicious attacks on others' infrastructure
- Violation of local laws and regulations

**Always obtain proper authorization before using this tool on any network.**

## Technical Details

### WiFi Deauthentication Packets
- **Frame Type**: 802.11 Management Frame - Deauthentication (0xC0)
- **Reason Code**: Typically "Previous authentication no longer valid" (2)
- **Target**: All stations connected to target BSSID
- **Effect**: Forces clients to disconnect and reassociate

### Monitor Mode
- Allows capturing and injecting raw 802.11 frames
- Bypasses normal WiFi filtering
- Required for packet injection operations

## Dependencies Details

```bash
# Check installed tools
which aireplay-ng airmon-ng airodump-ng iwconfig

# Manual installation (Debian/Ubuntu)
sudo apt-get install aircrack-ng wireless-tools

# Verify installation
airmon-ng --version
aireplay-ng --version
airodump-ng --version
```

## Performance Tips

- **Faster Scanning**: Use 5 GHz networks (less interference)
- **Better Results**: Position closer to target network
- **Stronger Signal**: Use external WiFi adapter with better antenna
- **Reliability**: Run on Kali Linux (optimized for WiFi testing)

## Support & Contribution

### Report Issues
For bugs or feature requests, please open an issue on GitHub.

### Contribute
Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Submit a pull request

## License

This project is released under the MIT License. See LICENSE file for details.

## Disclaimer

**This tool is provided for educational and authorized testing purposes only.** The authors are not responsible for misuse or damages caused by this tool. Users are solely responsible for ensuring they have proper authorization before using this tool on any network.

---

**⚠️ Always get written permission before conducting security tests on systems you don't own.**

**Last Updated**: 2026  
**Author**: CSK4 Development Team  
**Status**: Active Development

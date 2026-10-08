import network
import urequests
import json
import os
import time
import machine

# --- Configuration ---
WIFI_SSID = "EWIS"
WIFI_PASSWORD = "onion321"

# Point to the raw file on GitHub or your local server
# The URL should end with a /
OTA_BASE_URL = "https://raw.githubusercontent.com/sspathirana/pico-ota-test/refs/heads/main/"
VERSION_FILE = "version.json"
APP_FILE = "main.py"
led = machine.Pin("LED", machine.Pin.OUT)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print("Waiting for connection...")
        time.sleep(1)
        
    if wlan.status() != 3:
        raise RuntimeError("WiFi connection failed")
        
    print("Connected. IP:", wlan.ifconfig()[0])
    return True

def check_for_update():
    print("Checking for updates...")
    try:
        # Fetch the remote version file
        response = urequests.get(OTA_BASE_URL + VERSION_FILE)
        remote_version = json.loads(response.text)['version']
        response.close()
        
        # Read local version
        local_version = 0
        if VERSION_FILE in os.listdir():
            with open(VERSION_FILE, 'r') as f:
                local_version = json.load(f)['version']
                
        print(f"Local: {local_version}, Remote: {remote_version}")
        
        if remote_version > local_version:
            print("New version found! Downloading...")
            # Download new main.py
            r = urequests.get(OTA_BASE_URL + APP_FILE)
            with open(APP_FILE, 'w') as f:
                f.write(r.text)
            r.close()
            
            # Update local version file
            with open(VERSION_FILE, 'w') as f:
                json.dump({'version': remote_version}, f)
            
            print("Update successful. Restarting...")
            time.sleep(2)
            machine.reset()
        else:
            print("Firmware is up to date.")
            
    except Exception as e:
        print("Update check failed:", e)

# --- Main Test Flow ---
if connect_wifi():
    check_for_update()
    print("Running application normally...")
    # Your normal application code goes here
while True:
    led.toggle()        # Flip the LED state (ON to OFF, OFF to ON)
    time.sleep(1)       # Wait for 1 second


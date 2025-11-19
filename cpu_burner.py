# cpu_burner.py
# WARNING: This script will genuinely spike your CPU usage to 100%.
# Argus is designed to detect and KILL this script.

import time
import os

def stress_cpu():
    print(f"🔥 CPU BURNER STARTED (PID: {os.getpid()})")
    print("   I am generating heat. Waiting for Argus to stop me...")
    
    # Infinite loop of math to spike CPU
    while True:
        [x**2 for x in range(10000)]

if __name__ == "__main__":
    try:
        stress_cpu()
    except KeyboardInterrupt:
        print("Stopped manually.")
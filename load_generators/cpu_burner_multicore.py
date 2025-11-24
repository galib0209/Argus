"""
Multicore CPU Burner – Stress Testing Module for Argus
Author: Ayushi Dwivedi (ayushidubey4569-cell)

Description:
    This script launches a CPU-burner process on **every available CPU core**
    to simulate extreme load conditions. The Argus monitoring agent should
    detect this overload and trigger its self-healing mechanism by killing
    these processes.

WARNING:
    Running this script will spike CPU usage to 100%.
    Use ONLY for testing the Argus SRE agent.
"""

import multiprocessing
import os

def burn():
    print(f"🔥 CPU BURNER STARTED (PID: {os.getpid()})")
    print("   I am generating heat. Waiting for Argus to stop me...")
    while True:
        [x**2 for x in range(10000)]

if __name__ == "__main__":
    for _ in range(multiprocessing.cpu_count()):
        multiprocessing.Process(target=burn).start()

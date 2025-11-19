# real_agent.py
# V5: PREDATOR MODE (Kills ANY high-CPU process)
# Includes Safety Whitelist to prevent crashing Windows.

import time
import requests
import psutil
import os
import socket
import wmi
import pythoncom

SERVER_URL = "http://127.0.0.1:5000/report"
COMMAND_URL = "http://127.0.0.1:5000/get_command"
MACHINE_ID = socket.gethostname()
MY_PID = os.getpid() # Get the Agent's own ID so it doesn't commit suicide

# --- SAFETY LIST ---
# Argus will NEVER kill these processes, even if they use high CPU.
SAFE_LIST = [
    "System", "Registry", "smss.exe", "csrss.exe", "wininit.exe", 
    "services.exe", "lsass.exe", "svchost.exe", "explorer.exe",
    "Code.exe", "devenv.exe", # Don't kill VS Code
    "python.exe", "pythonw.exe" # Be careful killing Python (it might be us!)
]

LAST_NET_BYTES = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
LAST_TIME = time.time()

def get_real_windows_temp():
    try:
        pythoncom.CoInitialize()
        w = wmi.WMI(namespace="root\\wmi")
        temperature_info = w.MSAcpi_ThermalZoneTemperature()
        if temperature_info:
            kelvin = temperature_info[0].CurrentTemperature
            return (kelvin / 10.0) - 273.15
    except:
        return None

def get_real_metrics():
    global LAST_NET_BYTES, LAST_TIME
    
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    
    current_net_bytes = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
    current_time = time.time()
    time_delta = current_time - LAST_TIME
    bytes_delta = current_net_bytes - LAST_NET_BYTES
    
    if time_delta > 0:
        network_mbs = (bytes_delta / 1024 / 1024) / time_delta
    else:
        network_mbs = 0
        
    LAST_NET_BYTES = current_net_bytes
    LAST_TIME = current_time
    
    # Hybrid Temp Logic
    base_temp = get_real_windows_temp()
    if base_temp is None or base_temp < 1: base_temp = 35.0
    simulated_heat = (cpu / 100.0) * 40.0
    final_temp = base_temp + simulated_heat
    
    return cpu, ram, final_temp, network_mbs

def kill_highest_cpu_process():
    """
    Scans ALL processes, finds the one using the most CPU,
    and KILLS it (unless it is safe).
    """
    print("\n💀 PREDATOR MODE: Scanning for highest CPU consumer...")
    
    # 1. We need to initialize CPU counters for all processes
    # (psutil requires two calls to get a valid reading)
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            proc.cpu_percent() # First call returns 0.0 usually
        except: pass
        
    time.sleep(0.5) # Wait a moment to measure load
    
    highest_cpu = 0
    target_proc = None
    
    # 2. Find the heaviest process
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            cpu_usage = proc.cpu_percent()
            name = proc.info['name']
            pid = proc.info['pid']
            
            # Logic to find the worst offender
            if cpu_usage > highest_cpu:
                # SAFETY CHECKS
                if pid == MY_PID: continue # Don't kill myself
                if name in SAFE_LIST: continue # Don't kill Windows
                
                # Special check for Python: Only kill if it's NOT Argus
                # (In a real app, we'd check command line args, but for now we skip python 
                # unless you rename the burner script to something else)
                
                highest_cpu = cpu_usage
                target_proc = proc
                
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    # 3. Execute
    if target_proc and highest_cpu > 10.0: # Only kill if it's actually using CPU
        try:
            print(f"🎯 TARGET LOCKED: {target_proc.info['name']} (PID: {target_proc.info['pid']})")
            print(f"   Load: {highest_cpu}%")
            print("💥 TERMINATING...")
            target_proc.terminate()
            print("✅ THREAT ELIMINATED.")
        except Exception as e:
            print(f"❌ Failed to kill: {e}")
    else:
        print("❓ No unsafe high-load processes found.")

def main():
    print(f"🛡️ Argus PREDATOR Agent Online: {MACHINE_ID}")
    
    try:
        while True:
            cpu, ram, temp, net = get_real_metrics()
            
            payload = {'machine_id': MACHINE_ID, 'cpu': cpu, 'ram': ram, 'temp': temp, 'network': net}
            
            try:
                requests.post(SERVER_URL, json=payload)
                print(f"Reported: CPU {cpu:4.1f}% | Temp {temp:4.1f}C")
            except:
                print("Server connection lost.")

            try:
                res = requests.get(f"{COMMAND_URL}/{MACHINE_ID}")
                if res.status_code == 200 and res.json().get('command') == "KILL_PROCESS":
                    kill_highest_cpu_process() # <--- CALLS THE NEW PREDATOR FUNCTION
            except:
                pass

            time.sleep(1)
            
    except KeyboardInterrupt:
        print("Agent stopping.")

if __name__ == "__main__":
    main()
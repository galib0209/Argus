# main.py
# ARGUS ORCHESTRATOR
# Launches all system components in separate console windows.

import subprocess
import time
import sys
import os
import platform

def launch_new_window(command, title="Argus Process"):
    """
    Launches a command in a new terminal window (Windows/Linux/Mac compatible).
    """
    system = platform.system()
    
    if system == "Windows":
        # On Windows, we use CREATE_NEW_CONSOLE to pop a new window
        return subprocess.Popen(
            command, 
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    elif system == "Darwin": # macOS
        # macOS requires AppleScript or 'open' to make a new terminal
        # This is a basic fallback for now
        return subprocess.Popen(command) 
    else: # Linux
        # Linux (Gnome/Ubuntu)
        # Try to use gnome-terminal if available, else fallback
        try:
            return subprocess.Popen(['gnome-terminal', '--'] + command)
        except:
            return subprocess.Popen(command)

def main():
    print("=======================================")
    print("   ⚡ ARGUS AUTONOMOUS AGENT SYSTEM   ")
    print("=======================================")
    print("Initializing System Components...")
    
    processes = []
    
    try:
        # 1. LAUNCH SERVER (The Brain)
        print("🚀 [1/3] Starting Brain (server.py)...")
        server_process = launch_new_window([sys.executable, "server.py"], "Argus Brain")
        processes.append(server_process)
        time.sleep(2) # Wait for server to bind port

        # 2. LAUNCH DASHBOARD (The UI)
        print("🚀 [2/3] Starting Mission Control (dashboard.py)...")
        # We run streamlit via python -m to avoid path issues
        dash_process = launch_new_window([sys.executable, "-m", "streamlit", "run", "dashboard.py"], "Argus Dashboard")
        processes.append(dash_process)
        time.sleep(2)

        # 3. LAUNCH REAL AGENT (The Hunter)
        print("🚀 [3/3] Starting Hunter Agent (real_agent.py)...")
        agent_process = launch_new_window([sys.executable, "real_agent.py"], "Argus Agent")
        processes.append(agent_process)

        print("\n✅ SYSTEM ONLINE.")
        print("   - Dashboard should open in your browser.")
        print("   - Agent is scanning local processes.")
        print("   - Server is processing telemetry.")
        print("\n⚠️  PRESS CTRL+C IN THIS WINDOW TO SHUT DOWN EVERYTHING.")
        
        # Keep the main script running to monitor the children
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 SHUTDOWN SIGNAL RECEIVED.")
        print("   Terminating all sub-systems...")
        
        for p in processes:
            try:
                p.terminate() # Soft kill
            except:
                pass
                
        print("✅ System Shutdown Complete.")

if __name__ == "__main__":
    main()
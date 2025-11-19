# server.py
# REAL MODE: Uses "KILL_PROCESS" tool
# Monitors Real CPU/RAM and authorizes process termination.

from flask import Flask, request, jsonify
import sqlite3
import datetime
import pandas as pd
import os
import google.generativeai as genai
from dotenv import load_dotenv

# --- DATETIME FIX ---
def adapt_datetime(val): return val.isoformat()
def convert_datetime(val): return datetime.datetime.fromisoformat(val.decode())
sqlite3.register_adapter(datetime.datetime, adapt_datetime)
sqlite3.register_converter("datetime", convert_datetime)

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('argus.db', detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS metrics 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  machine_id TEXT, cpu REAL, ram REAL, temp REAL, network REAL, timestamp DATETIME)''')
    c.execute('''CREATE TABLE IF NOT EXISTS alerts 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  machine_id TEXT, analysis TEXT, timestamp DATETIME)''')
    c.execute('''CREATE TABLE IF NOT EXISTS commands 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  machine_id TEXT, command TEXT, executed INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

init_db()

def execute_kill_tool(machine_id):
    """Queues a KILL command for the agent to execute locally."""
    print(f"🛠️ TOOL USE: Authorizing KILL_PROCESS for {machine_id}...")
    conn = sqlite3.connect('argus.db', detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    c.execute("INSERT INTO commands (machine_id, command, executed) VALUES (?, ?, 0)",
              (machine_id, "KILL_PROCESS"))
    conn.commit()
    conn.close()

def ask_gemini_agent(machine_id, recent_data):
    if not API_KEY: return

    prompt = f"""
    You are Argus, a Real-Time SRE Agent protecting a physical server.
    
    TOOL AVAILABLE: If CPU is critical, output "ACTION: KILL".
    
    Analyze real telemetry for '{machine_id}':
    {recent_data}
    
    Rules:
    1. IF CPU > 90% -> STATUS: CRITICAL. REASON: High Load. ACTION: KILL.
    2. IF CPU Rising Fast -> STATUS: WARNING.
    3. Else -> STATUS: HEALTHY.
    
    Output format:
    STATUS: [status]
    REASON: [reason]
    ACTION: [NONE or KILL]
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        print(f"🤖 Gemini Logic:\n{text}\n")
        
        if "CRITICAL" in text or "WARNING" in text:
            log_alert(machine_id, text)

        if "ACTION: KILL" in text:
            execute_kill_tool(machine_id)
            
    except Exception as e:
        print(f"Gemini Error: {e}")

def log_alert(machine_id, analysis):
    conn = sqlite3.connect('argus.db', detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    c.execute("INSERT INTO alerts (machine_id, analysis, timestamp) VALUES (?, ?, ?)",
              (machine_id, analysis, datetime.datetime.now()))
    conn.commit()
    conn.close()

@app.route('/report', methods=['POST'])
def handle_report():
    data = request.json
    machine_id = data.get('machine_id')
    cpu = data.get('cpu')
    ram = data.get('ram')
    temp = data.get('temp', 0)
    network = data.get('network', 0)
    now = datetime.datetime.now()

    conn = sqlite3.connect('argus.db', detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    c.execute("INSERT INTO metrics (machine_id, cpu, ram, temp, network, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
              (machine_id, cpu, ram, temp, network, now))
    conn.commit()
    conn.close()

    # Trigger AI if CPU > 80 (Real CPU spike)
    if cpu > 80: 
        conn = sqlite3.connect('argus.db', detect_types=sqlite3.PARSE_DECLTYPES)
        df = pd.read_sql(f"SELECT cpu, ram, temp, network FROM metrics WHERE machine_id='{machine_id}' ORDER BY timestamp DESC LIMIT 5", conn)
        conn.close()
        ask_gemini_agent(machine_id, df.to_string(index=False))
    
    return jsonify({"status": "success"}), 200

@app.route('/get_command/<machine_id>', methods=['GET'])
def get_command(machine_id):
    conn = sqlite3.connect('argus.db', detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    c.execute("SELECT id, command FROM commands WHERE machine_id=? AND executed=0 LIMIT 1", (machine_id,))
    row = c.fetchone()
    command = "NONE"
    if row:
        cmd_id, command = row
        c.execute("UPDATE commands SET executed=1 WHERE id=?", (cmd_id,))
        conn.commit()
    conn.close()
    return jsonify({"command": command}), 200

if __name__ == "__main__":
    print("Starting Argus Server (REAL MODE)...")
    app.run(host='0.0.0.0', port=5000)
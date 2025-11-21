# server.py
# FINAL V3: Supports detailed execution reporting from Agent.
# (Requires deleting argus.db before first run)

from flask import Flask, request, jsonify
import sqlite3
import datetime
import pandas as pd
import os
import google.generativeai as genai
from dotenv import load_dotenv

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
    # UPDATED TABLE: Added 'details' column
    c.execute('''CREATE TABLE IF NOT EXISTS commands 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  machine_id TEXT, command TEXT, executed INTEGER DEFAULT 0, details TEXT)''')
    conn.commit()
    conn.close()

init_db()

def execute_kill_tool(machine_id):
    print(f"🛠️ TOOL USE: Authorizing KILL_PROCESS for {machine_id}...")
    conn = sqlite3.connect('argus.db', detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    # Insert command, not executed yet, no details yet
    c.execute("INSERT INTO commands (machine_id, command, executed, details) VALUES (?, ?, 0, ?)",
              (machine_id, "KILL_PROCESS", "Pending..."))
    conn.commit()
    conn.close()

def log_alert(machine_id, analysis):
    conn = sqlite3.connect('argus.db', detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    c.execute("INSERT INTO alerts (machine_id, analysis, timestamp) VALUES (?, ?, ?)",
              (machine_id, analysis, datetime.datetime.now()))
    conn.commit()
    conn.close()

def ask_gemini_agent(machine_id, recent_data):
    if not API_KEY: return
    latest_metrics = recent_data.split('\n')[1].split()
    try:
        curr_cpu = float(latest_metrics[0])
        curr_ram = float(latest_metrics[1])
        curr_temp = float(latest_metrics[2])
    except: curr_cpu, curr_ram, curr_temp = 0, 0, 0

    prompt = f"""
    You are Argus. Analyze telemetry for '{machine_id}':
    CPU: {curr_cpu}%, RAM: {curr_ram}%, Temp: {curr_temp}C

    CRITICAL RULES (Trigger ACTION: KILL if ANY are true):
    1. IF CPU > 90% -> High Load Risk.
    2. IF RAM > 95% -> Memory OOM Risk.
    3. IF Temp > 85C -> Overheating Risk.
    
    OTHERWISE: Output "ACTION: NONE".

    Output format:
    STATUS: [CRITICAL/WARNING/HEALTHY]
    REASON: [Specific reason]
    ACTION: [NONE or KILL]
    """
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        print(f"🤖 Gemini Logic:\n{text}\n")
        if "CRITICAL" in text or "WARNING" in text: log_alert(machine_id, text)
        if "ACTION: KILL" in text: execute_kill_tool(machine_id)
    except Exception as e: print(f"Gemini Error: {e}")

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
    if cpu > 80 or ram > 90 or temp > 80: 
        conn = sqlite3.connect('argus.db', detect_types=sqlite3.PARSE_DECLTYPES)
        df = pd.read_sql(f"SELECT cpu, ram, temp, network FROM metrics WHERE machine_id='{machine_id}' ORDER BY timestamp DESC LIMIT 5", conn)
        conn.close()
        ask_gemini_agent(machine_id, df.to_string(index=False))
    return jsonify({"status": "success"}), 200

# UPDATED: Returns Command ID and doesn't mark executed immediately
@app.route('/get_command/<machine_id>', methods=['GET'])
def get_command(machine_id):
    conn = sqlite3.connect('argus.db', detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    c.execute("SELECT id, command FROM commands WHERE machine_id=? AND executed=0 LIMIT 1", (machine_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return jsonify({"id": row[0], "command": row[1]}), 200
    return jsonify({"id": None, "command": "NONE"}), 200

# NEW ENDPOINT: Agent reports back what it killed
@app.route('/report_execution', methods=['POST'])
def report_execution():
    data = request.json
    cmd_id = data.get('id')
    details = data.get('details')
    print(f"✅ EXECUTION REPORT: Command {cmd_id} -> {details}")
    conn = sqlite3.connect('argus.db', detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    # Mark as executed and save details
    c.execute("UPDATE commands SET executed=1, details=? WHERE id=?", (details, cmd_id))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    print("Starting Argus Server (V3 Final)...")
    app.run(host='0.0.0.0', port=5000)

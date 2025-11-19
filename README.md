⚡ Argus: Autonomous SRE Agent (Powered by Gemini 2.5)

Capstone Project Submission

Track: AI Agents & Automation

Role: Sole Developer

📖 Executive Summary

In modern cloud infrastructure, downtime is expensive. Traditional monitoring tools are "reactive"—they wait for a server to crash before alerting a human engineer. By the time the alert is received, the damage is done.

Argus is the solution. It is an Autonomous Site Reliability Engineering (SRE) Agent.

Instead of relying on static thresholds, Argus uses Google Gemini 2.5 to actively reason about system telemetry (CPU, RAM, Temperature, Network) in real-time. When it detects a critical threat—such as a runaway process causing overheating—it does not just send an alert. It autonomously intervenes, hunting down the specific process responsible and terminating it to restore system stability immediately.

🏗️ Architecture & Key Concepts

Argus is built on a Client-Server-Agent architecture designed for real-time autonomy.

🧠 Key AI Agent Concepts Implemented:

Observability (The Eyes): A local agent (real_agent.py) scans hardware at the kernel level, monitoring CPU load, RAM usage, Network I/O, and Motherboard Temperature (via Windows WMI).

Reasoning (The Brain): Telemetry is streamed to a central core (server.py). Anomalies are sent to Gemini 1.5 Flash. The LLM analyzes the context (e.g., "Is high CPU correlated with rising heat?") to distinguish between heavy load and a system-critical threat.

Tool Use (The Hands): Upon confirming a threat, Gemini authorizes a "Kill Command". The Agent switches to "Predator Mode," scanning the process list to identify the highest resource consumer and terminating it autonomously.

📊 System Diagram

graph TD
    subgraph Local Machine [Host Machine]
        A[Argus Hunter Agent] -->|1. Collect Real Metrics| B(Hardware / Kernel)
        A -->|5. Kill Rogue Process| C[Rogue App / Script]
    end

    subgraph Core System [Argus Core]
        A -->|2. Stream Telemetry| D[Flask Server]
        D -->|3. Analyze State| E{Gemini 1.5 API}
        E -->|4. Decision: ACTION KILL| D
        D -->|Store Logs| F[(SQLite DB)]
    end

    F -->|Read Data| G[Mission Control Dashboard]


🛠️ Tech Stack

AI Engine: Google Gemini 1.5 Flash (via google-generativeai)

Backend: Python Flask (REST API)

Frontend: Streamlit + Altair (Real-time Cyberpunk Dashboard)

System Interaction: psutil (Process Management), WMI (Hardware Sensors)

Orchestration: Python subprocess (Multi-process management)

🚀 Installation & Setup

Prerequisites

Python 3.10+ installed.

Windows OS (Required for WMI Temperature sensors and Console management).

A Google Gemini API Key.

Step 1: Clone & Install

# Clone the repository
git clone "https://github.com/AIwithKashan/Argus-Autonomous-AI-SRE"
cd Argus

# Install dependencies
pip install -r requirements.txt


Step 2: Configure Security

Open a file named .env in the root directory and add your API key:

GEMINI_API_KEY=your_actual_api_key_here


🕹️ How to Run the Demo (One-Click Launch)

Argus includes an orchestrator script that launches the Brain, the Agent, and the Dashboard simultaneously.

⚠️ IMPORTANT: For the Agent to access Hardware Temperature and kill processes, you must run your terminal as Administrator.

Open your terminal as Administrator.

Run the orchestrator:

python main.py


Three windows will open:

Argus Brain: The server processing logic.

Argus Agent: The scanner showing real-time metrics.

Dashboard: Your browser will open the Mission Control interface.

🧪 Triggering the "Self-Healing" Test

To demonstrate the AI's autonomy, we use a "Villain Script" that intentionally spikes CPU usage.

Ensure Argus is running and the Dashboard is visible (Green status).

Open a new terminal and run:

python cpu_burner.py


Watch the magic:

CPU will spike to 100%.

Dashboard will turn RED (Critical).

Gemini will log: ACTION: KILL.

Argus Agent will identify python.exe (running cpu_burner) as the threat and terminate it.

The system will return to Green/Healthy automatically.

📂 File Structure

main.py: The orchestrator. Runs the whole system.

server.py: The "Brain". Handles database, API, and Gemini integration.

real_agent.py: The "Hunter". Scans hardware and kills processes.

dashboard.py: The UI. Streamlit interface with Altair charts.

cpu_burner.py: The "Villain". A script to simulate a system crash.

argus.db: (Auto-generated) Stores logs and metric history.

Developed for the AI Agents Capstone Project.

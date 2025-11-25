# 🛡️ Argus: Autonomous AI SRE Agent

[![Project Status](https://img.shields.io/badge/Status-Completed-success)](https://github.com/YOUR_USERNAME/Argus-Autonomous-Agent)
[![AI](https://img.shields.io/badge/AI-Gemini%202.5-purple)](https://deepmind.google/technologies/gemini/)
[![Platform](https://img.shields.io/badge/Platform-Windows-blue)](https://www.microsoft.com/en-us/windows)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **An autonomous digital immune system for infrastructure that predicts crashes and self-heals in real-time.**

---

<div align="center">
  <img src="architecture.png" alt="Argus Architecture Diagram" width="800">
</div>

---

## 📖 Executive Summary

In modern cloud infrastructure, **downtime is expensive**. Traditional monitoring tools are "reactive"—they wait for a server to crash before alerting a human engineer at 3 AM. By the time the alert is received, the damage is already done.

**Argus is the solution.** It is an **Autonomous Site Reliability Engineering (SRE) Agent** designed for the **Google AI Agents Hackathon 2025 (Enterprise Track)**.

Instead of relying on static thresholds, Argus uses **Google Gemini 2.5** to actively *reason* about system telemetry in real-time. When it detects a critical threat—such as a rogue process causing rapid overheating or memory exhaustion—it doesn't just send an alert. It **autonomously intervenes**, intelligently hunting down the specific process responsible and terminating it to restore system stability immediately, without human intervention.

---

## 🏗️ Key Features (The Agentic Loop)

Argus implements a complete autonomous loop, moving from perception to action in seconds:

### 1. 👁️ Deep Observability (The Eyes)
A local Python agent scans the host machine at the kernel level, collecting deep, real-time data:
* **CPU Load:** Total system usage percentage.
* **RAM Usage:** Memory pressure and availability.
* **Network I/O:** Real-time data throughput (MB/s).
* **Hardware Temperature:** Reads real motherboard sensors via Windows WMI, with a physics-based simulation fallback for compatibility.

### 2. 🧠 Gemini 2.5 Reasoning (The Brain)
Telemetry is streamed to a central Flask server. Anomalies are sent to the **Gemini 2.5 API**. The LLM analyzes the *context* of the metrics (e.g., "Is high CPU correlated with dangerous temperature rise?") to distinguish between safe heavy load and a critical threat.

### 3. 🛠️ Smart Autonomous Action (The Hands)
Upon confirming a threat, Gemini authorizes a **"Kill Command"**. The Agent switches to "Predator Mode." Unlike simple scripts, Argus is a **Smart Hunter**:
* It scans the full process list to identify the highest resource consumer.
* It checks a robust **Safety Whitelist** to avoid killing critical system apps (e.g., Explorer, Browsers, System Idle Process).
* It intelligently differentiates between its own components (Dashboard, Server) and rogue Python scripts by analyzing command-line arguments, ensuring it only terminates the threat.
* It provides a detailed **Execution Report** back to the UI, confirming exactly which PID was terminated and why.

---

## 💻 Cyberpunk Mission Control UI

Argus features a custom-built, real-time dashboard for full system visibility.

<div align="center">
  <img src="dashboard_preview.png" alt="Argus Dashboard Preview" width="800">
  <p><em>The dashboard turns RED to indicate a critical threat and displays live autonomous actions.</em></p>
</div>

* **Live Telemetry:** Glowing metric cards for CPU, RAM, Temp, and Network.
* **Dynamic Charts:** Real-time Altair charts that change color based on threat levels, with visual "danger lines."
* **Reasoning Logs:** A scrolling terminal window showing Gemini's live thought process.
* **Action Report:** A prominent sidebar that updates instantly when an autonomous kill occurs, detailing the terminated process.

---

## 🚀 Quick Start Guide

**Prerequisites:**
* Windows 10/11 (Required for hardware sensor access and process management).
* Python 3.10 or higher.
* **Administrator Privileges** (Crucial for terminating processes).

### 1. Clone & Install
```bash
git clone https://github.com/AIwithKashan/Argus.git
cd Argus
pip install -r requirements.txt
``` 
### 2. Configure Security
Open file named .env in the project's root directory and add your Google Gemini API Key:
```
GEMINI_API_KEY=your_actual_api_key_here
```
(Note: Do not commit this file to version control.)

### 3. Launch System (One-Click Orchestration)
⚠️ IMPORTANT: Open your terminal or VS Code as Administrator.

Run the main orchestrator script to launch all components simultaneously:
```
python main.py
```
This will automatically launch three windows:

The Brain: The Flask server processing logic.

The Smart Agent: The silent hunter scanning processes in the background.

The Dashboard: Your default web browser will open the Mission Control interface.

### 🧪 The Demo: Triggering a Self-Healing Event
To demonstrate Argus's autonomy, we include "Villain" scripts to simulate system attacks.

Ensure Argus is running and the dashboard shows GREEN (System Stable) status.

Open a new terminal window.

Run the CPU burner script:
```
python cpu_burner.py
```

Watch the autonomous response:

The dashboard header turns RED (CRITICAL THREAT DETECTED).

The CPU Chart crosses the danger line and turns neon red.

Gemini logs show: ACTION: KILL.

The Smart Agent identifies the specific python.exe running the burner (ignoring the dashboard process) and terminates it.

The dashboard's "Action Report" panel updates to confirm the kill.

The system returns to GREEN automatically.

### 🛠️ Tech Stack
AI Model: Google Gemini 2.5 Flash

Backend Framework: Python Flask

Database: SQLite

Frontend UI: Streamlit, Altair (Custom Cyberpunk Theme)

System Interaction:

psutil: Cross-platform process and system monitoring.

WMI & pywin32: Windows-specific hardware sensor access.

Orchestration: Python subprocess module.


## Created by Kashan Khan & Ayushi for the AI Agents Hackathon 2025.


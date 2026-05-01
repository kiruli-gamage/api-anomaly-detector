# api-anomaly-detector

Overview
SentinelAI is an intelligent observability framework that bridges the gap between raw system telemetry and actionable engineering insights. By combining unsupervised machine learning for detection and Generative AI for automated root-cause analysis, it eliminates the "interpretability gap" common in traditional monitoring tools.

Core Features
Intelligent Detection: Uses an Isolation Forest ensemble to monitor Latency, RPS, Error Rate, and CPU Usage, identifying anomalies based on multi-dimensional relationships rather than static thresholds.

Sub-Second Diagnostics: Leverages the Groq LPU architecture and LLaMA 3.3 to generate human-readable incident reports in real-time.

Non-Blocking UI: A multithreaded Plotly Dash interface that remains responsive while the AI processes background diagnostics.

Chaos Engineering Suite: Includes a built-in anomaly injection framework to simulate database deadlocks, traffic surges, and service failures.

System Architecture
The pipeline follows a modular design to ensure high availability and low latency:

Data Generation: Synthetic telemetry is modeled via NumPy to simulate "healthy" system behavior.

ML Inference: The Isolation Forest evaluates the live stream against a pre-trained serialized baseline.

LLM Reasoning: Upon detection, statistical "deltas" are sent to Groq for automated root-cause deduction.

Visualization: Data and AI reports are rendered on a live-updating dashboard.

Technical Stack
Language: Python 3.x

ML & Data: Scikit-learn (Isolation Forest), NumPy, Pickle

AI Inference: Groq Cloud API (LLaMA 3.3 70B)

Frontend: Plotly Dash

Concurrency: Python Threading

Getting Started
1. Prerequisites

Python 3.8+

A Groq API Key (Get it at console.groq.com)

2. Installation

Bash
git clone https://github.com/yourusername/sentinel-ai.git
cd sentinel-ai
pip install -r requirements.txt
3. Configuration
Create a .env file in the root directory:

Plaintext
GROQ_API_KEY=your_api_key_here
4. Execution

Bash
python app.py
Project Structure
app.py: Dashboard logic and UI layout.

detector.py: ML implementation and anomaly logic.

generator.py: Synthetic telemetry and stress-test injection.

requirements.txt: Project dependencies.

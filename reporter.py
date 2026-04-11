import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_incident_report(anomaly_data):
    prompt = f"""You are a senior DevOps engineer writing a professional incident report.
    
An anomaly was detected in the API monitoring system with these metrics:
- Timestamp: {anomaly_data['timestamp']}
- Latency: {anomaly_data['latency_ms']}ms (normal is ~120ms)
- Requests/sec: {anomaly_data['requests_per_sec']} (normal is ~50)
- Error rate: {round(anomaly_data['error_rate'] * 100, 1)}% (normal is ~1%)
- CPU usage: {anomaly_data['cpu_usage']}% (normal is ~40%)
- Confidence: {anomaly_data['confidence']}%

Write a short, professional incident report with:
1. What happened
2. Likely cause
3. Recommended action

Keep it under 100 words. Be direct and professional."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200
    )

    return response.choices[0].message.content

import requests
import json
import google.generativeai as genai
import time
from datetime import datetime, timedelta
from devices import get_devices_list
from traffic import get_traffic_activities
from audit_logs import get_site_audit_logs
from chatbot import GEMINI_API_KEY

# Configure Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def get_ai_dashboard_data(site_id, token, base_url):
    """
    Generates AI dashboard data by fetching real Omada data and analyzing it with Gemini.
    """
    print("--- [AI Dashboard] Generating data... ---")
    print(f"--- [AI Dashboard] Time module: {time} ---")
    
    # 1. Fetch Real Data Context
    # We need to gather enough context for the AI to make a decision.
    # - Devices (status, cpu, mem)
    # - Recent Traffic (last 1 hour)
    # - Recent Logs (errors/warnings)
    
    omadac_id = "25d8717240c92695570075f3a0975d9e" # Hardcoded for now as per main.py usage, or pass it in.
    # In main.py, OMADAC_ID is imported from authentication. We should ideally pass it or import it.
    from authentication import OMADAC_ID
    
    # A. Devices
    devices = get_devices_list(base_url, token, OMADAC_ID, site_id)
    
    # B. Traffic (Last 1 hour)
    end_time = int(time.time())
    start_time = end_time - 3600
    traffic = get_traffic_activities(base_url, token, OMADAC_ID, site_id, start_time, end_time)
    
    # C. Logs (Last 20 entries)
    logs = get_site_audit_logs(base_url, token, OMADAC_ID, site_id, {"pageSize": 20, "currentPage": 1})

    # Prepare Context String
    context_str = f"""
    Current Network State:
    - Devices: {json.dumps(devices if devices else [], default=str)}
    - Traffic (Last 1h): {json.dumps(traffic if traffic else [], default=str)}
    - Recent Logs: {json.dumps(logs if logs else [], default=str)}
    """

    # 2. Ask Gemini to Analyze
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        You are an expert Network Reliability Engineer AI. Analyze the following Omada Network data and generate a health report.
        
        Data:
        {context_str}
        
        Task:
        1. Calculate a 'healthScore' (0-100) based on device status (connected/disconnected), CPU/Mem usage, and error logs.
        2. Generate a short 'healthScoreExplanation' (max 2 sentences) explaining WHY the score is calculated this way (e.g., "Score is 95 because all devices are online and traffic is normal, but one AP has slightly high memory.").
        3. Generate 2-3 specific 'insights' about the network's current state.
        4. Identify any 'anomalies' (e.g., high latency, disconnected devices, high CPU). If none, return empty list.
        5. Predict 'predictions' for network load (%) for the next 24 hours (hourly). Base this on the current traffic trend if visible, otherwise assume a standard daily curve (peak 9am-5pm).
        
        Output format: JSON ONLY.
        {{
            "healthScore": 95,
            "healthScoreExplanation": "Score is high because all critical devices are online with low resource usage.",
            "insights": ["Insight 1", "Insight 2"],
            "anomalies": [{{"severity": "High", "entity": "AP-1", "issue": "Disconnected", "recommendation": "Check cable"}}],
            "predictions": [{{"time": "10:00", "predictedLoad": 45}}, ...]
        }}
        """
        
        response = model.generate_content(prompt)
        text_response = response.text.strip().replace('```json', '').replace('```', '')
        ai_result = json.loads(text_response)
        
        return ai_result

    except Exception as e:
        print(f"AI Analysis Failed: {e}")
        # Fallback to mock/safe data if AI fails
        return {{
            "healthScore": 0,
            "healthScoreExplanation": "AI analysis failed, so the score cannot be explained.",
            "insights": ["AI Analysis failed. Please check backend logs."],
            "anomalies": [],
            "predictions": []
        }}


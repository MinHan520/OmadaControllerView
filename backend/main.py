from flask import Flask, request, jsonify
from traffic import get_traffic_activities
from flask_cors import CORS
from authentication import run_authentication_flow, OMADAC_ID
from sites import get_sites_list, get_specific_site
from dashboard import get_site_overview_diagram
from devices import get_devices_list, get_device_details
from audit_logs import get_site_audit_logs, get_global_audit_logs
from ai_dashboard import get_ai_dashboard_data

app = Flask(__name__)
CORS(app)

# Initialize Firestore
from firebase_utils import initialize_firestore
initialize_firestore()

@app.route("/login", methods=["POST"])
def login():
    # Attempt to initialize Firestore (safe to call multiple times)
    initialize_firestore()
    
    data = request.get_json()
    base_url = data.get("base_url")
    username = data.get("username")
    password = data.get("password")

    if not all([base_url, username, password]):
        return jsonify({"error": "Missing required fields"}), 400

    auth_result = run_authentication_flow(base_url, username, password)

    if auth_result and auth_result.get("access_token"):
        return jsonify(auth_result)
    else:
        return jsonify({"error": "Authentication failed"}), 401

@app.route("/sites", methods=["POST"])
def sites():
    data = request.get_json()
    print("---[/sites] Received data: ---")
    print(data)
    
    base_url = data.get("base_url")
    access_token = data.get("access_token")

    if not all([base_url, access_token]):
        print("---[/sites] Error: Missing required fields ---")
        return jsonify({"error": "Missing required fields: base_url and access_token are required."}), 400

    sites_data = get_sites_list(base_url, access_token, OMADAC_ID)
    print(f"---[/sites] Response to frontend: {sites_data} ---")

    if sites_data:
        return jsonify(sites_data)
    else:
        return jsonify({"error": "Failed to get sites"}), 500

@app.route("/sites/<site_id>", methods=["POST"])
def site(site_id):
    data = request.get_json()
    base_url = data.get("base_url")
    access_token = data.get("access_token")

    if not all([base_url, access_token]):
        return jsonify({"error": "Missing required fields"}), 400

    site_data = get_specific_site(base_url, access_token, OMADAC_ID, site_id)

    if site_data:
        return jsonify(site_data)
    else:
        return jsonify({"error": "Failed to get site"}), 500

@app.route("/sites/<site_id>/dashboard", methods=["POST"])
def dashboard(site_id):
    data = request.get_json()
    base_url = data.get("base_url")
    access_token = data.get("access_token")

    if not all([base_url, access_token]):
        return jsonify({"error": "Missing required fields"}), 400

    dashboard_data = get_site_overview_diagram(base_url, access_token, OMADAC_ID, site_id)
    print(f"---[/sites/{site_id}/dashboard] Response to frontend: {dashboard_data} ---")

    if dashboard_data:
        return jsonify(dashboard_data)
    else:
        return jsonify({"error": "Failed to get dashboard"}), 500

@app.route("/sites/<site_id>/devices", methods=["POST"])
def devices(site_id):
    data = request.get_json()
    base_url = data.get("base_url")
    access_token = data.get("access_token")

    if not all([base_url, access_token]):
        return jsonify({"error": "Missing required fields"}), 400

    devices_data = get_devices_list(base_url, access_token, OMADAC_ID, site_id)
    print(f"---[/sites/{site_id}/devices] Response to frontend: {devices_data} ---")

    if devices_data is not None:
        return jsonify(devices_data)
    else:
        return jsonify({"error": "Failed to get devices"}), 500

@app.route("/sites/<site_id>/devices/<mac>", methods=["POST"])
def device_details(site_id, mac):
    data = request.get_json()
    base_url = data.get("base_url")
    access_token = data.get("access_token")

    if not all([base_url, access_token]):
        return jsonify({"error": "Missing required fields"}), 400

    device_data = get_device_details(base_url, access_token, OMADAC_ID, site_id, mac)
    print(f"---[/sites/{site_id}/devices/{mac}] Response to frontend: {device_data} ---")

    if device_data:
        return jsonify(device_data)
    else:
        return jsonify({"error": "Failed to get device details"}), 500

@app.route("/sites/<site_id>/audit_logs", methods=["POST"])
def site_audit_logs(site_id):
    data = request.get_json()
    base_url = data.get("base_url")
    access_token = data.get("access_token")
    params = data.get("params", {})

    if not all([base_url, access_token]):
        return jsonify({"error": "Missing required fields"}), 400

    logs_data = get_site_audit_logs(base_url, access_token, OMADAC_ID, site_id, params)

    if logs_data:
        return jsonify(logs_data)
    else:
        return jsonify({"error": "Failed to get site audit logs"}), 500

@app.route("/global_audit_logs", methods=["POST"])
def global_audit_logs():
    data = request.get_json()
    base_url = data.get("base_url")
    access_token = data.get("access_token")
    params = data.get("params", {})

    if not all([base_url, access_token]):
        return jsonify({"error": "Missing required fields"}), 400

    logs_data = get_global_audit_logs(base_url, access_token, OMADAC_ID, params)

    if logs_data:
        return jsonify(logs_data)
    else:
        return jsonify({"error": "Failed to get global audit logs"}), 500

# New route for traffic activities
@app.route("/sites/<site_id>/traffic_activities", methods=["POST", "OPTIONS"])
def traffic_activities(site_id):
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
        
    data = request.get_json()
    base_url = data.get("base_url")
    access_token = data.get("access_token")
    start = data.get("start")
    end = data.get("end")
    ap_mac = data.get("ap_mac")
    switch_mac = data.get("switch_mac")

    if not all([base_url, access_token, start, end]):
        return jsonify({"error": "Missing required fields"}), 400
    
    # The specific endpoint /stat/switches/{mac} requested by the user returns 404.
    # We revert to using the general dashboard traffic endpoint which supports filtering by switchMac.
    traffic_data = get_traffic_activities(base_url, access_token, OMADAC_ID, site_id, start, end, ap_mac, switch_mac)
        
    if traffic_data:
        return jsonify({"errorCode": 0, "result": traffic_data})
    else:
        return jsonify({"error": "Failed to get traffic data"}), 500
        
@app.route("/sites/<site_id>/ai_dashboard", methods=["POST"])
def ai_dashboard_route(site_id):
    data = request.get_json()
    base_url = data.get("base_url")
    access_token = data.get("access_token")

    if not all([base_url, access_token]):
        return jsonify({"error": "Missing required fields"}), 400

    ai_data = get_ai_dashboard_data(site_id, access_token, base_url)
    
    if ai_data:
        return jsonify(ai_data)
    else:
        return jsonify({"error": "Failed to generate AI data"}), 500

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message")
    access_token = data.get("access_token")
    base_url = data.get("base_url")

    if not all([user_message, access_token, base_url]):
        return jsonify({"error": "Missing required fields"}), 400

    from chatbot import generate_rag_response
    response = generate_rag_response(user_message, access_token, base_url)
    return jsonify({"answer": response})

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

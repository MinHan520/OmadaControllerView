from flask import Flask, request, jsonify
from flask_cors import CORS
from authentication import run_authentication_flow, OMADAC_ID
from sites import get_sites_list, get_specific_site
from dashboard import get_site_overview_diagram
from devices import get_devices_list, get_device_details
from audit_logs import get_site_audit_logs, get_global_audit_logs

app = Flask(__name__)
CORS(app)

@app.route("/login", methods=["POST"])
def login():
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

    if devices_data:
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

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

"""
This module handles authentication for the Omada controller.
"""
import json
import urllib3
import requests

# Disable InsecureRequestWarning: Unverified HTTPS request is being made.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- Configuration ---
# CLIENT_ID = "975fc957360942df99cbd661a833e4cc"
CLIENT_ID = "47f10502b539408faeb61b75f78e21a2"
# CLIENT_SECRET = "7488ee406c9843fa80e86d0f9570c693"
CLIENT_SECRET = "639686a2051a43e5b0366877ed7f163e"
# OMADAC_ID = "6efebeb06fb81dfe27d81641e734ada3"
OMADAC_ID = "1242a081f0444ff04b7a53b9e0299fb0"

def make_request(base_url, method, url_path, headers=None, data=None, json_data=None, params=None):
    """
    A stateless request helper that requires the base_url for each call.
    """
    if not base_url:
        raise ValueError("base_url must be provided to make_request")
    url = f"{base_url}{url_path}"
    print("\n--- New Request ---")
    print(f"Request: {method.upper()} {url}")
    if headers:
        print(f"Headers: {json.dumps(headers, indent=2)}")
    if params:
        print(f"Query Params: {json.dumps(params, indent=2)}")
    if json_data:
        print(f"JSON Body: {json.dumps(json_data, indent=2)}")
    if data:
        print(f"Form Data: {data}")

    try:
        # In production, you should use a valid certificate by setting verify=True
        # and possibly passing the path to your CA bundle.
        response = requests.request(
            method,
            url,
            headers=headers,
            data=data,
            json=json_data,
            params=params,
            verify=False,
            timeout=30
        )

        print("\n--- Response ---")
        print(f"Status Code: {response.status_code}")
        try:
            # Try to pretty-print JSON response
            print(f"Body: {json.dumps(response.json(), indent=2)}")
        except json.JSONDecodeError:
            # Fallback for non-JSON response
            print(f"Body: {response.text}")

        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        return response
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code} - {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"An unexpected error occurred: {e}")
        return None

def login_to_controller(base_url, username, password):
    """Logs into the controller to get a CSRF token and session ID."""
    print("\n---- Step 1: Logging in to get CSRF token and Session ID ----")
    url_path = "/openapi/authorize/login"
    params = {
        "client_id": CLIENT_ID,
        "omadac_id": OMADAC_ID,
    }
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "username": username,
        "password": password
    }

    response = make_request(base_url, "POST", url_path, headers=headers, json_data=payload, params=params)

    if not response:
        return None, None

    try:
        data = response.json()
        if data.get("errorCode") == 0:
            result = data.get("result", {})
            csrf_token = result.get("csrfToken")
            session_id = result.get("sessionId")
            print("\nSuccessfully logged in via OpenAPI.")
            print(f"CSRF Token: {csrf_token}")
            return csrf_token, session_id
        print(f"Login failed: {data.get('msg')}")
    except json.JSONDecodeError:
        print("Failed to decode JSON from login response.")
    return None, None

def get_auth_code(base_url, csrf_token, session_id):
    """Gets the authorization code."""
    print("\n\n---- Step 2: Get Authentication Code ----")
    if not (csrf_token and session_id):
        print("\nMissing CSRF Token or SessionID. Please generate again later.")
        return None

    url_path = f"/openapi/authorize/code"
    params = {
        "client_id": CLIENT_ID,
        "omadac_id": OMADAC_ID,
        "response_type": "code"
    }
    headers = {
        "Content-Type": "application/json",
        "Csrf-token": csrf_token,
        "Cookie": f"TPOMADA_SESSIONID={session_id}"
    }

    response = make_request(base_url, "POST", url_path, headers=headers, params=params)
    if not response:
        return None
    try:
        data = response.json()
        if data.get("errorCode") == 0:
            authorization_code = data.get("result")
            print("\nSuccessfully retrieved authorization code.")
            print(f"Authorization Code: {authorization_code}")
            return authorization_code
        print(f"Failed to get authorization code: {data.get('msg')}")
    except json.JSONDecodeError:
        print("Failed to decode JSON from getAuthCode response.")
    return None

def get_access_token(base_url, authorization_code):
    """Gets the access token."""
    print("\n\n---- Step 3: Get Access Token ----")
    if not authorization_code:
        print("\nMissing Authorization Code. Cannot get access token.")
        return None, None

    url_path = "/openapi/authorize/token"
    params = {
        "grant_type": "authorization_code",
        "code": authorization_code
    }
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    header = {
        "Content-Type": "application/json"
    }

    response = make_request(base_url, "POST", url_path, headers=header, json_data=payload, params=params)
    if not response:
        return None, None
    try:
        data = response.json()
        if data.get("errorCode") == 0:
            result = data.get("result", {})
            access_token = result.get("accessToken")
            refresh_token = result.get("refreshToken")
            print("\nSuccessfully retrieved access token.")
            return access_token, refresh_token
        print(f"Failed to get access token: {data.get('msg')}")
    except json.JSONDecodeError:
        print("Failed to decode JSON from getAccessToken response.")
    return None, None

def run_authentication_flow(base_url, username, password):
    """
    Orchestrates the entire authentication flow.

    Args:
        base_url (str): The base URL of the Omada controller (e.g., https://192.168.1.100).
        username (str): The username for the controller.
        password (str): The password for the controller.

    Returns:
        A tuple containing (access_token, refresh_token) or (None, None) if it fails.
    """
    csrf_token, session_id = login_to_controller(base_url, username, password)
    if not (csrf_token and session_id):
        print("\nAuthentication failed at login step.")
        return None, None

    auth_code = get_auth_code(base_url, csrf_token, session_id)
    if not auth_code:
        print("\nAuthentication failed at getting authorization code step.")
        return None, None

    access_token, refresh_token = get_access_token(base_url, auth_code)
    if not access_token:
        print("\nAuthentication failed at getting access token step.")
        return None, None

    return access_token, refresh_token


import requests
import urllib3
import json

# Disable InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- Configuration from user specification ---
CLIENT_ID = "975fc957360942df99cbd661a833e4cc"
CLIENT_SECRET = "7488ee406c9843fa80e86d0f9570c693"
OMADAC_ID = "6efebeb06fb81dfe27d81641e734ada3"

def make_request(base_url, method, url_path, headers=None, data=None, json_data=None, params=None):
    """
    A stateless request helper that requires the base_url for each call.
    """
    if not base_url:
        raise ValueError("base_url must be provided to make_request")
    
    url = f"{base_url}{url_path}"
    
    try:
        response = requests.request(
            method,
            url,
            headers=headers,
            data=data,
            json=json_data,
            params=params,
            verify=False, # In production, this should be True with a valid cert
            timeout=30
        )
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        return response
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code} - {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"An unexpected error occurred: {e}")
        return None

def login_to_controller(base_url, username, password):
    """Step 1: Logs into the controller to get a CSRF token and session ID."""
    print("\n---- [Auth Step 1] Logging in to get CSRF token and Session ID ----")
    url_path = "/openapi/authorize/login"
    params = {"client_id": CLIENT_ID, "omadac_id": OMADAC_ID}
    payload = {"username": username, "password": password}

    response = make_request(base_url, "POST", url_path, json_data=payload, params=params)
    if not response:
        return None, None

    try:
        data = response.json()
        if data.get("errorCode") == 0:
            result = data.get("result", {})
            csrf_token = result.get("csrfToken")
            session_id = result.get("sessionId")
            print("--- [Auth Step 1] Success.")
            return csrf_token, session_id
    except (json.JSONDecodeError, AttributeError):
        pass
    print("--- [Auth Step 1] Failed.")
    return None, None

def get_auth_code(base_url, csrf_token, session_id):
    """Step 2: Gets the authorization code."""
    print("\n---- [Auth Step 2] Get Authentication Code ----")
    url_path = f"/openapi/authorize/code"
    params = {"client_id": CLIENT_ID, "omadac_id": OMADAC_ID, "response_type": "code"}
    headers = {"Csrf-token": csrf_token, "Cookie": f"TPOMADA_SESSIONID={session_id}"}

    response = make_request(base_url, "POST", url_path, headers=headers, params=params)
    if not response:
        return None
    try:
        data = response.json()
        if data.get("errorCode") == 0:
            authorization_code = data.get("result")
            print("--- [Auth Step 2] Success.")
            return authorization_code
    except (json.JSONDecodeError, AttributeError):
        pass
    print("--- [Auth Step 2] Failed.")
    return None

def get_access_token(base_url, authorization_code):
    """Step 3: Gets the access token."""
    print("\n---- [Auth Step 3] Get Access Token ----")
    url_path = "/openapi/authorize/token"
    params = {"grant_type": "authorization_code", "code": authorization_code}
    payload = {"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET}

    response = make_request(base_url, "POST", url_path, json_data=payload, params=params)
    if not response:
        return None, None
    try:
        data = response.json()
        if data.get("errorCode") == 0:
            result = data.get("result", {})
            access_token = result.get("accessToken")
            refresh_token = result.get("refreshToken")
            print("--- [Auth Step 3] Success.")
            return access_token, refresh_token
    except (json.JSONDecodeError, AttributeError):
        pass
    print("--- [Auth Step 3] Failed.")
    return None, None

def run_authentication_flow(base_url, username, password):
    """Orchestrates the entire authentication flow."""
    csrf_token, session_id = login_to_controller(base_url, username, password)
    if not (csrf_token and session_id):
        return None

    auth_code = get_auth_code(base_url, csrf_token, session_id)
    if not auth_code:
        return None

    access_token, refresh_token = get_access_token(base_url, auth_code)
    if not access_token:
        return None

    print("\n--- Authentication Flow Complete. Tokens Obtained. ---")
    return {"access_token": access_token, "refresh_token": refresh_token}

def refresh_access_token(base_url, refresh_token):
    """Refreshes the access token using the refresh token."""
    print(f"\n---- [Auth Refresh] Attempting to refresh access token... ----")
    url_path = "/openapi/authorize/token"
    params = {"grant_type": "refresh_token", "refresh_token": refresh_token}
    payload = {"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET}

    response = make_request(base_url, "POST", url_path, json_data=payload, params=params)
    if not response:
        return None
    try:
        data = response.json()
        if data.get("errorCode") == 0:
            result = data.get("result", {})
            new_access_token = result.get("accessToken")
            new_refresh_token = result.get("refreshToken")
            print("--- [Auth Refresh] Success.")
            return {"access_token": new_access_token, "refresh_token": new_refresh_token}
    except (json.JSONDecodeError, AttributeError):
        pass
    
    print("--- [Auth Refresh] Failed.")
    return None

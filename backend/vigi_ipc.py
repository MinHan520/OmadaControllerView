import requests
import json
import urllib3
import urllib.parse

# Disable InsecureRequestWarning for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def authenticate_vigi_ipc(device_ip, password_md5):
    """
    Authenticates with a VIGI IPC and returns the session token (stok).

    Args:
        device_ip (str): The IP address of the VIGI IPC.
        password_md5 (str): The MD5 hash of the password.

    Returns:
        str: The session token (stok) if authentication is successful.
        None: If authentication fails.
    """
    # URL for the initial authentication request
    # Must include the device address and the default HTTPS port (20443).
    url = f"https://{device_ip}:20443/"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Request Body: A JSON string with the method "doAuth"
    payload = {
        "method": "doAuth",
        "params": {
            "password": password_md5,
            "passwdType": "md5"
        }
    }
    
    try:
        # JSON/Encoding Rule: All API requests and responses must be handled using Percent-encoding (URL encoding) for JSON strings.
        json_str = json.dumps(payload)
        encoded_payload = urllib.parse.quote(json_str)
        
        print(f"Sending Auth Request to {url}")
        
        response = requests.post(
            url, 
            data=encoded_payload, 
            headers=headers, 
            verify=False, 
            timeout=10
        )
        
        response.raise_for_status()
        
        # Decode the response
        decoded_response = urllib.parse.unquote(response.text)
        try:
            data = json.loads(decoded_response)
        except json.JSONDecodeError:
            # Fallback: sometimes the response might not be encoded or might be raw JSON?
            # But the rule says "All ... responses must be handled using Percent-encoding"
            # We'll try loading raw text if decoding fails to be robust, or just fail.
            # Let's assume strict adherence first, but logging raw text helps debugging.
            print(f"Failed to decode JSON from response. Raw text: {response.text}")
            return None
        
        # Expected Response: A successful response returns the stok value in the result body.
        if "result" in data and "stok" in data["result"]:
            return data["result"]["stok"]
        else:
            print(f"Authentication failed. Response data: {data}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error during authentication: {e}")
        return None

def example_usage_get_device_info(device_ip, stok):
    """
    Example demonstrating how to use the returned stok in a hypothetical second API call.
    """
    # URL Format: https://<device_addr>:<port>/stok=<stok>
    url = f"https://{device_ip}:20443/stok={stok}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Hypothetical second API call
    payload = {
        "method": "getDeviceInfo",
        "params": {}
    }
    
    try:
        json_str = json.dumps(payload)
        encoded_payload = urllib.parse.quote(json_str)
        
        print(f"Sending Request to {url}")
        
        response = requests.post(
            url,
            data=encoded_payload,
            headers=headers,
            verify=False,
            timeout=10
        )
        
        response.raise_for_status()
        
        decoded_response = urllib.parse.unquote(response.text)
        return json.loads(decoded_response)
        
    except Exception as e:
        print(f"Error in example usage: {e}")
        return None

# Configuration
DEVICE_IP = "192.168.0.9"
# MD5 of 'admin' -> 21232f297a57a5a743894a0e4a801fc3
PASSWORD_MD5 = "21232f297a57a5a743894a0e4a801fc3"

def authenticate_configured_vigi():
    """
    Authenticates the VIGI IPC configured in this module.
    """
    print(f"--- Authenticating VIGI IPC ({DEVICE_IP}) ---")
    return authenticate_vigi_ipc(DEVICE_IP, PASSWORD_MD5)

if __name__ == "__main__":
    # Example Usage
    print(f"--- Starting VIGI IPC Authentication Test ---")
    stok = authenticate_configured_vigi()
    
    if stok:
        print(f"Successfully authenticated. Stok: {stok}")
        
        print("--- Testing Subsequent Request (getDeviceInfo) ---")
        info = example_usage_get_device_info(DEVICE_IP, stok)
        if info:
            print("Device Info Response:", json.dumps(info, indent=2))
        else:
            print("Failed to get device info.")
    else:
        print("Authentication failed.")

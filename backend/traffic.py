"""
This module handles traffic activity retrieval for the Omada controller.
"""

import time
import json
from authentication import make_request
from firebase_utils import save_document

def get_traffic_activities(base_url, access_token, omadac_id, site_id, start, end, ap_mac=None, switch_mac=None):
    """
    Retrieves traffic activities (AP and Switch) for a specific site within a time range.

    Args:
        base_url (str): Base URL of the Omada controller.
        access_token (str): Access token for authentication.
        omadac_id (str): Omada controller ID.
        site_id (str): Site ID.
        start (int): Start timestamp (seconds).
        end (int): End timestamp (seconds).
        ap_mac (str, optional): MAC address of the AP to filter by.
        switch_mac (str, optional): MAC address of the Switch to filter by.

    Returns:
        dict: Dictionary with keys 'apTrafficActivities' and 'switchTrafficActivities' containing lists, or None on failure.
    """
    print(f"\n--- Fetching Traffic Activities for Site {site_id} (from {start} to {end}) ---")
    url_path = f"/openapi/v1/{omadac_id}/sites/{site_id}/dashboard/traffic-activities"
    headers = {"Authorization": f"AccessToken={access_token}"}
    params = {"start": start, "end": end}
    
    # Attempt to filter by device MAC if provided
    if ap_mac:
        params["apMac"] = ap_mac
    if switch_mac:
        params["switchMac"] = switch_mac

    response = make_request(base_url, "GET", url_path, headers=headers, params=params)
    if not response:
        return None
    try:
        data = response.json()
        if data.get("errorCode") != 0:
            print(f"API Error fetching traffic: {data.get('msg')} (Code: {data.get('errorCode')})")
            return None
        result = data.get("result", {})
        
        traffic_data = {
            "apTrafficActivities": result.get("apTrafficActivities", []),
            "switchTrafficActivities": result.get("switchTrafficActivities", [])
        }

        # Store in Firebase
        try:
            print("--- Storing traffic data in Firebase ---")
            doc_id = str(int(time.time()))
            
            # Prepare data for Firestore (firebase-admin SDK handles type conversion)
            firestore_data = {
                "siteId": site_id,
                "timestamp": int(doc_id),
                "apTraffic": traffic_data["apTrafficActivities"],
                "switchTraffic": traffic_data["switchTrafficActivities"]
            }
            
            save_document(collection_id="traffic_logs", document_id=doc_id, data=firestore_data)
            print(f"Successfully stored traffic data in Firebase (Doc ID: {doc_id})")
        except Exception as e:
            print(f"Error storing data in Firebase: {e}")

        return traffic_data

    except (ValueError, KeyError) as e:
        print(f"Error parsing traffic response: {e}")
        return None

def get_switch_statistics(base_url, access_token, omadac_id, site_id, switch_mac, start, end):
    """
    Retrieves statistics for a specific switch using the stat/switches endpoint.
    """
    print(f"\n--- Fetching Specific Switch Statistics for {switch_mac} ---")
    
    # Try using the MAC address WITH dashes/colons as provided (Omada API inconsistency)
    # switch_mac_clean = switch_mac.replace("-", "").replace(":", "")
    
    url_path = f"/openapi/v1/{omadac_id}/sites/{site_id}/stat/switches/{switch_mac}"
    headers = {"Authorization": f"AccessToken={access_token}"}
    # This endpoint might not support start/end, but we'll pass them if it's a stat history endpoint,
    # or just ignore them if it's current stats. The user requested this specific URL.
    params = {"start": start, "end": end} 

    response = make_request(base_url, "GET", url_path, headers=headers, params=params)
    if not response:
        return None
    
    try:
        data = response.json()
        if data.get("errorCode") != 0:
            print(f"API Error fetching switch stats: {data.get('msg')} (Code: {data.get('errorCode')})")
            return None
            
        result = data.get("result", {})
        
        # The user wants to display traffic. 
        # If this endpoint returns a list of stats (time series), we use it.
        # If it returns a single object (current stats), we might need to wrap it.
        # For now, we'll assume it returns something we can pass back.
        # We'll map it to 'switchTrafficActivities' format if possible, or just return raw.
        
        # If the result is a dict (single current stat), we wrap it in a list
        if isinstance(result, dict):
            # Try to normalize fields to match what frontend expects (txData, rxData, time)
            # Frontend expects: { time, txData, rxData }
            # If result has 'tx' and 'rx', we map them.
            normalized_stat = {
                "time": result.get("time", int(time.time())), # Use current time if missing
                "txData": result.get("tx", 0),
                "rxData": result.get("rx", 0),
                "mac": switch_mac
            }
            return {"switchTrafficActivities": [normalized_stat], "apTrafficActivities": []}
            
        elif isinstance(result, list):
            return {"switchTrafficActivities": result, "apTrafficActivities": []}
            
        return {"switchTrafficActivities": [], "apTrafficActivities": []}

    except (ValueError, KeyError) as e:
        print(f"Error parsing switch stats response: {e}")
        return None

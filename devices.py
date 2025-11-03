"""
This module handles device-related operations for the Omada controller.
"""
from authentication import make_request

def get_devices_list(base_url, access_token, omadac_id, site_id, db):
    """
    Retrieves a list of all devices for a specific site from the Omada controller.
    Also saves/updates each device in the Firestore database.

    Args:
        base_url (str): The base URL of the Omada controller.
        access_token (str): The access token for authentication.
        omadac_id (str): The Omada Controller ID.
        site_id (str): The ID of the site whose devices are to be retrieved.
        db (firestore.Client): The Firestore client for database operations.

    Returns:
        list: A list of device dictionaries, or None if the request fails.
    """
    print(f"\n--- Fetching All Devices for Site ID: {site_id} (with pagination) ---")
    url_path = f"/openapi/v1/{omadac_id}/sites/{site_id}/devices"
    headers = {"Authorization": f"AccessToken={access_token}"}
    
    all_devices = []
    page = 1
    page_size = 100  # Fetch 100 devices per API call

    while True:
        params = {
            "page": page,
            "pageSize": page_size
        }
        
        print(f"\nFetching page {page}...")
        response = make_request(base_url, "GET", url_path, headers=headers, params=params)

        if not response:
            print("Request failed. Aborting device fetch.")
            return None

        try:
            data = response.json()
            if data.get("errorCode") != 0:
                print(f"API Error on page {page}: {data.get('msg')}")
                return None

            result = data.get("result", {})
            current_page_devices = result.get("data", [])
            total_devices = result.get("totalRows", 0)

            if not current_page_devices:
                print("No more devices to fetch.")
                break

            all_devices.extend(current_page_devices)
            print(f"Fetched {len(current_page_devices)} devices. Total so far: {len(all_devices)}/{total_devices}")

            # --- Save devices to Firestore ---
            if db:
                print(f"Saving {len(current_page_devices)} devices to Firestore under sites/{site_id}/devices...")
                for device in current_page_devices:
                    try:
                        # Use the MAC address as the unique document ID for upserting
                        device_mac = device.get('mac')
                        if device_mac:
                            db.collection('sites').document(site_id).collection('devices').document(device_mac).set(device)
                    except Exception as e:
                        print(f"Error saving device {device.get('mac', 'N/A')} to Firestore: {e}")

            if len(all_devices) >= total_devices:
                print("\nAll devices have been retrieved.")
                break
            
            page += 1
        except (ValueError, KeyError) as e:
            print(f"An error occurred while parsing devices response: {e}")
            return None
            
    return all_devices
"""
This module handles device-related operations for the Omada controller.
"""
from authentication import make_request

def get_devices_list(base_url, access_token, omadac_id, site_id):
    """
    Retrieves a list of all devices for a specific site from the Omada controller.

    Args:
        base_url (str): The base URL of the Omada controller.
        access_token (str): The access token for authentication.
        omadac_id (str): The Omada Controller ID.
        site_id (str): The ID of the site whose devices are to be retrieved.

    Returns:
        list: A list of device dictionaries, or None if the request fails.
    """
    print(f"\n--- Fetching All Devices for Site ID: {site_id} (with pagination) ---")
    url_path = f"/openapi/v1/{omadac_id}/sites/{site_id}/devices"
    headers = {"Authorization": f"AccessToken={access_token}"}
    
    all_devices = []
    page = 1
    page_size = 100

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

            if len(all_devices) >= total_devices:
                print("\nAll devices have been retrieved.")
                break
            
            page += 1
        except (ValueError, KeyError) as e:
            print(f"An error occurred while parsing devices response: {e}")
            return None
            
    return all_devices

def get_device_details(base_url, access_token, omadac_id, site_id, mac):
    """
    Retrieves detailed information for a specific device.

    Args:
        base_url (str): The base URL of the Omada controller.
        access_token (str): The access token for authentication.
        omadac_id (str): The Omada Controller ID.
        site_id (str): The ID of the site where the device is located.
        mac (str): The MAC address of the device.

    Returns:
        dict: A dictionary of the device's details, or None if the request fails.
    """
    print(f"\n--- Fetching Device Details for MAC: {mac} in Site ID: {site_id} ---")
    url_path = f"/openapi/v1/{omadac_id}/sites/{site_id}/devices/{mac}"
    headers = {"Authorization": f"AccessToken={access_token}"}

    response = make_request(base_url, "GET", url_path, headers=headers)

    if not response:
        return None

    try:
        data = response.json()
        if data.get("errorCode") == 0:
            print(f"Successfully retrieved device details for {mac}.")
            return data.get("result")
        print(f"API Error fetching device details: {data.get('msg')} (Code: {data.get('errorCode')})")
    except (ValueError, KeyError) as e:
        print(f"An error occurred while parsing device details response: {e}")
    return None

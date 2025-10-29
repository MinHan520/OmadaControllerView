"""
This module handles audit log operations for the Omada controller.
"""
from authentication import make_request

def get_site_audit_logs(base_url, access_token, omadac_id, site_id, params):
    """
    Retrieves a list of audit logs for a specific site from the Omada controller.
    This function handles pagination to retrieve all logs.

    Args:
        base_url (str): The base URL of the Omada controller.
        access_token (str): The access token for authentication.
        omadac_id (str): The Omada Controller ID.
        site_id (str): The ID of the site whose logs are to be retrieved.
        params (dict): A dictionary of query parameters (filters, sorts, etc.).

    Returns:
        list: A list of audit log dictionaries, or None if the request fails.
    """
    print(f"\n--- Fetching Audit Logs for Site ID: {site_id} (with pagination) ---")
    url_path = f"/openapi/v1/{omadac_id}/sites/{site_id}/audit-logs"
    headers = {"Authorization": f"AccessToken={access_token}"}
    
    # If a specific page is requested in params, don't loop.
    fetch_all_pages = 'page' not in params

    all_logs = []
    page = int(params.get('page', 1))
    # pageSize is expected to be in the params dict from the user

    while True:
        # Update the page for each iteration
        params['page'] = page
        
        print(f"\nFetching page {page}...")
        response = make_request(base_url, "GET", url_path, headers=headers, params=params)

        if not response:
            print("Request failed. Aborting audit log fetch.")
            return None

        try:
            data = response.json()
            if data.get("errorCode") != 0:
                print(f"API Error on page {page}: {data.get('msg')}")
                return None

            result = data.get("result", {})
            current_page_logs = result.get("data", [])
            total_logs = result.get("totalRows", 0)

            if not current_page_logs:
                print("No more logs to fetch.")
                break

            all_logs.extend(current_page_logs)
            print(f"Fetched {len(current_page_logs)} logs. Total so far: {len(all_logs)}/{total_logs}")

            if len(all_logs) >= total_logs:
                print("\nAll audit logs have been retrieved.")
                break

            if not fetch_all_pages:
                # If we were asked for a specific page, we are done.
                break
            
            page += 1
        except (ValueError, KeyError) as e:
            print(f"An error occurred while parsing audit logs response: {e}")
            return None
            
    return all_logs

def get_global_audit_logs(base_url, access_token, omadac_id, params):
    """
    Retrieves a list of global audit logs from the Omada controller.
    This function handles pagination to retrieve all logs.

    Args:
        base_url (str): The base URL of the Omada controller.
        access_token (str): The access token for authentication.
        omadac_id (str): The Omada Controller ID.
        params (dict): A dictionary of query parameters (filters, sorts, etc.).

    Returns:
        list: A list of audit log dictionaries, or None if the request fails.
    """
    print("\n--- Fetching Global Audit Logs (with pagination) ---")
    url_path = f"/openapi/v1/{omadac_id}/audit-logs"
    headers = {"Authorization": f"AccessToken={access_token}"}
    
    # If a specific page is requested in params, don't loop.
    fetch_all_pages = 'page' not in params

    all_logs = []
    page = int(params.get('page', 1))
    # pageSize is expected to be in the params dict from the user

    while True:
        # Update the page for each iteration
        params['page'] = page
        
        print(f"\nFetching page {page}...")
        response = make_request(base_url, "GET", url_path, headers=headers, params=params)

        if not response:
            print("Request failed. Aborting global audit log fetch.")
            return None

        try:
            data = response.json()
            if data.get("errorCode") != 0:
                print(f"API Error on page {page}: {data.get('msg')}")
                return None

            result = data.get("result", {})
            current_page_logs = result.get("data", [])
            total_logs = result.get("totalRows", 0)

            if not current_page_logs:
                print("No more logs to fetch.")
                break

            all_logs.extend(current_page_logs)
            print(f"Fetched {len(current_page_logs)} logs. Total so far: {len(all_logs)}/{total_logs}")

            if len(all_logs) >= total_logs:
                print("\nAll global audit logs have been retrieved.")
                break

            if not fetch_all_pages:
                # If we were asked for a specific page, we are done.
                break
            
            page += 1
        except (ValueError, KeyError) as e:
            print(f"An error occurred while parsing global audit logs response: {e}")
            return None
            
    return all_logs
"""
This module handles audit log-related operations for the Omada controller.
"""
from authentication import make_request
from firebase_utils import save_document

def get_site_audit_logs(base_url, access_token, omadac_id, site_id, params=None):
    """
    Retrieves the audit logs for a specific site.

    Args:
        base_url (str): The base URL of the Omada controller.
        access_token (str): The access token for authentication.
        omadac_id (str): The Omada Controller ID.
        site_id (str): The ID of the site to retrieve the audit logs for.
        params (dict, optional): The URL parameters for the request. Defaults to None.

    Returns:
        list: A list of audit log entries, or None if it fails.
    """
    print(f"\n--- Fetching Audit Logs for Site (ID: {site_id}) ---")
    url_path = f"/openapi/v1/{omadac_id}/sites/{site_id}/audit-logs"
    headers = {"Authorization": f"AccessToken={access_token}"}

    all_logs = []
    page = 1
    page_size = 100
    
    # Initialize params if None
    if params is None:
        params = {}

    while True:
        # Update page and pageSize in params
        params["page"] = page
        params["pageSize"] = page_size
        
        print(f"Fetching audit logs page {page}...")
        response = make_request(base_url, "GET", url_path, headers=headers, params=params)

        if not response:
            print("Request failed. Aborting audit log fetch.")
            return None

        try:
            data = response.json()
            if data.get("errorCode") != 0:
                print(f"API Error fetching audit logs on page {page}: {data.get('msg')} (Code: {data.get('errorCode')})")
                return None

            result = data.get("result", {})
            current_page_logs = result.get("data", [])
            total_rows = result.get("totalRows", 0)
            
            if not current_page_logs:
                print("No more logs to fetch.")
                break

            all_logs.extend(current_page_logs)
            
            if current_page_logs:
                print(f"---[audit_logs] Sample Log Entry: {current_page_logs[0]} ---")

            # --- Firestore Integration ---
            print(f"---[audit_logs] Saving {len(current_page_logs)} site audit logs to Firestore... ---")
            for log in current_page_logs:
                # Use log ID as document ID if available, otherwise skip or use something else
                log_id = log.get("id")
                if log_id:
                    # Add site_id to the log data for context
                    log_with_context = log.copy()
                    log_with_context["siteId"] = site_id
                    save_document(collection_id="site_audit_logs", document_id=str(log_id), data=log_with_context)
            # ---------------------------

            print(f"Fetched {len(current_page_logs)} logs. Total so far: {len(all_logs)}/{total_rows}")

            if len(all_logs) >= total_rows:
                print("All audit logs have been retrieved.")
                break
            
            page += 1

        except (ValueError, KeyError) as e:
            print(f"An error occurred while parsing the audit logs response: {e}")
            return None

    return {"errorCode": 0, "result": {"data": all_logs, "totalRows": len(all_logs)}}

def get_global_audit_logs(base_url, access_token, omadac_id, params=None):
    """
    Retrieves the global audit logs.

    Args:
        base_url (str): The base URL of the Omada controller.
        access_token (str): The access token for authentication.
        omadac_id (str): The Omada Controller ID.
        params (dict, optional): The URL parameters for the request. Defaults to None.

    Returns:
        list: A list of global audit log entries, or None if it fails.
    """
    print(f"\n--- Fetching Global Audit Logs ---")
    url_path = f"/openapi/v1/{omadac_id}/audit-logs"
    headers = {"Authorization": f"AccessToken={access_token}"}

    response = make_request(base_url, "GET", url_path, headers=headers, params=params)

    if not response:
        return None

    try:
        data = response.json()
        if data.get("errorCode") == 0:
            print(f"Successfully retrieved global audit logs.")
            logs = data.get("result", {}).get("data", [])
            
            # --- Firestore Integration ---
            print(f"---[audit_logs] Saving {len(logs)} global audit logs to Firestore... ---")
            for log in logs:
                log_id = log.get("id")
                if log_id:
                    save_document(collection_id="global_audit_logs", document_id=str(log_id), data=log)
            # ---------------------------
            
            return logs
        print(f"API Error fetching global audit logs: {data.get('msg')} (Code: {data.get('errorCode')})")
    except (ValueError, KeyError) as e:
        print(f"An error occurred while parsing the global audit logs response: {e}")
    return None

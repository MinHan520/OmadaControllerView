"""
This module handles audit log-related operations for the Omada controller.
"""
from authentication import make_request

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

    response = make_request(base_url, "GET", url_path, headers=headers, params=params)

    if not response:
        return None

    try:
        data = response.json()
        if data.get("errorCode") == 0:
            print(f"Successfully retrieved audit logs for site {site_id}.")
            return data.get("result", {}).get("data", [])
        print(f"API Error fetching audit logs: {data.get('msg')} (Code: {data.get('errorCode')})")
    except (ValueError, KeyError) as e:
        print(f"An error occurred while parsing the audit logs response: {e}")
    return None

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
            return data.get("result", {}).get("data", [])
        print(f"API Error fetching global audit logs: {data.get('msg')} (Code: {data.get('errorCode')})")
    except (ValueError, KeyError) as e:
        print(f"An error occurred while parsing the global audit logs response: {e}")
    return None

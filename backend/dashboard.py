"""
This module handles dashboard-related operations for the Omada controller.
"""
from authentication import make_request

def get_site_overview_diagram(base_url, access_token, omadac_id, site_id):
    """
    Retrieves the overview diagram information for a specific site.

    Args:
        base_url (str): The base URL of the Omada controller.
        access_token (str): The access token for authentication.
        omadac_id (str): The Omada Controller ID.
        site_id (str): The ID of the site to retrieve the dashboard for.

    Returns:
        dict: A dictionary of the site's overview diagram info, or None if fails.
    """
    print(f"\n--- Fetching Dashboard for Site (ID: {site_id}) ---")
    url_path = f"/openapi/v1/{omadac_id}/sites/{site_id}/dashboard/overview-diagram"
    headers = {"Authorization": f"AccessToken={access_token}"}

    response = make_request(base_url, "GET", url_path, headers=headers)

    if not response:
        return None

    try:
        data = response.json()
        if data.get("errorCode") == 0:
            print(f"Successfully retrieved dashboard for site {site_id}.")
            dashboard_info = data.get("result")
            return dashboard_info
        print(f"API Error fetching dashboard: {data.get('msg')} (Code: {data.get('errorCode')})")
    except (ValueError, KeyError) as e:
        print(f"An error occurred while parsing the dashboard response: {e}")
    return None
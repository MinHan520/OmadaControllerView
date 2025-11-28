
from authentication import make_request
from firebase_utils import save_document # Import the save function

def get_sites_list(base_url, access_token, omadac_id):
    """
    Retrieves a list of all sites from the Omada controller (using v1 API) and saves them to Firestore.
    """
    print("\n---[sites-v1] Fetching All Sites... ---")
    url_path = f"/openapi/v1/{omadac_id}/sites"
    headers = {"Authorization": f"AccessToken={access_token}"}
    all_sites = []
    page = 1
    page_size = 100

    while True:
        params = {"page": page, "pageSize": page_size}
        response = make_request(base_url, "GET", url_path, headers=headers, params=params)
        if not response or response.status_code != 200:
            error_data = response.json() if response else {}
            return {"errorCode": -1, "msg": f"Request failed: {error_data.get('msg', 'Unknown error')}"}

        try:
            data = response.json()
            print(f"---[sites-v1] Raw API Response Data: {data} ---")
            if data.get("errorCode") != 0:
                return data

            result = data.get("result", {})
            current_page_data = result.get("data", [])
            total_rows = result.get("totalRows", 0)
            
            if not current_page_data:
                break

            # --- Firestore Integration ---
            print("---[sites-v1] Saving fetched sites to Firestore... ---")
            for site_data in current_page_data:
                save_document(collection_id="sites", document_id=site_data.get("siteId"), data=site_data)
            # ---------------------------

            all_sites.extend(current_page_data)
            if len(all_sites) >= total_rows:
                break
            page += 1

        except (ValueError, KeyError) as e:
            return {"errorCode": -1, "msg": f"Error parsing response: {e}"}
            
    print("\n---[sites-v1] All sites have been retrieved and saved to Firestore. ---")
    return {"errorCode": 0, "result": {"data": all_sites, "totalRows": len(all_sites)}}

def get_specific_site(base_url, access_token, omadac_id, site_id):
    """
    Retrieves details for a specific site.
    """
    print(f"\n---[sites-v1] Fetching Site Details for Site ID: {site_id} ---")
    url_path = f"/openapi/v1/{omadac_id}/sites/{site_id}"
    headers = {"Authorization": f"AccessToken={access_token}"}
    response = make_request(base_url, "GET", url_path, headers=headers)
    if not response:
        return {"errorCode": -1, "msg": "Request failed in make_request"}
    return response.json()

def get_site_dashboard(base_url, access_token, omadac_id, site_id):
    """
    Fetches the dashboard statistics for a specific site using the v2 API.
    """
    print(f"\n---[sites-v2] Fetching Dashboard for Site (ID: {site_id}) ---")
    url_path = f"/openapi/v2/{omadac_id}/sites/{site_id}/dashboard"
    headers = {"Authorization": f"AccessToken={access_token}"}
    response = make_request(base_url, "GET", url_path, headers=headers)
    if not response:
        return {"errorCode": -1, "msg": "Request failed in make_request"}
    return response.json()

def _get_paginated_data(base_url, access_token, omadac_id, site_id, endpoint_path):
    """
    Helper function to retrieve all paginated data from a given v1 endpoint.
    """
    headers = {"Authorization": f"AccessToken={access_token}"}
    all_data = []
    page = 1
    page_size = 100

    while True:
        params = {"page": page, "pageSize": page_size}
        response = make_request(base_url, "GET", endpoint_path, headers=headers, params=params)
        if not response or response.status_code != 200:
            error_data = response.json() if response else {}
            return {"errorCode": -1, "msg": f"Request failed: {error_data.get('msg', 'Unknown error')}"}

        try:
            data = response.json()
            if data.get("errorCode") != 0:
                return data

            result = data.get("result", {})
            current_page_data = result.get("data", [])
            total_rows = result.get("totalRows", 0)
            
            if not current_page_data:
                break

            all_data.extend(current_page_data)
            if len(all_data) >= total_rows:
                break
            page += 1

        except (ValueError, KeyError) as e:
            return {"errorCode": -1, "msg": f"Error parsing response: {e}"}

    return {"errorCode": 0, "result": {"data": all_data, "totalRows": len(all_data)}}

def get_site_devices(base_url, access_token, omadac_id, site_id):
    """
    Retrieves the device list for a specific site using the v1 API with pagination.
    """
    print(f"\n---[sites-v1] Fetching Devices for Site (ID: {site_id}) ---")
    url_path = f"/openapi/v1/{omadac_id}/sites/{site_id}/devices"
    return _get_paginated_data(base_url, access_token, omadac_id, site_id, url_path)

def get_site_audit_log(base_url, access_token, omadac_id, site_id):
    """
    Retrieves the audit log for a specific site using the v1 API with pagination.
    """
    print(f"\n---[sites-v1] Fetching Audit Log for Site (ID: {site_id}) ---")
    url_path = f"/openapi/v1/{omadac_id}/sites/{site_id}/logs/audit"
    return _get_paginated_data(base_url, access_token, omadac_id, site_id, url_path)

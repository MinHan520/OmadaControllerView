"""
This module handles site-related operations for the Omada controller.
"""
from authentication import make_request

def get_sites_list(base_url, access_token, omadac_id):
    """
    Retrieves a list of all sites from the Omada controller.

    Args:
        base_url (str): The base URL of the Omada controller.
        access_token (str): The access token for authentication.
        omadac_id (str): The Omada Controller ID.

    Returns:
        list: A list of site dictionaries, or None if the request fails.
    """
    print("\n--- Fetching All Sites (with pagination) ---")
    url_path = f"/openapi/v1/{omadac_id}/sites"
    headers = {"Authorization": f"AccessToken={access_token}"}
    
    all_sites = []
    page = 1
    page_size = 100  # Fetch 100 sites per API call (max is 1000)

    while True:
        params = {
            "page": page,
            "pageSize": page_size
        }
        
        print(f"\nFetching page {page}...")
        response = make_request(base_url, "GET", url_path, headers=headers, params=params)

        if not response:
            print("Request failed. Aborting site fetch.")
            return None

        try:
            data = response.json()
            if data.get("errorCode") != 0:
                print(f"API Error on page {page}: {data.get('msg')}")
                return None

            result = data.get("result", {})
            current_page_sites = result.get("data", [])
            total_sites = result.get("totalRows", 0)

            if not current_page_sites:
                print("No more sites to fetch.")
                break

            all_sites.extend(current_page_sites)
            print(f"Fetched {len(current_page_sites)} sites. Total so far: {len(all_sites)}/{total_sites}")

            if len(all_sites) >= total_sites:
                print("\nAll sites have been retrieved.")
                break
            
            page += 1
        except (ValueError, KeyError) as e:
            print(f"An error occurred while parsing sites response: {e}")
            return None
            
    return all_sites

def get_specific_site(base_url, access_token, omadac_id, site_id):
    """
    Retrieves information for a specific site from the Omada controller.

    Args:
        base_url (str): The base URL of the Omada controller.
        access_token (str): The access token for authentication.
        omadac_id (str): The Omada Controller ID.
        site_id (str): The ID of the site to retrieve.

    Returns:
        dict: A dictionary of the site's information, or None if the request fails.
    """
    print(f"\n--- Fetching Specific Site (ID: {site_id}) ---")
    url_path = f"/openapi/v1/{omadac_id}/sites/{site_id}"
    headers = {"Authorization": f"AccessToken={access_token}"}

    response = make_request(base_url, "GET", url_path, headers=headers)

    if not response:
        return None

    try:
        data = response.json()
        if data.get("errorCode") == 0:
            site_info = data.get("result")
            print(f"Successfully retrieved information for site '{site_info.get('name', site_id)}'.")
            return site_info
        print(f"API Error fetching site {site_id}: {data.get('msg')} (Code: {data.get('errorCode')})")
    except (ValueError, KeyError) as e:
        print(f"An error occurred while parsing the site response: {e}")
    return None
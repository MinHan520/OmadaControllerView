"""
This module is for command-line interface (CLI) interaction and is not part of the web API.
This module handles the user login flow.
https://10.30.31.115:8043

https://192.168.0.7:8043
https://192.168.0.106:8043
"""
import getpass
import json
import firebase_admin
from firebase_admin import credentials, firestore
from authentication import run_authentication_flow, OMADAC_ID
from sites import get_sites_list, get_specific_site
from dashboard import get_site_overview_diagram
from devices import get_devices_list
from audit_logs import get_site_audit_logs, get_global_audit_logs
from chatbot import initialize_dependencies as initialize_chatbot, get_chat_response, read_all_firestore_data

def initialize_firestore(service_account_key_path="serviceAccountKey.json"):
    """
    Initializes the Firebase Admin SDK and returns a Firestore client.
    Handles cases where the app is already initialized.

    Args:
        service_account_key_path (str): Path to the Firebase service account key.

    Returns:
        firestore.Client: The Firestore database client, or None if initialization fails.
    """
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(service_account_key_path)
            firebase_admin.initialize_app(cred)
        return firestore.client()
    except Exception as e:
        print(f"Error initializing Firestore: {e}")
        return None

def main():
    """
    Main function to get user credentials and run the authentication flow.
    """
    print("--- Omada Controller Login ---")
    base_url = input("Enter the controller's base URL (e.g., https://192.168.1.100): ")
    username = input("Enter your username: ")
    try:
        password = getpass.getpass("Enter your password: ")
    except getpass.GetPassWarning as error:
        print('ERROR', error)
        return

    access_token, refresh_token = run_authentication_flow(base_url, username, password)

    if access_token:
        print("\n\n✅ Authentication Successful!")

        # Initialize Firestore
        print("\n--- Initializing Firestore ---")
        db = initialize_firestore("omadasdn-52c0d-firebase-adminsdk-fbsvc-d1221871c5.json")

        if db:
            # Proceed with normal application logic
            print("✅ Firestore client initialized successfully.")
            # Proceed to the main application menu, passing the db client
            main_menu(base_url, access_token, db)
        else:
            print("❌ Could not initialize Firestore. Database features will be unavailable.")
            # You could choose to exit here, or proceed without db features
            # main_menu(base_url, access_token, None)

def handle_dashboard_view(base_url, access_token, db):
    """
    Lists sites and prompts the user to view a dashboard before the main menu.
    """
    print("\nFetching available sites to display a dashboard...")
    sites = get_sites_list(base_url, access_token, OMADAC_ID, db)
    if not sites:
        print("Could not retrieve sites.")
        return

    print("\n--- Available Sites ---")
    for site in sites:
        print(f"  - Name: {site.get('name', 'N/A')}, ID: {site.get('id')}")

    site_id = input("\nEnter a Site ID to view its dashboard (or press Enter to skip): ")
    if site_id:
        dashboard_info = get_site_overview_diagram(base_url, access_token, OMADAC_ID, site_id, db)
        if dashboard_info:
            print("\n--- Site Dashboard Overview ---")
            print(json.dumps(dashboard_info, indent=2))

def main_menu(base_url, access_token, db):
    """Displays the main menu and routes to sub-menus."""
    while True:
        print("\n--- Main Menu ---")
        print("1. Site Management")
        print("2. Device Management")
        print("3. Log Management")
        print("4. View a Site's Dashboard")
        print("5. AI Chatbot Assistant")
        print("6. Read All Firestore Data (Diagnostic)")
        print("7. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            handle_site_management(base_url, access_token, db)
        elif choice == '2':
            handle_device_management(base_url, access_token, db)
        elif choice == '3':
            handle_logs_management(base_url, access_token, db)
        elif choice == '4':
            handle_dashboard_view(base_url, access_token, db)
        elif choice == '5':
            handle_ai_chatbot(db)
        elif choice == '6':
            read_all_firestore_data(db)
        elif choice == '7':
            print("\nExiting. Goodbye!")
            break
        else:
            print("\nInvalid choice. Please try again.")

def handle_device_management(base_url, access_token, db):
    """Handles listing devices for a user-selected site."""
    print("\n--- Device Management: Select a Site ---")
    sites = get_sites_list(base_url, access_token, OMADAC_ID, db)
    if not sites:
        print("Could not retrieve sites to select from.")
        return

    for site in sites:
        print(f"  - Name: {site.get('name', 'N/A')}, ID: {site.get('id')}")

    site_id = input("\nEnter the Site ID to view its devices: ")
    if site_id:
        devices = get_devices_list(base_url, access_token, OMADAC_ID, site_id, db)
        if devices:
            print("\n--- Device List ---")
            print(json.dumps(devices, indent=2))

def handle_site_management(base_url, access_token, db):
    """
    Displays a menu for site operations.
    """
    while True:
        print("\n--- Site Management ---")
        print("1. View all sites")
        print("2. View a specific site")
        print("3. Return to Main Menu")
        choice = input("Enter your choice: ")

        if choice == '1':
            sites = get_sites_list(base_url, access_token, OMADAC_ID, db)
            if sites:
                print("\n--- Available Sites ---")
                # Pretty print the site list
                print(json.dumps(sites, indent=2))
        elif choice == '2':
            site_id = input("Enter the site ID to view: ")
            if site_id:
                site_info = get_specific_site(base_url, access_token, OMADAC_ID, site_id, db)
                if site_info:
                    print("\n--- Site Details ---")
                    print(json.dumps(site_info, indent=2))
        elif choice == '3':
            return # Return to the main_menu loop
        else:
            print("\nInvalid choice. Please try again.")

def handle_logs_management(base_url, access_token, db):
    """Displays a menu for log operations."""
    while True:
        print("\n--- Log Management ---")
        print("1. View Site Audit Logs")
        print("2. View Global Audit Logs")
        print("3. View Application Usage (Not Implemented)")
        print("4. Return to Main Menu")
        choice = input("Enter your choice: ")

        if choice == '1':
            handle_site_audit_log_view(base_url, access_token, db)
        elif choice == '2':
            handle_global_audit_log_view(base_url, access_token, db)
        elif choice == '3':
            print("\nThis feature is not yet implemented.")
        elif choice == '4':
            return
        else:
            print("\nInvalid choice. Please try again.")

def handle_site_audit_log_view(base_url, access_token, db):
    """Handles fetching and displaying site audit logs."""
    print("\n--- View Site Audit Logs: Select a Site ---")
    sites = get_sites_list(base_url, access_token, OMADAC_ID, db)
    if not sites:
        print("Could not retrieve sites to select from.")
        return

    for site in sites:
        print(f"  - Name: {site.get('name', 'N/A')}, ID: {site.get('id')}")

    site_id = input("\nEnter the Site ID to view its audit logs: ")
    if not site_id:
        return

    params = _get_audit_log_params_from_user()

    logs = get_site_audit_logs(base_url, access_token, OMADAC_ID, site_id, params, db)
    if logs:
        print("\n--- Site Audit Logs ---")
        print(json.dumps(logs, indent=2))

def handle_global_audit_log_view(base_url, access_token, db):
    """Handles fetching and displaying global audit logs."""
    print("\n--- View Global Audit Logs ---")
    
    params = _get_audit_log_params_from_user()

    logs = get_global_audit_logs(base_url, access_token, OMADAC_ID, params, db)
    if logs:
        print("\n--- Global Audit Logs ---")
        print(json.dumps(logs, indent=2))

def _get_audit_log_params_from_user():
    """Helper function to collect audit log filter parameters from the user."""
    print("\n--- Configure Log Filters (press Enter to skip a filter) ---")
    params = {}
    params['pageSize'] = input("Page Size (1-1000, e.g., 100): ") or "100"

    sort_time = input("Sort by time ('asc' or 'desc'): ")
    if sort_time:
        params['sorts.time'] = sort_time
    
    filter_result = input("Filter by result (0 for success, 1 for failed): ")
    if filter_result:
        params['filters.result'] = filter_result
    
    filter_level = input("Filter by level (Error, Warning, Information): ")
    if filter_level:
        params['filters.level'] = filter_level
    
    filter_types = input("Filter by audit types (comma-separated, e.g., Log,Cloud Access): ")
    if filter_types:
        params['filters.auditTypes'] = filter_types
    
    search_key = input("Fuzzy search for content: ")
    if search_key:
        params['searchKey'] = search_key
    return params

def handle_ai_chatbot(db):
    """
    Initializes and runs a conversational session with the AI chatbot.
    """
    print("\n--- 🤖 Initializing AI Chatbot Assistant ---")
    # The chatbot's initializer is idempotent for Firebase and will configure Gemini.
    # We only need the model from it, as we already have the db client.
    _, model = initialize_chatbot()

    if not model:
        print("❌ Could not initialize the AI model. The chatbot is unavailable.")
        return

    print("\n✅ Chatbot is ready. Ask questions about your Omada network.")
    print("   Type 'exit' to return to the main menu.")

    chat_history = []
    while True:
        try:
            user_query = input("\nYou: ")
            if user_query.lower() == 'exit':
                print("Returning to the main menu...")
                break

            # Get the response from the chatbot's main function
            response_dict = get_chat_response(user_query, chat_history, db, model)
            bot_answer = response_dict.get("answer", "I'm sorry, I don't have an answer for that.")

            print(f"Bot: {bot_answer}")

            # Update the chat history for conversational context
            chat_history.append(f"User: {user_query}")
            chat_history.append(f"Bot: {bot_answer}")

        except KeyboardInterrupt:
            print("\nReturning to the main menu...")
            break

if __name__ == "__main__":
    main()

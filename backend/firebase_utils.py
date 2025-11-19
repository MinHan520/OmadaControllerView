
import os
import firebase_admin
from firebase_admin import credentials, firestore

# Path to the service account key file.
# IMPORTANT: Ensure 'serviceAccountKey.json' is in the project's root directory.
SERVICE_ACCOUNT_KEY_PATH = 'serviceAccountKey.json'
db = None

def initialize_firestore():
    """
    Initializes the Firestore client using a service account.
    Checks if the key file exists before attempting to initialize.
    """
    global db
    if firebase_admin._apps:
        # Already initialized
        if not db:
            db = firestore.client()
        return

    if not os.path.exists(SERVICE_ACCOUNT_KEY_PATH):
        print(f"--- FIREBASE ERROR: Service account key not found at '{SERVICE_ACCOUNT_KEY_PATH}'. ---")
        print("--- Firebase integration will be disabled. Please add the key file to the project root. ---")
        return

    try:
        cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("--- Firebase initialized successfully. Firestore client is ready. ---")
    except Exception as e:
        print(f"--- FIREBASE ERROR: Failed to initialize Firebase: {e} ---")
        db = None

def save_document(collection_id, document_id, data):
    """
    Saves a dictionary of data to a Firestore document.
    """
    if not db:
        # This check prevents errors if initialization failed.
        # The data will still be returned to the frontend, but not saved to the DB.
        print(f"--- Firestore is not initialized. Skipping save for doc '{document_id}'. ---")
        return False
    
    if not document_id:
        print(f"--- FIRESTORE WARNING: Document ID is missing. Cannot save to collection '{collection_id}'. ---")
        return False

    try:
        doc_ref = db.collection(collection_id).document(document_id)
        doc_ref.set(data, merge=True) # Use merge=True to update/create without overwriting all fields
        print(f"--- Firestore: Saved document '{document_id}' to collection '{collection_id}'. ---")
        return True
    except Exception as e:
        print(f"--- FIRESTORE ERROR: Failed to save document '{document_id}': {e} ---")
        return False

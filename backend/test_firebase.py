
import firebase_admin
from firebase_admin import credentials, firestore
import os

SERVICE_ACCOUNT_KEY_PATH = 'serviceAccountKey.json'

def test_connection():
    if not os.path.exists(SERVICE_ACCOUNT_KEY_PATH):
        print("Key file not found.")
        return

    try:
        cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        print("Attempting to write to Firestore...")
        doc_ref = db.collection('test_collection').document('test_doc')
        doc_ref.set({'test': 'data'})
        print("Successfully wrote to Firestore.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_connection()

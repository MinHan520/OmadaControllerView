import json
import requests

# Replace with your Firebase project ID and service account key file
PROJECT_ID = "omadasdn-52c0d"
SERVICE_ACCOUNT_KEY_PATH = "omadasdn-52c0d-firebase-adminsdk-fbsvc-d1221871c5.json"

def get_access_token():
    """
    Authenticates with Firebase and returns an access token.
    """
    with open(SERVICE_ACCOUNT_KEY_PATH, "r") as f:
        service_account_key = json.load(f)

    auth_url = "https://accounts.google.com/o/oauth2/token"
    auth_payload = {
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": _create_jwt(service_account_key),
    }

    response = requests.post(auth_url, data=auth_payload)
    response.raise_for_status()  # Raise an exception for bad status codes
    return response.json()["access_token"]

def _create_jwt(service_account_key):
    """
    Creates a JWT for authentication.
    """
    import time
    from jose import jwt

    now = int(time.time())
    payload = {
        "iss": service_account_key["client_email"],
        "sub": service_account_key["client_email"],
        "aud": "https://accounts.google.com/o/oauth2/token",
        "iat": now,
        "exp": now + 3600,  # Token is valid for 1 hour
        "scope": "https://www.googleapis.com/auth/datastore",
    }

    return jwt.encode(payload, service_account_key["private_key"], algorithm="RS256")

def get_document(access_token, collection_id, document_id):
    """
    Gets a document from Firestore.
    """
    url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/{collection_id}/{document_id}"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def set_document(access_token, collection_id, document_id, data):
    """
    Sets a document in Firestore.
    """
    url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/{collection_id}/{document_id}"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.patch(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def read_all_firestore_data(access_token):
    """
    Reads all documents from all collections in Firestore.
    """
    collections_url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents:listCollectionIds"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.post(collections_url, headers=headers, json={})
    response.raise_for_status()
    collection_ids = response.json().get("collectionIds", [])

    all_data = {}
    for collection_id in collection_ids:
        documents_url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/{collection_id}"
        response = requests.get(documents_url, headers=headers)
        response.raise_for_status()
        all_data[collection_id] = response.json()

    return all_data
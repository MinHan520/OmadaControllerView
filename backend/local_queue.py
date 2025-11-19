"""
This module provides a local SQLite-based queue for pending Firestore writes.
It allows the application to save data locally when offline and sync it later.
"""
import sqlite3
import json

DB_FILE = "offline_queue.db"

def initialize_local_queue():
    """
    Initializes the local SQLite database and creates the 'pending_writes' table
    if it doesn't already exist. This should be called once on application startup.
    """
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            # The UNIQUE constraint on (collection_path, document_id) is crucial
            # for the INSERT OR REPLACE logic to work as an "upsert".
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pending_writes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    collection_path TEXT NOT NULL,
                    document_id TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    UNIQUE(collection_path, document_id)
                )
            """)
        print("✅ Local offline queue initialized successfully.")
    except sqlite3.Error as e:
        print(f"❌ Error initializing local queue: {e}")

def queue_write(collection_path, document_id, data):
    """
    Queues a Firestore write operation to the local SQLite database.
    Uses 'INSERT OR REPLACE' to perform an upsert, ensuring the latest data
    for a given document is stored.

    Args:
        collection_path (str): The path of the Firestore collection.
        document_id (str): The ID of the document.
        data (dict): The Python dictionary to be written to the document.
    """
    try:
        data_json = json.dumps(data)
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO pending_writes (collection_path, document_id, data_json) VALUES (?, ?, ?)",
                (collection_path, document_id, data_json)
            )
            conn.commit()
        print(f"Offline: Queued write for document '{document_id}' in collection '{collection_path}'.")
    except (sqlite3.Error, TypeError) as e:
        print(f"❌ Error queueing write for document '{document_id}': {e}")

def sync_offline_writes(db):
    """
    Attempts to sync all pending writes from the local queue to Firestore.
    Successfully synced records are removed from the local queue.

    Args:
        db (firestore.Client): An initialized Firestore client.
    """
    if not db:
        print("Firestore client not available. Skipping offline sync.")
        return

    print("\n--- 🔄 Starting sync of offline writes to Firestore ---")
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, collection_path, document_id, data_json FROM pending_writes")
            pending_writes = cursor.fetchall()

            if not pending_writes:
                print("No pending writes to sync.")
                return

            successful_ids = []
            for row in pending_writes:
                try:
                    data = json.loads(row['data_json'])
                    db.collection(row['collection_path']).document(row['document_id']).set(data)
                    successful_ids.append(row['id'])
                    print(f"  ✅ Synced document: {row['collection_path']}/{row['document_id']}")
                except Exception as e:
                    print(f"  ❌ Failed to sync document {row['document_id']}. Will retry later. Error: {e}")

            if successful_ids:
                # Delete all successfully synced rows in a single operation
                placeholders = ','.join('?' for _ in successful_ids)
                cursor.execute(f"DELETE FROM pending_writes WHERE id IN ({placeholders})", successful_ids)
                conn.commit()
                print(f"--- ✅ Sync complete. {len(successful_ids)} records removed from local queue. ---")
    except sqlite3.Error as e:
        print(f"❌ Error during sync process: {e}")
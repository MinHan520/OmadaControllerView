"""
This module provides a complete backend for an advanced, conversational RAG
(Retrieval-Augmented Generation) chatbot. It uses the Google Gemini API for
natural language understanding and generation, and Firebase Firestore as its
knowledge base for Omada Controller network information.
"""
import os
import json
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, firestore

# --- Boilerplate & Initialization ---

def initialize_dependencies():
    """
    Initializes all external services (Firebase and Gemini).
    Reads configuration from environment variables.
    """
    print("--- Initializing Dependencies ---")
    db_client = None
    model = None

    # 1. Initialize Firebase
    try:
        # The GOOGLE_APPLICATION_CREDENTIALS env var should point to your service account key file.
        # If it's set, initialize_app() will use it automatically.
        if not firebase_admin._apps:
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred)
        db_client = firestore.client()
        print("✅ Firebase initialized successfully.")
    except Exception as e:
        print(f"❌ Error initializing Firebase: {e}")
        print("   Please ensure the 'GOOGLE_APPLICATION_CREDENTIALS' environment variable is set correctly.")

    # 2. Configure Gemini API
    try:
        #gemini_api_key = os.environ.get("GEMINI_API_KEY")
        gemini_api_key = 'AIzaSyBaKY-E0J_Qz1R4d1sUpNxxjOaOkfLmJV4'
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable not found.")
        genai.configure(api_key=gemini_api_key)
        # Using a valid, recent model name as the one in the prompt may be a future version.
        model = genai.GenerativeModel(
            'gemini-2.5-flash',
            generation_config={"response_mime_type": "application/json"}
        )
        print("✅ Gemini API configured successfully.")
    except Exception as e:
        print(f"❌ Error configuring Gemini API: {e}")

    return db_client, model

def get_chat_response(query: str, history: list, db, model) -> dict:
    """
    Handles the main logic flow for the RAG chatbot.

    Args:
        query (str): The user's current question.
        history (list): A list of prior messages in the conversation.
        db (firestore.Client): An initialized Firestore client.
        model (genai.GenerativeModel): An initialized Gemini model.

    Returns:
        dict: A dictionary containing the bot's answer, e.g., {"answer": "..."}.
    """
    if not db or not model:
        return {"answer": "I'm sorry, my backend services are not configured correctly. Please contact the administrator."}

    try:
        # --- Step 1: The "Omada Controller" Guardrail (Input Validation) ---
        guardrail_prompt = """
        You are a classification model. Your sole purpose is to determine if a user's question is related to an Omada Controller network system. Respond with a single, valid JSON object: {"is_related": true} if the question is about network devices, SSIDs, clients, VLANs, or network status. Respond with {"is_related": false} if the question is about any other topic (like weather, history, cooking, or other products).
        """
        guardrail_response = model.generate_content([guardrail_prompt, query])
        guardrail_result = json.loads(guardrail_response.text)

        if not guardrail_result.get("is_related"):
            return {"answer": "I can only answer questions related to Omada Controller. Please try related questions."}

        # --- Step 2: Intent & Entity Analysis (The "Missing Information" Check) ---
        analysis_prompt = """
        You are an AI assistant analyzing a user's request for a network admin. Analyze the "Current Query" in the context of the "Chat History".
        Your goal is to decide if you have enough information to search the database.
        Respond with a single, valid JSON object based on one of these two scenarios:

        1. **If the query is clear and specific** (e.g., "What is the status of the 'Main AP'?", or "What about the 'Guest SSID'?"):
           Respond with:
           `{"is_clear": true, "entities": {"device": "Main AP", "client": null, "topic": "status"}}`
           (Fill in `entities` with all extracted items: `device`, `client`, `network`, `topic`, etc.)

        2. **If the query is vague, ambiguous, or missing information** (e.g., "What is the status?", "Tell me about it.", "How many users?"):
           Respond with:
           `{"is_clear": false, "clarification_question": "Which device are you asking about?"}`
           (The `clarification_question` should be a natural, helpful follow-up.)
        """
        analysis_response = model.generate_content([analysis_prompt, f"Chat History: {history}", f"Current Query: {query}"])
        analysis_result = json.loads(analysis_response.text)

        # --- Step 3: Logic Branch (Clarify or Retrieve) ---
        if not analysis_result.get("is_clear"):
            return {"answer": analysis_result.get("clarification_question", "I'm not sure what you mean. Could you be more specific?")}

        # --- Step 4: Targeted Data Retrieval (Smart Retrieval) ---
        entities = analysis_result.get("entities", {})
        context_data = []
        #app_id = os.environ.get("APP_ID")
        app_id = 'omadasdn-52c0d'
        if not app_id:
            return {"answer": "Configuration error: APP_ID is not set."}

        print(f"🔍 Retrieving data for entities: {entities}")

        if entities.get("device"):
            device_ref = db.collection(f'artifacts/{app_id}/public/data/omada_devices')
            docs = device_ref.where('name', '==', entities['device']).stream()
            for doc in docs:
                context_data.append(doc.to_dict())

        if entities.get("network"):
            network_ref = db.collection(f'artifacts/{app_id}/public/data/omada_networks')
            docs = network_ref.where('name', '==', entities['network']).stream()
            for doc in docs:
                context_data.append(doc.to_dict())

        # Add other entity retrieval logic here (e.g., for clients, SSIDs, etc.)

        if not context_data:
            firestore_context = "No matching items were found in the database for the given query."
        else:
            firestore_context = json.dumps(context_data, indent=2)

        print(f"📚 Context for generation:\n{firestore_context}")

        # --- Step 5: Augmentation & Generation (Final Answer) ---
        final_answer_prompt = """
        You are an expert AI assistant for the Omada Controller network. You will be given a user's question and a targeted JSON blob of data from the database that *specifically* relates to their question.
        Your task is to answer the user's question based *only* on the provided data.
        - Do not make up information.
        - If the provided data is empty or states no items were found, inform the user (e.g., "I couldn't find a device with that name.").
        - If the data has the information, answer the question clearly.
        """
        # Re-initialize the model for text response
        text_model = genai.GenerativeModel('gemini-2.5-flash')
        final_response = text_model.generate_content([
            final_answer_prompt,
            f"Chat History: {history}",
            f"Database Context: {firestore_context}",
            f"User's Question: {query}"
        ])

        # --- Step 6: Final Response ---
        return {"answer": final_response.text}

    except json.JSONDecodeError as e:
        print(f"❌ JSON Parsing Error: {e}")
        return {"answer": "I'm sorry, I had trouble understanding the data structure. Please try again."}
    except Exception as e:
        print(f"❌ An unexpected error occurred in get_chat_response: {e}")
        return {"answer": "I'm sorry, something went wrong on my end. Please try again later."}


if __name__ == "__main__":
    # --- Setup: Ensure environment variables are set ---
    # 1. GOOGLE_APPLICATION_CREDENTIALS: Path to your Firebase service account JSON file.
    #    e.g., "C:\Users\user\secrets\my-firebase-key.json"
    # 2. GEMINI_API_KEY: Your API key for the Google Gemini service.
    # 3. APP_ID: The application ID for your Firestore data structure.
    #    e.g., "omadasdn-52c0d"

    # Initialize services once at the start
    db, model = initialize_dependencies()

    if not db or not model:
        print("\nExiting due to initialization failure.")
    else:
        print("\n--- 🤖 Omada RAG Chatbot Ready ---")
        print("Type 'exit' to end the conversation.")

        # This list will store the conversation history
        chat_history = []

        while True:
            try:
                user_query = input("\nYou: ")
                if user_query.lower() == 'exit':
                    print("Bot: Goodbye!")
                    break

                # Get the response from the main function
                response_dict = get_chat_response(user_query, chat_history, db, model)
                bot_answer = response_dict.get("answer", "I'm sorry, I don't have an answer for that.")

                print(f"Bot: {bot_answer}")

                # --- Crucially, update the chat history ---
                # The format should match what the model expects.
                # A simple list of alternating user/bot messages is a good start.
                chat_history.append(f"User: {user_query}")
                chat_history.append(f"Bot: {bot_answer}")

            except KeyboardInterrupt:
                print("\nBot: Goodbye!")
                break
            except Exception as e:
                print(f"\nAn error occurred in the main loop: {e}")
                break

def read_all_firestore_data(db):
    """
    Reads and prints all data from the Firestore database to verify connection and access.
    This is a diagnostic function that traverses known collections and subcollections.

    Args:
        db (firestore.Client): An initialized Firestore client.
    """
    if not db:
        print("❌ Firestore client is not available.")
        return

    print("\n--- 🔍 Reading all data from Firestore ---")
    try:
        # List of known top-level collections
        top_level_collections = ['sites', 'global_audit_logs']

        for collection_name in top_level_collections:
            print(f"\n[Collection: {collection_name}]")
            docs = db.collection(collection_name).stream()
            doc_count = 0
            for doc in docs:
                doc_count += 1
                print(f"  📄 Document: {doc.id}")
                print(f"    Data: {json.dumps(doc.to_dict(), indent=4, default=str)}")

                # Specifically check for subcollections within 'sites'
                if collection_name == 'sites':
                    subcollections = doc.reference.collections()
                    for subcollection in subcollections:
                        print(f"    [Subcollection: {subcollection.id}]")
                        sub_docs = subcollection.stream()
                        for sub_doc in sub_docs:
                            print(f"      📄 Sub-Document: {sub_doc.id}")
                            print(f"        Data: {json.dumps(sub_doc.to_dict(), indent=4, default=str)}")
            if doc_count == 0:
                print("  (No documents found in this collection)")
    except Exception as e:
        print(f"❌ An error occurred while reading from Firestore: {e}")
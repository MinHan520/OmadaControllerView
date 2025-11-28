import os
import json
import google.generativeai as genai
from chatbot_persona import SYSTEM_PERSONA
from firebase_utils import db, initialize_firestore

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyCayyIj5ogZw787WSvcgMpGRv-0DsxjaM8"
if not GEMINI_API_KEY:
    print("--- WARNING: GEMINI_API_KEY not found. Chatbot will not function correctly. ---")

try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"--- Error configuring Gemini: {e} ---")

def get_chat_response(query: str, history: list, db_client, model_unused=None) -> dict:
    """
    Handles the main logic flow for the RAG chatbot.
    """
    if not db_client:
        return {"answer": "I'm sorry, my backend services are not configured correctly. Please contact the administrator."}

    try:
        # Use a valid model
        model = genai.GenerativeModel('gemini-2.5-flash')

        # --- Step 1: The "Omada Controller" Guardrail (Input Validation) ---
        guardrail_prompt = """
        You are a classification model. Your sole purpose is to determine if a user's question is related to an Omada Controller network system, networking, or the chatbot's capabilities. 
        Respond with a single, valid JSON object: {"is_related": true} if the question is about network devices, SSIDs, clients, VLANs, network status, logs, or traffic. 
        Respond with {"is_related": false} if the question is about any other topic (like weather, history, cooking, or other products).
        """
        try:
            guardrail_response = model.generate_content([guardrail_prompt, query])
            guardrail_result = json.loads(guardrail_response.text.strip().replace('```json', '').replace('```', ''))
            
            if not guardrail_result.get("is_related"):
                return {"answer": "I can only answer questions related to your Omada Controller and network. Please try related questions."}
        except Exception as e:
            print(f"Guardrail check failed: {e}")
            # Fallback: assume related if check fails to avoid blocking valid queries due to JSON errors
            pass

        # --- Step 2: Intent & Entity Analysis ---
        analysis_prompt = """
        You are an AI assistant analyzing a user's request for a network admin. Analyze the "Current Query" in the context of the "Chat History".
        Your goal is to decide if you have enough information to search the database.
        Respond with a single, valid JSON object based on one of these two scenarios:

        1. **If the query is clear and specific** (e.g., "What is the status of the 'Main AP'?", "Show me error logs", "How many devices?"):
           Respond with:
           `{"is_clear": true, "entities": {"device": "Main AP", "topic": "status", "collection": "devices"}}`
           (Fill in `entities` with extracted items. Valid collections: 'devices', 'sites', 'audit_logs', 'traffic_logs', 'all')

        2. **If the query is vague** (e.g., "Tell me about it.", "Status?"):
           Respond with:
           `{"is_clear": false, "clarification_question": "Which device or aspect of the network are you asking about?"}`
        """
        try:
            analysis_response = model.generate_content([analysis_prompt, f"Chat History: {history}", f"Current Query: {query}"])
            analysis_text = analysis_response.text.strip().replace('```json', '').replace('```', '')
            analysis_result = json.loads(analysis_text)

            if not analysis_result.get("is_clear"):
                return {"answer": analysis_result.get("clarification_question", "I'm not sure what you mean. Could you be more specific?")}
            
            entities = analysis_result.get("entities", {})
        except Exception as e:
            print(f"Analysis failed: {e}")
            entities = {"collection": "all"} # Fallback to fetching everything

        # --- Step 3: Targeted Data Retrieval ---
        print(f"🔍 Retrieving data for entities: {entities}")
        context_data = []
        
        # Helper to fetch and format
        def fetch_collection(col_name, limit=10):
            ref = db_client.collection(col_name).limit(limit)
            docs = ref.stream()
            data = []
            for doc in docs:
                d = doc.to_dict()
                d['id'] = doc.id
                data.append(d)
            return data

        target_collection = entities.get("collection", "all")
        
        if target_collection == 'devices' or target_collection == 'all':
            devices = fetch_collection('devices')
            if devices:
                context_data.append(f"Devices: {json.dumps(devices, default=str)}")
        
        if target_collection == 'sites' or target_collection == 'all':
            sites = fetch_collection('sites')
            if sites:
                context_data.append(f"Sites: {json.dumps(sites, default=str)}")

        if target_collection == 'audit_logs' or target_collection == 'all' or entities.get("topic") == "logs":
            logs = fetch_collection('audit_logs', limit=5)
            if logs:
                context_data.append(f"Recent Logs: {json.dumps(logs, default=str)}")

        if target_collection == 'traffic_logs' or target_collection == 'all' or entities.get("topic") == "traffic":
            traffic = fetch_collection('traffic_logs', limit=3)
            if traffic:
                context_data.append(f"Recent Traffic: {json.dumps(traffic, default=str)}")

        firestore_context = "\n".join(context_data) if context_data else "No specific data found in database."
        print(f"📚 Context size: {len(firestore_context)} chars")

        # --- Step 4: Augmentation & Generation ---
        final_answer_prompt = f"""
        {SYSTEM_PERSONA}

        You will be given a user's question and a JSON blob of data from the database.
        Your task is to answer the user's question based *only* on the provided data.
        - Do not make up information.
        - If the provided data is empty or states no items were found, inform the user.
        - If the data has the information, answer the question clearly.

        Database Context:
        {firestore_context}

        Chat History:
        {history}

        User's Question:
        {query}

        Answer:
        """
        
        final_response = model.generate_content(final_answer_prompt)
        return {"answer": final_response.text}

    except Exception as e:
        print(f"❌ An unexpected error occurred in get_chat_response: {e}")
        return {"answer": "I'm sorry, something went wrong on my end. Please try again later."}

def generate_rag_response(user_message: str, access_token: str, base_url: str) -> str:
    """
    Wrapper to maintain compatibility with main.py route.
    """
    # In a real app, we'd fetch history from DB using a session ID.
    # For now, we pass an empty history or could implement simple in-memory history if needed.
    # The frontend sends 'message', so we treat each request as standalone or rely on client-side history if we were sending it.
    # But get_chat_response takes 'history'. We'll pass empty list for now as main.py doesn't persist it.
    
    response = get_chat_response(user_message, [], db)
    return response.get("answer")


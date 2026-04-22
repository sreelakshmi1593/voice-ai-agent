import json
import os

# Simple file-based session memory (works without Redis)
SESSION_FILE = "sessions.json"

def load_sessions():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            return json.load(f)
    return {}

def save_sessions(sessions):
    with open(SESSION_FILE, "w") as f:
        json.dump(sessions, f)

def get_session(patient_id: str) -> dict:
    sessions = load_sessions()
    if patient_id not in sessions:
        sessions[patient_id] = {
            "conversation_history": [],
            "language": "english",
            "last_intent": None,
            "patient_name": None
        }
        save_sessions(sessions)
    return sessions[patient_id]

def update_session(patient_id: str, role: str, content: str, 
                   language: str = None, intent: str = None,
                   patient_name: str = None):
    sessions = load_sessions()
    if patient_id not in sessions:
        sessions[patient_id] = {
            "conversation_history": [],
            "language": "english",
            "last_intent": None,
            "patient_name": None
        }
    
    # Add to conversation history
    sessions[patient_id]["conversation_history"].append({
        "role": role,
        "content": content
    })
    
    # Keep only last 10 messages
    if len(sessions[patient_id]["conversation_history"]) > 10:
        sessions[patient_id]["conversation_history"] = \
            sessions[patient_id]["conversation_history"][-10:]
    
    # Update language preference
    if language:
        sessions[patient_id]["language"] = language
    
    # Update intent
    if intent:
        sessions[patient_id]["last_intent"] = intent

    # Update patient name
    if patient_name:
        sessions[patient_id]["patient_name"] = patient_name
    
    save_sessions(sessions)

def clear_session(patient_id: str):
    sessions = load_sessions()
    if patient_id in sessions:
        sessions[patient_id]["conversation_history"] = []
        sessions[patient_id]["last_intent"] = None
        save_sessions(sessions)
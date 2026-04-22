from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import json
import time
import os
import shutil
from dotenv import load_dotenv

# Import our modules
from database import Base, engine
from agent.reasoning.ai_agent import understand_intent, detect_language
from scheduler.appointment_engine.appointment_service import (
    book_appointment, cancel_appointment, 
    reschedule_appointment, get_available_slots,
    get_patient_appointments
)
from memory.session_memory.session_manager import (
    get_session, update_session, clear_session
)
from services.text_to_speech.tts_service import save_audio_only
from services.speech_to_text.stt_service import text_from_audio_file

load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Voice AI Agent - Clinical Appointment System")

# Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ─────────────────────────────────────────
# CORE AGENT LOGIC
# ─────────────────────────────────────────

def process_patient_request(user_text: str, patient_id: str) -> dict:
    """
    Main pipeline:
    Text → AI Agent → Tool → Response
    """
    total_start = time.time()

    # Get session memory
    session = get_session(patient_id)
    conversation_history = session["conversation_history"]
    
    # Step 1: Understand intent using AI
    agent_start = time.time()
    intent_data = understand_intent(user_text, conversation_history, patient_id)
    agent_latency = (time.time() - agent_start) * 1000

    intent = intent_data.get("intent", "unknown")
    language = intent_data.get("language", "english")
    response_text = intent_data.get("response", "")
    specialization = intent_data.get("specialization")
    date = intent_data.get("date")
    time_slot = intent_data.get("time")
    patient_name = intent_data.get("patient_name") or session.get("patient_name", "Patient")
    new_date = intent_data.get("new_date")
    new_time = intent_data.get("new_time")

    # Step 2: Execute tool based on intent
    tool_result = None

    if intent == "book" and specialization and date and time_slot:
        tool_result = book_appointment(
            patient_name=patient_name,
            patient_id=patient_id,
            specialization=specialization,
            date=date,
            time=time_slot,
            language=language
        )
        if tool_result["success"]:
            if language == "hindi":
                response_text = f"आपका अपॉइंटमेंट {tool_result['doctor']} के साथ {date} को {time_slot} बजे बुक हो गया है।"
            elif language == "tamil":
                response_text = f"உங்கள் சந்திப்பு {tool_result['doctor']} உடன் {date} அன்று {time_slot} மணிக்கு பதிவு செய்யப்பட்டது."
            else:
                response_text = f"Your appointment with {tool_result['doctor']} is confirmed for {date} at {time_slot}."
        else:
            # Get available slots
            available = get_available_slots(specialization, date)
            if available:
                slots_text = ", ".join(available[:3])
                if language == "hindi":
                    response_text = f"वह स्लॉट उपलब्ध नहीं है। उपलब्ध समय: {slots_text}"
                elif language == "tamil":
                    response_text = f"அந்த நேரம் கிடைக்கவில்லை. கிடைக்கும் நேரங்கள்: {slots_text}"
                else:
                    response_text = f"That slot is not available. Available slots are: {slots_text}"

    elif intent == "check_availability" and specialization and date:
        available = get_available_slots(specialization, date)
        if available:
            slots_text = ", ".join(available)
            if language == "hindi":
                response_text = f"{specialization} के लिए {date} को उपलब्ध समय: {slots_text}"
            elif language == "tamil":
                response_text = f"{specialization} க்கு {date} அன்று கிடைக்கும் நேரங்கள்: {slots_text}"
            else:
                response_text = f"Available slots for {specialization} on {date}: {slots_text}"
        else:
            if language == "hindi":
                response_text = f"माफ करें, {date} को कोई स्लॉट उपलब्ध नहीं है।"
            elif language == "tamil":
                response_text = f"மன்னிக்கவும், {date} அன்று இடங்கள் இல்லை."
            else:
                response_text = f"Sorry, no slots available on {date}."

    elif intent == "cancel" and date and time_slot:
        tool_result = cancel_appointment(patient_id, date, time_slot)
        if tool_result["success"]:
            if language == "hindi":
                response_text = "आपका अपॉइंटमेंट रद्द कर दिया गया है।"
            elif language == "tamil":
                response_text = "உங்கள் சந்திப்பு ரத்து செய்யப்பட்டது."
            else:
                response_text = "Your appointment has been cancelled successfully."

    elif intent == "reschedule" and date and time_slot and new_date and new_time:
        tool_result = reschedule_appointment(patient_id, date, time_slot, new_date, new_time)
        if tool_result["success"]:
            if language == "hindi":
                response_text = f"आपका अपॉइंटमेंट {new_date} को {new_time} बजे के लिए बदल दिया गया है।"
            elif language == "tamil":
                response_text = f"உங்கள் சந்திப்பு {new_date} அன்று {new_time} மணிக்கு மாற்றப்பட்டது."
            else:
                response_text = f"Your appointment has been rescheduled to {new_date} at {new_time}."

    # Step 3: Update session memory
    update_session(
        patient_id=patient_id,
        role="user",
        content=user_text,
        language=language,
        intent=intent,
        patient_name=patient_name
    )
    update_session(
        patient_id=patient_id,
        role="assistant",
        content=response_text
    )

    total_latency = (time.time() - total_start) * 1000

    # Log latency
    print(f"""
    ╔══════════════════════════════╗
    ║      LATENCY BREAKDOWN       ║
    ╠══════════════════════════════╣
    ║ Agent reasoning: {agent_latency:.0f} ms
    ║ Total latency:   {total_latency:.0f} ms
    ║ Target:          < 450 ms
    ║ Status: {'✅ PASS' if total_latency < 450 else '⚠️ SLOW'}
    ╚══════════════════════════════╝
    """)

    return {
        "response": response_text,
        "intent": intent,
        "language": language,
        "latency_ms": total_latency,
        "agent_latency_ms": agent_latency
    }

# ─────────────────────────────────────────
# REST API ENDPOINTS
# ─────────────────────────────────────────

@app.get("/")
def health_check():
    return {"status": "running", "message": "Voice AI Agent is active"}

@app.post("/chat")
def chat(data: dict):
    """Text-based chat endpoint"""
    user_text = data.get("message", "")
    patient_id = data.get("patient_id", "patient_001")
    
    result = process_patient_request(user_text, patient_id)
    return result

@app.post("/voice")
async def voice_endpoint(audio: UploadFile = File(...), 
                         patient_id: str = "patient_001"):
    """Voice upload endpoint"""
    # Save uploaded audio
    audio_path = f"temp_audio_{patient_id}.wav"
    with open(audio_path, "wb") as f:
        shutil.copyfileobj(audio.file, f)
    
    # Get session for language
    session = get_session(patient_id)
    language = session.get("language", "english")
    
    # STT
    stt_start = time.time()
    stt_result = text_from_audio_file(audio_path, language)
    stt_latency = (time.time() - stt_start) * 1000
    
    if not stt_result["success"]:
        return {"error": stt_result["error"]}
    
    user_text = stt_result["text"]
    
    # Process request
    result = process_patient_request(user_text, patient_id)
    result["recognized_text"] = user_text
    result["stt_latency_ms"] = stt_latency
    
    # Generate audio response
    tts_start = time.time()
    audio_response = save_audio_only(
        result["response"], 
        result["language"],
        f"response_{patient_id}.mp3"
    )
    tts_latency = (time.time() - tts_start) * 1000
    result["tts_latency_ms"] = tts_latency
    result["audio_response_file"] = audio_response
    
    # Cleanup
    if os.path.exists(audio_path):
        os.remove(audio_path)
    
    return result

@app.get("/appointments/{patient_id}")
def get_appointments(patient_id: str):
    """Get all appointments for a patient"""
    appointments = get_patient_appointments(patient_id)
    return {
        "patient_id": patient_id,
        "appointments": [
            {
                "id": a.id,
                "doctor": a.doctor_name,
                "specialization": a.specialization,
                "date": a.date,
                "time": a.time,
                "status": a.status,
                "language": a.language
            }
            for a in appointments
        ]
    }

@app.delete("/session/{patient_id}")
def reset_session(patient_id: str):
    """Clear session memory"""
    clear_session(patient_id)
    return {"message": "Session cleared"}

# ─────────────────────────────────────────
# WEBSOCKET FOR REAL-TIME COMMUNICATION
# ─────────────────────────────────────────

@app.websocket("/ws/{patient_id}")
async def websocket_endpoint(websocket: WebSocket, patient_id: str):
    await websocket.accept()
    print(f"✅ WebSocket connected: {patient_id}")
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message = json.loads(data)
            user_text = message.get("message", "")
            
            if not user_text:
                continue
            
            # Process request
            result = process_patient_request(user_text, patient_id)
            
            # Send response back
            await websocket.send_text(json.dumps({
                "response": result["response"],
                "intent": result["intent"],
                "language": result["language"],
                "latency_ms": result["latency_ms"]
            }))
            
    except WebSocketDisconnect:
        print(f"❌ WebSocket disconnected: {patient_id}")
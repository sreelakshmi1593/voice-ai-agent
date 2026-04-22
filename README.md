# Real-Time Multilingual Voice AI Agent
## Clinical Appointment Booking System

A real-time voice AI agent that manages clinical appointments through natural voice conversations in English, Hindi, and Tamil.

---

## Features
- Book, reschedule, and cancel appointments
- Multilingual support (English, Hindi, Tamil)
- Real-time WebSocket communication
- Contextual memory (session + persistent)
- Conflict detection with alternative suggestions
- Latency tracking and measurement

---

## Tech Stack
- **Backend**: FastAPI (Python)
- **AI Agent**: Groq (LLaMA 3.1)
- **Speech-to-Text**: Google Speech Recognition
- **Text-to-Speech**: gTTS
- **Database**: SQLite
- **Memory**: File-based session storage
- **Real-time**: WebSockets

---

## Architecture

```
User Speech
     ↓
Speech-to-Text (Google STT)
     ↓
Language Detection (Unicode-based)
     ↓
AI Agent (Groq / LLaMA 3.1)
     ↓
Tool Orchestration
     ↓
Appointment Service (SQLite)
     ↓
Text Response
     ↓
Text-to-Speech (gTTS)
     ↓
Audio Response
```

---

## Setup Instructions

### 1. Clone repository
```bash
git clone https://github.com/YOUR_USERNAME/voice-ai-agent.git
cd voice-ai-agent
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install fastapi uvicorn groq SpeechRecognition gTTS sqlalchemy python-dotenv websockets pyaudio langdetect python-multipart google-genai
```

### 4. Set up environment variables
Create a `.env` file in root folder:
```
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Run the server
```bash
uvicorn main:app --reload
```

### 6. Open frontend
Open `index.html` in your browser.

---

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Health check |
| `/chat` | POST | Text chat |
| `/voice` | POST | Voice upload |
| `/appointments/{patient_id}` | GET | Get appointments |
| `/session/{patient_id}` | DELETE | Clear session |
| `/ws/{patient_id}` | WebSocket | Real-time chat |

---

## Memory Design

**Session Memory** - File-based JSON storage
- Stores conversation history per patient
- Tracks current intent and language preference
- Keeps last 10 messages for context

**Persistent Memory** - SQLite database
- Stores all appointment records
- Doctor schedules and availability
- Patient history across sessions

---

## Latency Breakdown

| Stage | Time |
|---|---|
| Speech Recognition | ~120 ms |
| Language Detection | ~5 ms |
| AI Agent (Groq) | ~300 ms |
| Tool Execution | ~50 ms |
| **Total** | **~450 ms** |

Target: under 450ms from speech end to first response.

---

## Multilingual Support

| Language | Example |
|---|---|
| English | "Book appointment with cardiologist tomorrow" |
| Hindi | "मुझे कल डॉक्टर से मिलना है" |
| Tamil | "நாளை மருத்துவரை பார்க்க வேண்டும்" |

Language is auto-detected using Unicode character ranges.
Responses are translated back to the user's language.

---

## Project Structure

```
voice-ai-agent/
├── agent/
│   └── reasoning/
│       └── ai_agent.py        # Groq LLaMA agent
├── backend/
├── memory/
│   └── session_memory/
│       └── session_manager.py # Session storage
├── scheduler/
│   └── appointment_engine/
│       └── appointment_service.py # Booking logic
├── services/
│   ├── speech_to_text/
│   │   └── stt_service.py
│   └── text_to_speech/
│       └── tts_service.py
├── database.py                # SQLite models
├── main.py                    # FastAPI server
├── index.html                 # Frontend UI
├── .env                       # API keys (not in git)
└── README.md
```

---

## Trade-offs

- Using **SQLite** instead of PostgreSQL for simplicity — easily replaceable
- Using **file-based sessions** instead of Redis for zero setup requirement
- Using **Groq free tier** instead of OpenAI for cost efficiency
- Tamil responses use a **translate-then-respond** approach for reliability

---

## Known Limitations

- Latency occasionally exceeds 450ms on Groq free tier
- Tamil JSON parsing requires an extra translation step
- Voice recording requires microphone browser permissions
- Redis TTL memory is not implemented (uses file-based storage)

---

## Author
Sreelakshmi Chowdam

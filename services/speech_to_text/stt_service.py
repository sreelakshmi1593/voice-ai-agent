import speech_recognition as sr
import time

recognizer = sr.Recognizer()

def speech_to_text(language: str = "english") -> dict:
    """
    Captures voice from microphone and converts to text
    """
    # Language codes for recognition
    lang_codes = {
        "english": "en-IN",
        "hindi": "hi-IN",
        "tamil": "ta-IN"
    }
    
    lang_code = lang_codes.get(language, "en-IN")
    
    start_time = time.time()
    
    with sr.Microphone() as source:
        print(f"🎤 Listening... (speak in {language})")
        
        # Adjust for ambient noise
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        try:
            # Listen for speech
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
            print("🔄 Processing speech...")
            
            # Convert to text
            text = recognizer.recognize_google(audio, language=lang_code)
            
            end_time = time.time()
            stt_latency = (end_time - start_time) * 1000
            
            print(f"✅ Recognized: {text}")
            print(f"⏱️ STT Latency: {stt_latency:.2f} ms")
            
            return {
                "success": True,
                "text": text,
                "latency_ms": stt_latency
            }
            
        except sr.WaitTimeoutError:
            return {
                "success": False,
                "text": "",
                "error": "No speech detected. Please try again."
            }
        except sr.UnknownValueError:
            return {
                "success": False,
                "text": "",
                "error": "Could not understand audio. Please speak clearly."
            }
        except Exception as e:
            return {
                "success": False,
                "text": "",
                "error": str(e)
            }

def text_from_audio_file(audio_file_path: str, language: str = "english") -> dict:
    """
    Converts audio file to text (for API uploads)
    """
    lang_codes = {
        "english": "en-IN",
        "hindi": "hi-IN",
        "tamil": "ta-IN"
    }
    
    lang_code = lang_codes.get(language, "en-IN")
    start_time = time.time()
    
    with sr.AudioFile(audio_file_path) as source:
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio, language=lang_code)
            end_time = time.time()
            latency = (end_time - start_time) * 1000
            return {
                "success": True,
                "text": text,
                "latency_ms": latency
            }
        except Exception as e:
            return {
                "success": False,
                "text": "",
                "error": str(e)
            }
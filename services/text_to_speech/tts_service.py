from gtts import gTTS
import os
import time
import platform

def text_to_speech(text: str, language: str = "english") -> dict:
    """
    Converts text response to audio and plays it
    """
    lang_codes = {
        "english": "en",
        "hindi": "hi",
        "tamil": "ta"
    }
    
    lang_code = lang_codes.get(language, "en")
    start_time = time.time()
    
    try:
        # Generate speech
        tts = gTTS(text=text, lang=lang_code, slow=False)
        
        # Save audio file
        audio_file = "response.mp3"
        tts.save(audio_file)
        
        end_time = time.time()
        tts_latency = (end_time - start_time) * 1000
        
        print(f"⏱️ TTS Latency: {tts_latency:.2f} ms")
        
        # Play audio
        play_audio(audio_file)
        
        return {
            "success": True,
            "audio_file": audio_file,
            "latency_ms": tts_latency
        }
        
    except Exception as e:
        print(f"TTS Error: {e}")
        # Fallback - just print the text
        print(f"🔊 Agent says: {text}")
        return {
            "success": False,
            "error": str(e)
        }

def play_audio(audio_file: str):
    """
    Plays audio file on Windows/Mac/Linux
    """
    try:
        system = platform.system()
        if system == "Windows":
            os.system(f"start {audio_file}")
        elif system == "Darwin":  # Mac
            os.system(f"afplay {audio_file}")
        else:  # Linux
            os.system(f"mpg123 {audio_file}")
    except Exception as e:
        print(f"Could not play audio: {e}")

def save_audio_only(text: str, language: str = "english", 
                    filename: str = "response.mp3") -> str:
    """
    Saves audio file without playing (for API responses)
    """
    lang_codes = {
        "english": "en",
        "hindi": "hi",
        "tamil": "ta"
    }
    lang_code = lang_codes.get(language, "en")
    
    tts = gTTS(text=text, lang=lang_code, slow=False)
    tts.save(filename)
    return filename
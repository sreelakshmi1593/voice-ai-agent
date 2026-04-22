from groq import Groq
import json
import os
import datetime
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def detect_language(text: str) -> str:
    for char in text:
        if '\u0B80' <= char <= '\u0BFF':
            return "tamil"
    for char in text:
        if '\u0900' <= char <= '\u097F':
            return "hindi"
    return "english"

def translate_to_english(text: str) -> str:
    try:
        r = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": f"Translate to English (only translation, no explanation): {text}"}],
            temperature=0.1
        )
        return r.choices[0].message.content.strip()
    except:
        return text

def get_response_in_language(english_response: str, language: str) -> str:
    if language == "english":
        return english_response
    try:
        lang_name = "Tamil" if language == "tamil" else "Hindi"
        r = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": f"Translate to {lang_name} (only translation): {english_response}"}],
            temperature=0.1
        )
        return r.choices[0].message.content.strip()
    except:
        return english_response

def understand_intent(user_text: str, conversation_history: list, patient_id: str) -> dict:

    language = detect_language(user_text)

    today = datetime.datetime.now().strftime('%Y-%m-%d')
    tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

    if language != "english":
        english_text = translate_to_english(user_text)
        print(f"Translated: {english_text}")
    else:
        english_text = user_text

    prompt = f"""Extract intent from this message: "{english_text}"

Today: {today}, Tomorrow: {tomorrow}

Return ONLY this JSON:
{{"intent": "INTENT", "specialization": null, "date": null, "time": null, "new_date": null, "new_time": null, "patient_name": null, "response": "RESPONSE"}}

Rules:
- message has "cancel" → intent = "cancel", extract date and time
- message has "reschedule" or "change" or "move" → intent = "reschedule", old date/time to date/time, new date/time to new_date/new_time
- message has "book" or "see doctor" or "appointment" → intent = "book"
- message has "hello" or "hi" → intent = "greeting", response = "Hello! I can help you book, cancel or reschedule appointments. How can I help you today?"
- message has "available" or "slots" or "check" → intent = "check_availability"
- specialization options: cardiologist, dermatologist, general, orthopedic, pediatrician
- if "tomorrow" in message → date = {tomorrow}
- if "today" in message → date = {today}
- time format: "09:00 AM" or "10:00 AM" etc
- for book intent without time: response = "What time works for you? Available slots: 09:00 AM, 10:00 AM, 11:00 AM, 02:00 PM, 03:00 PM, 04:00 PM"
- Use ENGLISH ONLY in all fields
- Return ONLY the JSON"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "Return only valid JSON with English text. No markdown. No backticks. No explanation."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1
        )

        response_text = response.choices[0].message.content.strip()
        print(f"Raw AI: {response_text[:300]}")

        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        start = response_text.find("{")
        end = response_text.rfind("}") + 1
        if start != -1 and end != 0:
            response_text = response_text[start:end]

        parsed = json.loads(response_text)
        parsed["language"] = language

        if language != "english" and "response" in parsed:
            parsed["response"] = get_response_in_language(parsed["response"], language)

        return parsed

    except Exception as e:
        print(f"AI Agent Error: {e}")

        if language == "tamil":
            fallback = "மன்னிக்கவும், மீண்டும் சொல்லுங்கள்."
        elif language == "hindi":
            fallback = "माफ करें, क्या आप दोबारा बोल सकते हैं?"
        else:
            fallback = "I'm sorry, could you please repeat that?"

        return {
            "intent": "unknown",
            "language": language,
            "response": fallback,
            "specialization": None,
            "date": None,
            "time": None
        }
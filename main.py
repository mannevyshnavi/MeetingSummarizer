# main.py
from fastapi import FastAPI, UploadFile, File
from motor.motor_asyncio import AsyncIOMotorClient
from faster_whisper import WhisperModel
import ollama
import json
import asyncio
import os

app = FastAPI()

## ---------------------
## Configuration & Setup
## ---------------------

# --- Database Connection ---
MONGO_DETAILS = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_DETAILS)
database = client.meetings
collection = database.get_collection("summaries")

# --- Model Loading ---
# Load models once at startup to save time on each request.
# "base" is small and fast. For higher accuracy, consider "medium" or "large-v3".
print("[SETUP] Loading faster-whisper model...")
asr_model = WhisperModel("base", device="cpu", compute_type="int8")
print("[SETUP] Models loaded successfully.")


## ---------------------
## Helper Functions
## ---------------------

async def save_audio_file(file: UploadFile):
    """Saves uploaded file temporarily to the 'temp_audio' directory."""
    # Ensure the temp directory exists
    os.makedirs("temp_audio", exist_ok=True)
    
    temp_file_path = f"temp_audio/temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        buffer.write(await file.read())
    return temp_file_path

def get_structured_summary(transcript: str) -> dict:
    """Calls Ollama to get a structured JSON summary from a transcript."""
    prompt = f"""
    You are an expert meeting assistant AI. Your task is to analyze the following meeting transcript and produce a JSON object with three keys: "summary", "key_decisions", and "action_items".

    - "summary": A concise paragraph summarizing the meeting's main topics and outcomes.
    - "key_decisions": A list of the most important decisions made.
    - "action_items": A list where each item is an object with "task", "owner", and "deadline". Default to "Unassigned" or "Not specified" if not mentioned.

    Based ONLY on the provided transcript.

    Transcript:
    \"\"\"
    {transcript}
    \"\"\"

    JSON Output:
    """
    
    response = ollama.chat(
        model='tinyllama',  # You can switch this to 'mistral' for potentially faster (but different) results
        format='json',
        messages=[{'role': 'user', 'content': prompt}]
    )
    return json.loads(response['message']['content'])


## ---------------------
## API Endpoint
## ---------------------

@app.post("/process/")
async def process_meeting_audio(file: UploadFile = File(...)):
    # 1. Save the audio file temporarily
    audio_path = await save_audio_file(file)
    print(f"[STATUS] Audio file saved to: {audio_path}")

    # 2. Transcribe using faster-whisper
    print("[STATUS] Transcribing audio with faster-whisper... This may take a while.")
    segments, _ = asr_model.transcribe(audio_path, beam_size=5)
    full_transcript = " ".join([segment.text.strip() for segment in segments])
    print("[STATUS] Transcription complete!")

    # 3. Get structured summary from Ollama
    print("[STATUS] Summarizing transcript with Ollama... This is the slowest step.")
    structured_data = get_structured_summary(full_transcript)
    print("[STATUS] Summarization complete!")

    # 4. Prepare data for database
    db_entry = {
        "filename": file.filename,
        "transcript": full_transcript,
        "summary": structured_data.get("summary"),
        "decisions": structured_data.get("key_decisions"),
        "actions": structured_data.get("action_items"),
    }

    # 5. Save to MongoDB
    await collection.insert_one(db_entry)
    print("[STATUS] Results saved to database.")
    
    # 6. Clean up temp file
    os.remove(audio_path)
    print(f"[STATUS] Temporary file {audio_path} removed.")

    return {"id": str(db_entry["_id"]), **db_entry}
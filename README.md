# 🎙️ Meeting Summarizer AI

This project provides an end-to-end solution for transcribing audio from meetings and generating structured, actionable summaries using locally-run AI models. It addresses the common problem of valuable information being lost after a meeting by creating a permanent, searchable, and summarized record.

The entire pipeline runs on your local machine, ensuring data privacy and eliminating reliance on paid cloud APIs.

---

## 🌟 Key Features

* **Audio Upload**: Simple web interface to upload meeting recordings (MP3, WAV, M4A).
* **Accurate Transcription**: Utilizes the highly optimized `faster-whisper` for precise speech-to-text conversion.
* **AI-Powered Summarization**: Employs a local LLM via Ollama to generate structured output, including:
    * A concise **summary** of the meeting.
    * A bulleted list of **key decisions**.
    * A table of **action items** with assigned owners and deadlines.
* **Privacy-Focused**: All processing, from transcription to summarization, happens on your machine. Your data never leaves your control.
* **Persistent Storage**: All results are saved to a MongoDB database for future reference.

---

## 🛠️ Tech Stack & Architecture

This project uses a modern, decoupled architecture with a Python backend and a Streamlit frontend.

* **Frontend**: **Streamlit** - For a simple, interactive user interface.
* **Backend**: **FastAPI** - A high-performance Python framework for building the API.
* **Transcription (ASR)**: **`faster-whisper`** - A highly optimized implementation of OpenAI's Whisper model for fast and accurate local transcription.
* **Language Model (LLM)**: **Ollama** - To serve open-source models like `Llama 3`, `Mistral`, or `TinyLlama` locally.
* **Database**: **MongoDB** - A flexible NoSQL database to store meeting transcripts and summaries.

### How It Works

The application follows a simple data flow:

1.  A user uploads an audio file via the **Streamlit** interface.
2.  Streamlit sends the file to the **FastAPI** backend.
3.  The backend uses **`faster-whisper`** to transcribe the audio into text.
4.  The complete transcript is sent to a locally-running **Ollama** LLM with a structured prompt.
5.  The LLM returns a JSON object containing the summary, decisions, and action items.
6.  The backend saves all this information to **MongoDB**.
7.  The final result is sent back to the Streamlit frontend for the user to view.

---

## ⚙️ Local Setup and Installation

Follow these steps to get the project running on your local machine.

### Prerequisites

* **Python 3.10+**
* **Ollama**: Download and install from [ollama.com](https://ollama.com).
* **MongoDB Community Server**: Download and install from the [official MongoDB website](https://www.mongodb.com/try/download/community).

### 1. Clone the Repository

```bash
git clone [https://github.com/your-username/MeetingSummarizer.git](https://github.com/your-username/MeetingSummarizer.git)
cd MeetingSummarizer
## Set Up the Python Virtual Environment
  # Create a virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Activate it (macOS/Linux)
source venv/bin/activate

3.Install Dependencies
pip install -r requirements.txt

4.Download an Ollama LLM
You need at least one model for summarization. tinyllama is recommended for initial testing due to its speed.
# Recommended for first-time use (fastest)
ollama pull tinyllama

# For higher quality (slower)
ollama pull mistral
ollama pull llama3


▶️ Running the Application
This application requires three separate processes to run concurrently in three different terminals. Ensure the main Ollama service is also running in the background.

Terminal 1: Start the MongoDB Server
mongod

Terminal 2: Start the FastAPI Backend
# Make sure your venv is active
uvicorn main:app --reload

Terminal 3: Start the Streamlit Frontend
# Make sure your venv is active
streamlit run app.py
After running the last command, a new tab should open in your browser at http://localhost:8501.

🔧 Configuration
Changing the LLM Model
The LLM used for summarization can be easily changed.

1.Open the main.py file.

2.Navigate to the get_structured_summary function.

3.Modify the model parameter in the ollama.chat() call
response = ollama.chat(
    model='tinyllama',  # Change this to 'mistral', 'llama3', etc.
    format='json',
    messages=[{'role': 'user', 'content': prompt}]
)
4.Save the file. The FastAPI server will automatically reload with the new model.

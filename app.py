# app.py
import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide")
st.title("🎙️ Meeting Summarizer")

# FastAPI endpoint URL
BACKEND_URL = "http://127.0.0.1:8000/process/"

uploaded_file = st.file_uploader(
    "Upload your meeting audio (MP3, WAV, M4A)...", 
    type=["mp3", "wav", "m4a"]
)

if uploaded_file is not None:
    st.audio(uploaded_file, format='audio/wav')
    
    with st.spinner("Processing your meeting... This may take a moment."):
        files = {'file': (uploaded_file.name, uploaded_file, uploaded_file.type)}
        try:
            response = requests.post(BACKEND_URL, files=files, timeout=1800)
            
            if response.status_code == 200:
                st.success("Processing complete!")
                data = response.json()

                # Display the results
                st.subheader("📝 Summary")
                st.write(data.get("summary", "No summary available."))

                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("🎯 Key Decisions")
                    st.json(data.get("decisions", []))

                with col2:
                    st.subheader("✅ Action Items")
                    actions = data.get("actions", [])
                    if actions:
                        df = pd.DataFrame(actions)
                        st.dataframe(df)
                    else:
                        st.write("No action items identified.")

                with st.expander("Full Transcript"):
                    st.write(data.get("transcript", "Transcript not available."))

            else:
                st.error(f"Error processing file: {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Could not connect to the backend. Please ensure it's running. Details: {e}")
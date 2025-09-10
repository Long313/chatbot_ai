# Voice-enabled Streamlit UI

This app adds **microphone recording** and **speech-to-text** to your chatbot UI.

## Install
```bash
python -m venv .env
# Windows PowerShell
.env\Scripts\Activate.ps1
pip install -r requirements_voice.txt
```

> The app uses:
> - `streamlit-audiorecorder` for recording from the **browser mic**
> - `SpeechRecognition` (Google Web Speech) to transcribe the recorded audio to text (vi-VN)
> - `openai==0.28.0` legacy client to talk to Groq's OpenAI-compatible endpoint (same as your existing code)

## Run
```bash
streamlit run app_voice.py
```
Open `http://localhost:8501`, click the **microphone** area to start/stop recording, and the app will transcribe and send the message.

## Notes
- The first time, your browser will ask for **microphone permission**; please allow it.
- For privacy, keep API keys out of source code.
- If you prefer a different STT service (e.g., Whisper), you can replace the transcription block in `app_voice.py`.

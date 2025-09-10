import io, wave
from datetime import datetime
import streamlit as st
import speech_recognition as sr
from audiorecorder import audiorecorder
from chat_core import configure_gemini, reply, DEFAULT_MODEL

st.set_page_config(page_title="AMAX - Chatbot🎙️", page_icon="💬", layout="wide")

GRADIENT = "linear-gradient(135deg, #822FFF, #FF35C4)"

# ---- CSS giữ nguyên ----
CUSTOM_CSS = f"""<style>
.stApp {{ background: #ffffff; color: #111827; }}
.chat-bubble {{ border-radius:14px; padding:10px 14px; margin:8px 0; max-width:85%; font-size:15px; border:1px solid #e5e7eb; background:#fff; }}
.user-bubble {{ margin-left:auto; background:#fafafa; }}
.assistant-bubble {{ margin-right:auto; background:#f8fafc; }}
.timestamp {{ font-size:12px; color:#6b7280; }}
.stButton > button {{ background:{GRADIENT}; color:white; border:none; border-radius:10px; padding:8px 14px; }}
.stButton > button:hover {{ filter: brightness(0.95); }}
input[type="text"], input[type="password"], textarea {{
  border:2px solid transparent !important; border-radius:7px !important;
  background-image: linear-gradient(#fff,#fff), {GRADIENT};
  background-origin:border-box; background-clip: padding-box, border-box;
}}
[data-testid="stChatInput"] textarea {{
  border:2px solid transparent !important; border-radius:7px !important;
  background-image: linear-gradient(#fff,#fff), {GRADIENT};
  background-origin:border-box; background-clip: padding-box, border-box;
}}
[data-testid="stSidebar"] {{ background:#FFF3FC; }}
.stAudio audio {{ width:100%; outline:none; }}
</style>"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---- Sidebar ----
with st.sidebar:
    st.header("⚙️ Cấu hình")
    gemini_key = st.text_input("Gemini API Key", type="password", help="Dán key từ Google AI Studio")
    model = st.text_input("Model", value=DEFAULT_MODEL)
    auto_send = st.checkbox("Tự gửi sau khi nhận dạng giọng nói", value=True)
    if st.button("🧹 Xoá hội thoại"):
        st.session_state.messages = []

# ---- Phiên chat ----
if "messages" not in st.session_state:
    st.session_state.messages = []

def render_message(role, content, t=None):
    t = t or datetime.now().strftime("%H:%M")
    bubble_class = "user-bubble" if role=="user" else "assistant-bubble"
    who = "🧑" if role=="user" else "🤖"
    st.markdown(f"""
    <div class="chat-bubble {bubble_class}">
        <div><b>{who}</b> · <span class="timestamp">{t}</span></div>
        <div>{content}</div>
    </div>""", unsafe_allow_html=True)

# ---- Hiển thị lịch sử chat ----
for m in st.session_state.messages:
    render_message(m["role"], m["content"], m.get("t"))

# ---- Khu nhập liệu ----
col_text, col_voice = st.columns([2,1])
with col_text:
    user_text = st.chat_input("Nhập tin nhắn…")

with col_voice:
    audio = audiorecorder("Bấm để nói 🎤", "Bấm để dừng ✔️")
    transcript = None
    if len(audio) > 0:
        wav_bytes = io.BytesIO()
        with wave.open(wav_bytes, "wb") as wf:
            wf.setnchannels(audio.channels)
            wf.setsampwidth(audio.sample_width)
            wf.setframerate(audio.frame_rate)
            wf.writeframes(audio.raw_data)
        wav_bytes.seek(0)
        st.audio(wav_bytes.getvalue(), format="audio/wav")

        r = sr.Recognizer()
        try:
            with sr.AudioFile(wav_bytes) as source:
                data = r.record(source)
            transcript = r.recognize_google(data, language="vi-VN")
            st.success(f"📝 Nhận dạng: {transcript}")
        except sr.UnknownValueError:
            st.warning("Chưa nghe rõ nội dung.")
        except sr.RequestError as e:
            st.error(f"Lỗi dịch vụ nhận dạng: {e}")

# ---- Gửi câu hỏi ----
to_send = user_text or transcript
if to_send:
    st.session_state.messages.append({"role":"user","content":to_send,"t":datetime.now().strftime("%H:%M")})
    render_message("user", to_send)
    try:
        configure_gemini(api_key=gemini_key)
        bot_text = reply(to_send)
    except Exception as e:
        bot_text = f"⚠️ Lỗi API: {e}"
    st.session_state.messages.append({"role":"assistant","content":bot_text,"t":datetime.now().strftime("%H:%M")})
    render_message("assistant", bot_text)

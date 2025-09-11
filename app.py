import io, wave
import webbrowser
import requests
import urllib.parse
from bs4 import BeautifulSoup
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
# Map tên trang sang URL
def extract_youtube_song(command: str) -> str | None:
    cmd = command.lower()
    if "bài hát" in cmd and "youtube" in cmd:
        # lấy phần sau "bài hát"
        query = command.split("bài hát", 1)[1]
        # loại bỏ mấy từ thừa
        query = query.replace("trên trang youtube.com", "")
        query = query.replace("trang youtube.com", "")
        query = query.replace("trên youtube.com", "")
        query = query.replace("youtube.com", "")
        return query.strip()
    return None

def play_first_youtube_result(query: str, api_key: str = None):
    if not api_key:
        api_key = "AIzaSyD6rtMXwUWS2iZAbWYi6aaF72NSivPKyDU"  # key mặc định
    search_url = (
        "https://www.googleapis.com/youtube/v3/search?"
        f"part=snippet&type=video&maxResults=1&q={urllib.parse.quote(query)}&key={api_key}"
    )
    resp = requests.get(search_url).json()
    items = resp.get("items", [])
    if not items:
        return "⚠️ Không tìm thấy video nào."
    video_id = items[0]["id"]["videoId"]
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    webbrowser.open(video_url, new=2)
    return f"🎵 Đang phát: {query}\n👉 {video_url}"

def open_site(command: str):
    cmd = command.lower()

    # --- Nếu có 'youtube' + 'tìm kiếm' ---
    if "youtube" in cmd and "tìm kiếm" in cmd:
        try:
            query = command.split("tìm kiếm", 1)[1].strip()
            if query:
                search_url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(query)
                webbrowser.open(search_url, new=2)
                return f"🎵 Đang mở YouTube và tìm kiếm: {query}"
        except:
            pass
        return "⚠️ Không nhận diện được từ khóa tìm kiếm trên YouTube."

    # --- Nếu có 'youtube' + 'bài hát' ---
    if "youtube" in cmd and "bài hát" in cmd:
        query = extract_youtube_song(command)
        if query:
            return play_first_youtube_result(query)
        else:
            return "⚠️ Không nhận diện được tên bài hát."

    # --- Map trang phổ biến ---
    SITE_MAP = {
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "facebook": "https://www.facebook.com",
        "zalo": "https://chat.zalo.me",
        "github": "https://github.com"
    }

    for name, url in SITE_MAP.items():
        if name in cmd:
            webbrowser.open(url, new=2)
            return f"🌐 Đang mở {name.title()}..."

    # fallback: tìm trên Google
    search_url = "https://www.google.com/search?q=" + urllib.parse.quote(command)
    webbrowser.open(search_url, new=2)
    return f"🔍 Không rõ trang, đang tìm '{command}' trên Google..."

# ---- Sidebar ----
with st.sidebar:
    st.header("⚙️ Cấu hình")
    gemini_key = st.text_input("API Key", type="password", help="Dán key từ Google AI Studio")
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

to_send = user_text or transcript
if to_send:
    # ✅ Kiểm tra lệnh mở trang
    if to_send.lower().startswith("mở "):
        site_name = to_send[3:].strip()  # lấy phần sau từ "mở"
        msg = open_site(site_name)
        st.success(msg)
    else:
        # Chat bình thường
        st.session_state.messages.append({"role":"user","content":to_send,"t":datetime.now().strftime("%H:%M")})
        render_message("user", to_send)
        try:
            configure_gemini(api_key=gemini_key)
            bot_text = reply(to_send)
        except Exception as e:
            bot_text = f"⚠️ Lỗi API: {e}"
        st.session_state.messages.append({"role":"assistant","content":bot_text,"t":datetime.now().strftime("%H:%M")})
        render_message("assistant", bot_text)

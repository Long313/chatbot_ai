"""
Core chat utilities for Gemini API + Tavily Web Search (cập nhật thông tin mới nhất)
"""

import os
import google.generativeai as genai
import requests
from langdetect import detect

DEFAULT_MODEL = "gemini-1.5-flash"

# ---- Hardcode Tavily key (web search) ----
TAVILY_KEY = "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"

def configure_gemini(api_key: str | None = None):
    """
    Configure the Gemini client.
    api_key: Gemini API key. Nếu None, đọc từ biến môi trường GEMINI_API_KEY.
    """
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY not set. Nhập key từ param hoặc biến môi trường.")
    genai.configure(api_key=key)

def search_web(query: str, max_results: int = 3) -> str:
    """
    Dùng Tavily để lấy thông tin mới nhất từ web.
    """
    if not TAVILY_KEY:
        return "⚠️ Chưa có TAVILY_API_KEY"
    
    resp = requests.post(
        "https://api.tavily.com/search",
        json={"query": query, "max_results": max_results},
        headers={"Authorization": f"Bearer {TAVILY_KEY}"}
    )
    if resp.status_code != 200:
        return f"⚠️ Lỗi Tavily API: {resp.text}"
    
    results = resp.json()
    return "\n".join([r.get("content","") for r in results.get("results", [])])

def ask_gemini(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """
    Nếu câu hỏi có từ khóa thời sự hoặc là tiếng Anh, tự động gọi web search để cập nhật thông tin.
    """
    try:
        lang = detect(prompt)
    except:
        lang = "vi"
    
    keywords_vi = ["hiện tại", "nay", "mới nhất", "tổng thống", "ngày hôm nay", "giá", "thời tiết", "báo cáo"]
    use_web = lang == "en" or any(word in prompt.lower() for word in keywords_vi)

    if use_web:
        web_data = search_web(prompt)
        prompt = f"Người dùng hỏi: {prompt}\nThông tin mới nhất từ web:\n{web_data}\nHãy trả lời chính xác bằng ngôn ngữ câu hỏi."

    model_obj = genai.GenerativeModel(model)
    response = model_obj.generate_content(prompt)
    return response.text

def reply(user_text: str) -> str:
    """
    Trả lời từ Gemini, fallback nếu trống.
    """
    if not user_text or not user_text.strip():
        return "Mình chưa nghe rõ. Bạn nhập lại giúp mình nhé."
    return ask_gemini(user_text)

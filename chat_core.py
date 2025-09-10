"""
Core chat utilities that can be reused by both CLI and UI apps.
Reads GROQ API key from environment or from a passed-in value.
"""

import os
from datetime import date, datetime

import openai  # openai==0.28 (legacy)

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
DEFAULT_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"


def configure_openai(api_key: str | None = None, api_base: str | None = GROQ_BASE_URL):
    """
    Configure the OpenAI client to use Groq's OpenAI-compatible endpoint.
    api_key: Groq API key (starts with gsk_). If None, read from environment variable GROQ_API_KEY.
    api_base: Base URL. Defaults to Groq's OpenAI-compatible endpoint.
    """
    key = api_key or os.getenv("GROQ_API_KEY")
    if not key:
        raise ValueError("GROQ_API_KEY not set. Provide it via function param or environment variable.")
    openai.api_key = key
    if api_base:
        openai.api_base = api_base


def ask_groq(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """
    Send a single-turn prompt to the Groq model and return the response text.
    """
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message["content"]


def reply(user_text: str) -> str:
    """
    Very simple rule-based layer for quick responses.
    Falls back to Groq model for everything else.
    """
    if not user_text or not user_text.strip():
        return "Mình chưa nghe rõ. Bạn nhập lại giúp mình nhé."

    lower = user_text.lower().strip()

    if "hello" in lower or "hi" in lower or "xin chào" in lower:
        return "Hello! 👋 Mình có thể giúp gì cho bạn?"
    if "today" in lower or "hôm nay" in lower:
        today = date.today()
        return today.strftime("Hôm nay là %d/%m/%Y.")
    if "time" in lower or "mấy giờ" in lower or "giờ" == lower:
        now = datetime.now()
        return now.strftime("Bây giờ là %H:%M.")

    # Default: ask the model
    return ask_groq(user_text)

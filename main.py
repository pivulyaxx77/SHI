import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# Завантаження правил
@st.cache_data(ttl=600)
def load_rules():
    r = requests.get("https://ukrainerpeh.xyz/#rules")
    soup = BeautifulSoup(r.text, "html.parser")
    return " ".join(soup.get_text(separator=" ").split())

rules_cache = load_rules()

st.title("RP Rules AI Bot")

question = st.text_input("Напиши питання про правила:")

if question:
    prompt = f"""
Ти — ШІ помічник сервера UKRAINE RP Emergency Hamburg.

Правила:
- Відповідаєш ТІЛЬКИ на питання про RP або правила сервера
- Використовуєш лише інформацію з правил
- Якщо питання не по темі — відповідай:
"Я не знаю відповіді, бо відповідаю лише на питання по правилах сервера UKRAINE RP."

Текст правил:
{rules_cache}

Питання гравця:
{question}
"""
    try:
        response = model.generate_content(prompt)
        st.write(response.text)
    except Exception as e:
        st.error(f"Помилка Gemini API: {e}")

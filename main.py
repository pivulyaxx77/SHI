import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# 1. Налаштування сторінки
st.set_page_config(page_title="UKRAINE RP Assistant", page_icon="🇺🇦")

st.markdown("<h1 style='text-align: center; color: #0057b7;'>🤖 Помічник UKRAINE RP</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #ffd700;'>Emergency Hamburg</h3>", unsafe_allow_html=True)

# 2. Функція збору правил (з обробкою помилок)
@st.cache_data(ttl=600)
def get_rules():
    url = "https://ukrainerpeh.xyz/#rules"
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text(separator=' ', strip=True)
        return text if len(text) > 100 else "Правила не знайдено на сторінці."
    except Exception as e:
        return f"Помилка завантаження: {e}"

# 3. Перевірка та налаштування API
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("❌ Додайте GOOGLE_API_KEY у Secrets!")
    st.stop()

try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Помилка ШІ: {e}")
    st.stop()

# 4. Робота з чатом
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Запитайте про правила сервера..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Звіряюся з базою знань..."):
            rules_context = get_rules()
            
            # Формуємо чітку інструкцію без складних лапок
            instruction = (
                f"Ти помічник сервера 'UKRAINE RP' у Emergency Hamburg. "
                f"Ось актуальні правила: {rules_context[:6000]}. "
                f"Відповіда

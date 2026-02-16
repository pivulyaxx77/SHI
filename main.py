import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# 1. Налаштування сторінки
st.set_page_config(page_title="UKRAINE RP Assistant", page_icon="🇺🇦")

# Стилізація заголовка
st.markdown("<h1 style='text-align: center; color: #0057b7;'>🤖 Помічник UKRAINE RP</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #ffd700;'>Emergency Hamburg</h3>", unsafe_allow_html=True)

# 2. Функція збору правил з сайту
@st.cache_data(ttl=600)  # Оновлювати правила раз на 10 хвилин
def get_rules():
    url = "https://ukrainerpeh.xyz/#rules"
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        # Видаляємо скрипти та непотрібні теги
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text(separator=' ', strip=True)
        return text
    except Exception as e:
        return f"Помилка завантаження правил: {e}"

# 3. Перевірка API ключа в Secrets
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("❌ Помилка: Не знайдено API ключ у налаштуваннях Secrets!")
    st.info("Будь ласка, додайте GOOGLE_API_KEY у вкладці Secrets вашого Streamlit Cloud.")
    st.stop()

# Налаштування моделі
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"❌ Помилка конфігурації ШІ: {e}")
    st.stop()

# 4. Логіка чату
if "messages" not in st.session_state:
    st.session_state.messages = []

# Відображення історії
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Поле вводу користувача
if prompt := st.chat_input("Напишіть ваше запитання про правила..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Звіряюся з правилами..."):
            rules_context = get_rules()
            
            system_instruction = f"""
            Ти — офіційний ШІ-помічник сервера 'UKRAINE RP' у грі Emergency Hamburg. 
            Твоє завдання — допомагати гравцям розуміти правила.
            
            Ось текст правил з нашого сайту: {rules_context[:8000]}

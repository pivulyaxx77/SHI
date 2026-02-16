import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# 1. Налаштування сторінки
st.set_page_config(page_title="UKRAINE RP Assistant", page_icon="🇺🇦")
st.title("🤖 Помічник UKRAINE RP")

# 2. Функція збору правил
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
        return text[:8000] if len(text) > 100 else "Правила не завантажились."
    except:
        return "Не вдалося отримати правила з сайту."

# 3. Налаштування API
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Додайте GOOGLE_API_KEY у Secrets!")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 4. Чат
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Запитайте про правила..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Звіряюся з правилами..."):
            rules_data = get_rules()
            # ОДИН суцільний рядок для інструкції (це прибере SyntaxError)
            instruction = f"Ти помічник сервера 'UKRAINE RP'. Правила: {rules_data}. Відповідай тільки про правила або RP. Якщо питання про інше, кажи: 'Я не знаю відповіді, так як я відповідаю на питання, лише пов'язані з правилами Сервера UKRAINE RP в Emergency Hamburg'."
            
            try:
                response = model.generate_content(f"{instruction}\n\nКористувач: {prompt}")
                answer = response.text if response else "Помилка відповіді."
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"Помилка: {e}")

with st.sidebar:
    if st.button("Оновити правила"):
        st.cache_data.clear()
        st.rerun()

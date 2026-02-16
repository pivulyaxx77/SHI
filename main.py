import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# Налаштування сторінки
st.set_page_config(page_title="UKRAINE RP Assistant", page_icon="🇺🇦")
st.title("🤖 Помічник UKRAINE RP")

# 1. Отримання правил з сайту
def get_rules_from_site():
    url = "https://ukrainerpeh.xyz/#rules"
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text(separator=' ', strip=True)
    except:
        return "Не вдалося завантажити правила."

# 2. Налаштування Gemini (використовуємо ваш ключ із Secrets)
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

current_rules = get_rules_from_site()

# 3. Чат
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
        system_instruction = f"""
        Ти — помічник сервера 'UKRAINE RP' у Emergency Hamburg. 
        Використовуй ці правила: {current_rules[:5000]}
        Якщо питання не про правила або не про RP на цьому сервері, відповідай: 
        'Я не знаю відповіді, так як я відповідаю на питання, лише пов'язані з правилами Сервера UKRAINE RP в Emergency Hamburg'.
        """
        
        # Запит до Gemini
        response = model.generate_content(f"{system_instruction}\n\nКористувач запитує: {prompt}")
        
        answer = response.text
        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

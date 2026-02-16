import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# Налаштування сторінки
st.set_page_config(page_title="UKRAINE RP Assistant", page_icon="🇺🇦")
st.title("🤖 Помічник сервераUKRAINE RP в EH")

# 1. Отримання правил з сайту
def get_rules_from_site():
    url = "https://ukrainerpeh.xyz/#rules"
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Отримуємо тільки текст, щоб не перевантажувати запит
        return soup.get_text(separator=' ', strip=True)
    except:
        return "Правила сервера тимчасово недоступні."

# 2. Налаштування Gemini
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Будь ласка, додайте GOOGLE_API_KEY у Secrets!")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# Завантажуємо правила (кешуємо, щоб не завантажувати щоразу)
if "rules_text" not in st.session_state:
    st.session_state.rules_text = get_rules_from_site()

# 3. Чат
if "messages" not in st.session_state:
    st.session_state.messages = []

# Відображення історії
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Поле вводу
if prompt := st.chat_input("Запитайте про правила UKRAINE RP..."):
    # Додаємо повідомлення користувача
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Відповідь ШІ
    with st.chat_message("assistant"):
        with st.spinner("Думаю..."):
            system_instruction = f"""
            Ти — помічник сервера 'UKRAINE RP' у грі Emergency Hamburg. 
            Твоя база знань: {st.session_state.rules_text[:10000]}
            
            ПРАВИЛО: Якщо питання не стосується правил сервера або RP, відповідай: 
            'Я не знаю відповіді, так як я відповідаю на питання, лише пов'язані з правилами Сервера UKRAINE RP в Emergency Hamburg'.
            """
            
            try:
                # Змінено формат запиту для стабільності
                full_prompt = f"{system_instruction}\n\nКористувач запитує: {prompt}"
                response = model.generate_content(full_prompt)
                
                if response and response.text:
                    answer = response.text
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error("ШІ не зміг згенерувати відповідь. Спробуйте ще раз.")
            except Exception as e:
                st.error(f"Виникла помилка: {e}")

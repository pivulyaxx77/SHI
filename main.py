import streamlit as st
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

# Налаштування сторінки
st.set_page_config(page_title="UKRAINE RP Assistant", page_icon="🇺🇦")
st.title("🤖 Помічник UKRAINE RP (Emergency Hamburg)")

# 1. Функція для отримання правил з вашого сайту
def get_rules_from_site():
    url = "https://ukrainerpeh.xyz/#rules"
    try:
        response = requests.get(url, timeout=10)
        # Отримуємо текст і очищаємо від тегів
        soup = BeautifulSoup(response.text, 'html.parser')
        # Беремо текст з основних блоків (можна уточнити теги, якщо правила в конкретних id)
        text = soup.get_text(separator=' ', strip=True)
        return text
    except Exception as e:
        return f"Помилка завантаження правил: {e}"

# 2. Ініціалізація ШІ через Secrets Streamlit
# Переконайтеся, що ви додали OPENAI_API_KEY у Settings -> Secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Завантажуємо актуальні правила
with st.spinner('Оновлюю правила з сайту...'):
    current_rules = get_rules_from_site()

# 3. Логіка чату
if "messages" not in st.session_state:
    st.session_state.messages = []

# Відображення історії повідомлень
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Запитайте про правила UKRAINE RP..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Промпт з вашими суворими обмеженнями
        system_instruction = f"""
        Ти — вузькоспеціалізований помічник сервера 'UKRAINE RP' у грі Emergency Hamburg.
        Твоя база знань — це текст з офіційного сайту: {current_rules}
        
        СУВОРІ ПРАВИЛА:
        1. Відповідай ТІЛЬКИ на питання про правила сервера та RP процеси.
        2. Якщо питання НЕ стосується правил або RP на цьому конкретному сервері, 
           відповідай дослівно: 'Я не знаю відповіді, так як я відповідаю на питання, лише пов'язані з правилами Сервера UKRAINE RP в Emergency Hamburg'.
        3. Не вигадуй правила, яких немає в тексті.
        4. Відповідай українською мовою.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3 # Низька температура для точності
        )
        
        answer = response.choices[0].message.content
        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

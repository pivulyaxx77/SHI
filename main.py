import os
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# API ключ Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

rules_cache = ""


def load_rules():
    """Завантаження правил із сайту"""
    global rules_cache
    try:
        r = requests.get("https://ukrainerpeh.xyz/#rules", timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(separator=" ")
        rules_cache = " ".join(text.split())
        print("Правила оновлено")
    except Exception as e:
        print("Помилка завантаження правил:", e)


# завантажити правила при старті
load_rules()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    question = request.json.get("question", "")

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
        return jsonify({"answer": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)

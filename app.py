import os
from flask import Flask, request
import requests

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8865686478:AAFoFrt4Rp3IIzxw49QyLkZrOp3d45f9PS0")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def ask_groq(message):
    try:
        if not GROQ_API_KEY:
            return "المفتاح GROQ مش موجود في Vercel!"

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": "انت بوت ذكي برمجك المهندس محمد صالح اللسامي، رد بالعربي."},
                {"role": "user", "content": message}
            ],
            "temperature": 0.7
        }
        r = requests.post(url, headers=headers, json=data, timeout=30)
        j = r.json()
        if "choices" in j:
            return j["choices"][0]["message"]["content"]
        else:
            return f"خطأ Groq: {j}"
    except Exception as e:
        return f"خطأ: {e}"

@app.route("/")
def home():
    return "Bot Ready - Mohamed Al-Lsami"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        if text == "/start":
            reply = "أهلاً! أنا بوت المهندس محمد صالح اللسامي 🤖 اسألني أي شيء!"
        else:
            reply = ask_groq(text)
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": reply})
    return "ok"

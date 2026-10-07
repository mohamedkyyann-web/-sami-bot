from flask import Flask, request
import requests
import os

app = Flask(__name__)

TOKEN = "8865686478:AAHGDP-W1Cwdb5WYHHlDngsriXp8j8Acb0Y"
GROQ_KEY = "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"

def get_ai(text):
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_KEY}"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "انت بوت يمني من تعز اسمك ذي سحر، لهجتك تعزية مضحكة، رد باختصار ودمك خفيف. صاحبك محمد"},
                    {"role": "user", "content": text}
                ]
            },
            timeout=20
        )
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(e)
    return "يا محمد النت ثقيل شوية، اسألني مرة ثانية 😅"

@app.route("/")
def home():
    return "Bot Working on Render!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if data and "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        txt = data["message"]["text"]
        reply = "هلا والله يا محمد 🔥 أنا ذي سحر من تعز، انتقلت لاستضافة جديدة قوية!" if txt == "/start" else get_ai(txt)
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": chat_id, "text": reply})
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

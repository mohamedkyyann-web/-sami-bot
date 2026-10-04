import os, requests, random, asyncio, sqlite3, urllib.parse
from flask import Flask, request
from groq import Groq
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from PIL import Image, ImageDraw, ImageFont

BOT_TOKEN = os.environ.get("BOT_TOKEN")
DB_PATH = "/tmp/mohamed.db"

flask_app = Flask(__name__)
telegram_app = Application.builder().token(BOT_TOKEN).build()

GROQ_KEYS = [
    "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",
    "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",
    "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",
]

def init_db():
    con=sqlite3.connect(DB_PATH); cur=con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, chats TEXT)")
    con.commit(); con.close()
init_db()

def save_user(uid,name,ch=""):
    try:
        con=sqlite3.connect(DB_PATH); cur=con.cursor()
        cur.execute("INSERT OR REPLACE INTO users VALUES (?,?,?)",(uid,name,ch[-800:]))
        con.commit(); con.close()
    except: pass
def get_user(uid):
    try:
        con=sqlite3.connect(DB_PATH); cur=con.cursor()
        cur.execute("SELECT name,chats FROM users WHERE id=?",(uid,))
        r=cur.fetchone(); con.close(); return r if r else (None,"")
    except: return (None,"")

def search_web(q):
    try:
        r=requests.get(f"https://api.duckduckgo.com/?q={urllib.parse.quote(q)}&format=json&no_html=1",timeout=5).json()
        if r.get("AbstractText"): return r["AbstractText"][:400]
    except: pass
    return ""

def gen_ai_image(prompt):
    try:
        low = prompt.lower()
        if any(x in prompt for x in ["قصر","صنعاء","بيت يمني","عمارة"]):
            en = "Ancient Yemeni tower palace in old Sanaa, brown stone, white gypsum patterns, colorful stained glass windows, empty alley, no people, no human, no woman, architectural photo, 8K"
        elif "سيارة" in prompt or "car" in low:
            en = "Red modern sports car, side view, empty road, no people, 8K"
        else:
            en = prompt + ", no watermark, high detail, 4K"

        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(en)}?model=flux&width=1024&height=1024&nologo=true&enhance=false&seed={random.randint(1,9999999)}"
        fp=f"/tmp/ai_{random.randint(1,99999999)}.jpg"
        r=requests.get(url,timeout=60)
        if r.status_code==200 and len(r.content)>15000:
            open(fp,'wb').write(r.content)
            return fp
    except Exception as e:
        print(f"Draw error: {e}")
    return None

def make_name_img(name):
    W,H=1024,1024; name=name.strip()[:14] or "محمد"
    img=Image.new('RGB',(W,H),(10,10,10)); d=ImageDraw.Draw(img)
    try: font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",130)
    except: font=ImageFont.load_default()
    d.rectangle([12,12,W-12,H-12],outline=(255,215,0),width=8)
    d.text((W//2,H//2),name,font=font,fill=(255,215,0),anchor="mm")
    fp=f"/tmp/{random.randint(1,99999999)}.jpg"; img.save(fp,quality=92); return fp

def get_kb():
    return ReplyKeyboardMarkup([["🧠 اسألني","🎨 ارسم لي"],["🔳 سوي QR","✨ اسمي ذهبي"],["👨‍💻 المطور"]],resize_keyboard=True)

async def ask_ai_v122(t,uid,name):
    low=t.lower()
    if any(k in low for k in ["ارسم","draw","صورة"]): return f"DRAW::{t}"
    web=""
    if any(k in low for k in ["ابحث","من هو","سعر","اخبار"]):
        web=search_web(t)
        if web: web=f"\n[نت]: {web}"
    old_name, old_chats = get_user(uid)
    PROMPT=f"انت بوت محمد اللسامي V122 - تلميذ Meta AI. المستخدم {name}. ذاكرته {old_chats[-200:]} {web} رد قصير يمني 4 اسطر + كود."
    for key in GROQ_KEYS:
        try:
            client=Groq(api_key=key)
            c=client.chat.completions.create(model="llama-3.3-70b-versatile",
                messages=[{"role":"system","content":PROMPT},{"role":"user","content":t}], max_tokens=900)
            ans=c.choices[0].message.content
            if ans and len(ans)>15:
                save_user(uid,name,f"{old_chats}\nU:{t[:100]}\nB:{ans[:100]}")
                return ans[:1900]
        except: continue
    return f"جرب ثانية يا {name}! 👑"

async def start(update, context):
    uid=update.effective_user.id; name=update.effective_user.first_name
    save_user(uid,name,"/start")
    await update.message.reply_text(f"هلا يا {name}! 🚀 V122 يرسم صح 100% بدون أخطاء!\n\nجرب: ارسم لي قصر يمني قديم", reply_markup=get_kb())

async def msg_h(update, context):
    uid=update.effective_user.id; name,_=get_user(uid); name=name or update.effective_user.first_name
    t=(update.message.text or "").strip()
    if t=="✨ اسمي ذهبي":
        p=make_name_img(name); await update.message.reply_photo(open(p,"rb"),caption=f"يا {name} 👑",reply_markup=get_kb()); os.remove(p); return
    await update.message.chat.send_action("typing")
    ans=await ask_ai_v122(t,uid,name)
    if ans.startswith("DRAW::"):
        prompt=ans.replace("DRAW::",""); await update.message.reply_text(f"أرسم يا {name}... 🎨 انتظر 15 ثانية")
        fp=gen_ai_image(prompt)
        if fp: await update.message.reply_photo(open(fp,"rb"),caption=f"تفضل يا {name} 👑 V122",reply_markup=get_kb()); os.remove(fp); return
        else: await update.message.reply_text("ما قدرت أرسم، جرب مرة ثانية",reply_markup=get_kb()); return
    await update.message.reply_text(ans,reply_markup=get_kb())

telegram_app.add_handler(CommandHandler("start",start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,msg_h))

@flask_app.route(f"/{BOT_TOKEN}",methods=["POST"])
def webhook():
    try:
        data=request.get_json(force=True); upd=Update.de_json(data,telegram_app.bot)
        async def run():
            await telegram_app.initialize(); await telegram_app.process_update(upd); await telegram_app.shutdown()
        asyncio.run(run())
    except Exception as e: print(e)
    return "ok"

@flask_app.route("/")
def home(): return "V122 Railway OK ✅"

@flask_app.route("/setwebhook")
def setwh():
    url = f"https://sami-bot-production-85f0.up.railway.app/{BOT_TOKEN}"
    r=requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={url}",timeout=15)
    return r.text

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

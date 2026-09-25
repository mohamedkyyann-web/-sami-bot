import telebot
from telebot import types
import time

TOKEN = "8865686478:AAEKR-3jJ4n6FDJDuWLo30rPdHL888Ne9TA"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(m):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📚 الثانوية", "🎓 الجامعة")
    kb.add("📖 مكتبة الكتب", "📞 تواصل معنا")
    bot.send_message(m.chat.id, "أهلاً بك في أكاديمية السامي 🌟\nاختر من القائمة:", reply_markup=kb)

@bot.message_handler(func=lambda x: True)
def all_msg(m):
    if "الثانوية" in m.text:
        bot.send_message(m.chat.id, "قسم الثانوية - قريباً بنضيف الملازم")
    elif "الجامعة" in m.text:
        bot.send_message(m.chat.id, "قسم الجامعة - قريباً")
    elif "مكتبة" in m.text:
        bot.send_message(m.chat.id, "📚 مكتبة الكتب\nارسل اسم الكتاب")
    elif "تواصل" in m.text:
        bot.send_message(m.chat.id, "تواصل: @Alsami_support")
    else:
        bot.send_message(m.chat.id, "اضغط /start")

while True:
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(e)
        time.sleep(5)

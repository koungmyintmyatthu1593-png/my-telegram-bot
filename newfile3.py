import os
import time
import threading
import random
import telebot
from flask import Flask
from waitress import serve
import gc

# =======================================================
# ၁။ Render အတွက် Web Server
# =======================================================
app = Flask('')
@app.route('/')
def home():
    return "MOVIE BOX Helper Bot Is Running Alive!"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    serve(app, host='0.0.0.0', port=port)

# =======================================================
# ၂။ Bot Setup
# =======================================================
BOT_TOKEN = '8687343780:AAEEEGqXQNLz-43fcqBRnlmxb88kCOwD4G4'
bot = telebot.TeleBot(BOT_TOKEN)
GROUP_ID = -100223906056351 

# =======================================================
# ၃။ စာဖျက်ပေးသည့် Function
# =======================================================
def delete_msg(chat_id, message_id, delay):
    time.sleep(delay)
    try:
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(f"စာဖျက်ရန် အမှား: {e}")

def send_and_schedule_delete(text, delay):
    try:
        msg = bot.send_message(GROUP_ID, text)
        threading.Thread(target=delete_msg, args=(GROUP_ID, msg.message_id, delay), daemon=True).start()
    except Exception as e:
        print(f"စာပို့ရန် အမှား: {e}")

# =======================================================
# ၄။ User Reply နှင့် Auto-delete
# =======================================================
@bot.message_handler(func=lambda message: True)
def reply_and_delete(message):
    if message.text.startswith('/start'):
        bot.reply_to(message, "မင်္ဂလာပါ! MOVIE BOX Bot အဆင်သင့်ရှိနေပါပြီဗျာ။")
        return

    sent_msg = bot.reply_to(message, "ရုပ်ရှင်ရှာဖွေပေးနေပါတယ်... 🍿🎬")
    warning_msg = bot.send_message(GROUP_ID, "‼️ movie finder bot ပို့ထားတဲ့စာက ၅ မိနစ်နေရင် အလိုလိုပျက်ပါမယ်နော် 🎬🍿 ... ‼️")
    
    threading.Thread(target=delete_msg, args=(GROUP_ID, sent_msg.message_id, 300), daemon=True).start()
    threading.Thread(target=delete_msg, args=(GROUP_ID, warning_msg.message_id, 300), daemon=True).start()

# =======================================================
# ၅။ Hourly Task (၁ နာရီတစ်ခါ)
# =======================================================
def hourly_task():
    messages = [
        "ပျင်းနေပြီလား ?", "စော်ရှိလား ?", "ဘယ်ရုပ်ရှင်ကြည့်ချင်ပါလဲ ?",
        "Movie request group ရဲ့ rules တွေကိုပြောပြရမလား ?",
        "အရမ်းချစ်တယ် ထားမသွားဘူးနော် 🥺", "အာဘွားပေး 🥺💗",
        "ဒီနေ့ဘယ်ရုပ်ရှင်တွေ trend ဖြစ်နေလဲ ?", "ဒီနေ့ ဘယ်ရုပ်ရှင်တွေကြည့်ရင်ကောင်းမလဲ ?",
        "လက်ထပ်ရအောင် 🤭💗", "သာယာတဲ့နေ့လေးတစ်နေ့ပါပဲ 🥰",
        "ဟိုကားက ကြည့်လို့ကောင်းတယ်ဆို"
    ]
    
    while True:
        send_and_schedule_delete(random.choice(messages), 2700)
        time.sleep(300)
        send_and_schedule_delete("‼️ movie finder bot ပို့ထားတဲ့စာက ၅ မိနစ်နေရင် အလိုလိုပျက်ပါမယ်နော် 🎬🍿 ... ‼️", 300)
        time.sleep(3000) 

# =======================================================
# ၆။ Main Program (Error မတက်အောင် ပြင်ဆင်ထားသည်)
# =======================================================
if __name__ == "__main__":
    threading.Thread(target=run_server, daemon=True).start()
    threading.Thread(target=hourly_task, daemon=True).start()
    
    print("Bot စတင်နေပါပြီ...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
    

import os
import time
import threading
import random
import telebot
from flask import Flask
from waitress import serve

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
    
    threading.Thread(target=delete_msg, args



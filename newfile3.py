import os
import time
import threading
import telebot
from flask import Flask
from waitress import serve

# Web Server Setup
app = Flask('')
@app.route('/')
def home():
    return "Bot is running!"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    serve(app, host='0.0.0.0', port=port)

# Bot Setup
BOT_TOKEN = '8687343780:AAEEEGqXQNLz-43fcqBRnlmxb88kCOwD4G4'
bot = telebot.TeleBot(BOT_TOKEN)

# သင့် Group ID အမှန်ကို ထည့်ထားပါသည်
GROUP_ID = -1003906056351 

@bot.message_handler(func=lambda message: True)
def reply_msg(message):
    try:
        # Group ID ကိုက်ညီမှုရှိမရှိ စစ်ဆေးပြီး စာပြန်ခြင်း
        if message.chat.id == GROUP_ID:
            bot.reply_to(message, "မင်္ဂလာပါ! ကျွန်တော် အလုပ်လုပ်နေပါပြီ 🍿🎬")
        else:
            # တခြားနေရာက စာပို့ရင်လည်း ID ကို သိအောင် ပြပေးပါလိမ့်မယ်
            bot.reply_to(message, f"ဒီ Group ရဲ့ ID က {message.chat.id} ပါ။")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    threading.Thread(target=run_server, daemon=True).start()
    print("Bot စတင်နေပါပြီ...")
    bot.infinity_polling(none_stop=True)
    

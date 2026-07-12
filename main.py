import os
import re
import threading
from flask import Flask
import telebot

# ----- CONFIGURATION -----
BOT_TOKEN = "8750561208:AAGucUHulHDIpCaFLUXpvFNHGZ9uqy1j5lY"
CHANNEL_ID = -1004438806546  # Movie Database Channel ID
GROUP_ID = -1003906056351  # Movie Request Group ID
# -------------------------

bot = telebot.TeleBot(BOT_TOKEN)
flask_app = Flask(__name__)

# ရုပ်ရှင်နာမည်နဲ့ ခုနှစ်ကို ဖမ်းယူမယ့် Regex
MOVIE_REGEX = re.compile(r"(?P<name>.+?)\s*\(?(?P<year>\b(19|20)\d{2}\b)\)?", re.IGNORECASE)

@flask_app.route('/')
def home():
    return "Bot is Alive and Running! 🚀"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port)

def delete_message_safe(chat_id, message_id):
    try:
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(f"Error deleting message: {e}")

@bot.message_handler(func=lambda message: message.chat.id == GROUP_ID and message.text is not None)
def handle_movie_request(message):
    text = message.text.strip()
    match = MOVIE_REGEX.search(text)
    if not match:
        return

    movie_name = match.group("name").strip().lower()
    movie_year = match.group("year")

    # ၁။ ရှာဖွေနေဆဲ Reply စာပို့ခြင်း
    try:
        searching_msg = bot.reply_to(message, "ခနလေးနော် ... 💗 တောင်းဆိုထားတဲ့ movie ကိုရှာဖွေနေပါတယ် ... 🎬‼️")
        threading.Timer(5, delete_message_safe, args=[GROUP_ID, searching_msg.message_id]).start()
    except Exception as e:
        print(f"Error: {e}")

    # ၂။ ရုပ်ရှင်ရှာမတွေ့ပါ စာတို (၅ မိနစ်ပြည့်ရင် ပျက်မည်)
    not_found_msg = bot.reply_to(message, "ခနစောင့်ပေးပါ🎬🍿 group admin တွေက movie upload နေပါတယ်... ⭐")
    threading.Timer(300, delete_message_safe, args=[GROUP_ID, not_found_msg.message_id]).start()

if __name__ == "__main__":
    print("Movie Finder Bot က အောင်မြင်စွာ စတင်လည်ပတ်နေပါပြီ... 🚀")
    
    # Flask Web Server ကို Background Thread မှာ မောင်းမယ်
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Bot ကို ရပ်မသွားအောင် ပတ်ထားမယ်
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
    

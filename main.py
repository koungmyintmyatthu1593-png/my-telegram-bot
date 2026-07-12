import os
import re
import threading
from fastapi import FastAPI, Request
import telebot

# ----- CONFIGURATION -----
BOT_TOKEN = "8942001881:AAETgL-CvjxwH-2SZ-bQqcF_HzOGXhZaYVU"
CHANNEL_ID = -1004438806546  # Movie Database Channel
GROUP_ID = -1003906056351    # Movie Request Group
# -------------------------

bot = telebot.TeleBot(BOT_TOKEN, threaded=True)
app = FastAPI()

# ရုပ်ရှင်နာမည်နဲ့ ခုနှစ်ကို ဖမ်းယူမယ့် Regex
MOVIE_REGEX = re.compile(r"(?P<name>.+?)\s*\(?(?P<year>\b(19|20)\d{2}\b)\)?", re.IGNORECASE)

# Render က ၂၄ နာရီ လာစစ်ရင် အလုပ်လုပ်မယ့် ပင်မလမ်းကြောင်း
@app.get("/")
def read_root():
    return {"status": "Movie Finder Bot is running 24/7 🚀"}

# Telegram ကစာတွေကို လက်ခံမယ့် Webhook လမ်းကြောင်း
@app.post(f"/{BOT_TOKEN}")
async def process_webhook(request: Request):
    json_string = await request.json()
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return {"status": "ok"}

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

    # ၁။ ရှာဖွေနေဆဲ Reply စာပို့ခြင်း (၅ စက္ကန့်နေရင် ပျက်မည်)
    try:
        searching_msg = bot.reply_to(message, "ခနလေးနော် ... 💗 တောင်းဆိုထားတဲ့ movie ကိုရှာဖွေနေပါတယ် ... 🎬‼️")
        threading.Timer(5, delete_message_safe, args=[GROUP_ID, searching_msg.message_id]).start()
    except Exception as e:
        print(f"Error: {e}")

    # ၂။ Admin တင်ပေးနေပါ စာတို (၅ မိနစ်ပြည့်ရင် ပျက်မည်)
    try:
        not_found_msg = bot.reply_to(message, "ခနစောင့်ပေးပါ🎬🍿 group admin တွေက movie upload နေပါတယ်... ⭐")
        threading.Timer(300, delete_message_safe, args=[GROUP_ID, not_found_msg.message_id]).start()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
        

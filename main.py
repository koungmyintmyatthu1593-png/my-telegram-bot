import os
import re
import threading
from fastapi import FastAPI, Request
import telebot

# ----- CONFIGURATION -----
BOT_TOKEN = "8942001881:AAETgL-CvjxwH-2SZ-bQqcF_HzOGXhZaYVU"
CHANNEL_ID = -1004438806546  # ရုပ်ရှင်တင်သည့် Channel ID
GROUP_ID = -1003906056351    # ရုပ်ရှင်တောင်းသည့် Group ID
# -------------------------

bot = telebot.TeleBot(BOT_TOKEN, threaded=True)
app = FastAPI()

# Bot ရဲ့ မှတ်ဉာဏ် (Channel ထဲမှာ Post အသစ်တက်တိုင်း ဒါကိုဖြည့်သွားပါမယ်)
MOVIE_MEMORY = {} 

MOVIE_REGEX = re.compile(r"(?P<name>.+?)\s*\(?(?P<year>\b(19|20)\d{2}\b)\)?", re.IGNORECASE)

@app.post(f"/{BOT_TOKEN}")
async def process_webhook(request: Request):
    bot.process_new_updates([telebot.types.Update.de_json(await request.json())])
    return {"status": "ok"}

def delete_message_safe(chat_id, message_id):
    try: bot.delete_message(chat_id, message_id)
    except: pass

# 1. Channel ထဲမှာ Post အသစ်တင်ရင် (သို့မဟုတ်) Forward လုပ်ရင် Bot က အော်တိုမှတ်မယ်
@bot.channel_post_handler(func=lambda message: message.chat.id == CHANNEL_ID)
def scan_movie(message):
    text = message.text or message.caption
    if text:
        match = MOVIE_REGEX.search(text)
        if match:
            key = f"{match.group('name').strip().lower()} {match.group('year').strip()}"
            MOVIE_MEMORY[key] = message.message_id
            print(f"🎬 Saved to Memory: {key} -> {message.message_id}")

# 2. Group ထဲက တောင်းဆိုမှုကို ချက်ချင်းဖြေပေးမယ်
@bot.message_handler(func=lambda message: message.chat.id == GROUP_ID and message.text)
def find_movie(message):
    match = MOVIE_REGEX.search(message.text)
    if not match: return
    
    key = f"{match.group('name').strip().lower()} {match.group('year').strip()}"
    
    # ၅ စက္ကန့်စာ ပို့ခြင်း
    searching_msg = bot.reply_to(message, "ခနလေးနော် ... 💗 တောင်းဆိုထားတဲ့ movie ကိုရှာဖွေနေပါတယ် ... 🎬‼️")
    threading.Timer(5, delete_message_safe, args=[GROUP_ID, searching_msg.message_id]).start()
    
    if key in MOVIE_MEMORY:
        try:
            fwd = bot.forward_message(GROUP_ID, CHANNEL_ID, MOVIE_MEMORY[key])
            alert = bot.reply_to(message, "movie finder bot 🔎 ပို့ထားတဲ့ post က ၅ မိနစ်နေရင် အလိုလိုပျက်ပါမယ်နော်🍿🎬 ... ‼️")
            threading.Timer(300, delete_message_safe, args=[GROUP_ID, fwd.message_id]).start()
            threading.Timer(300, delete_message_safe, args=[GROUP_ID, alert.message_id]).start()
        except Exception as e:
            print(f"Forward Error: {e}")
    else:
        not_found = bot.reply_to(message, "ခနစောင့်ပေးပါ🎬🍿 group admin တွေက movie upload နေပါတယ်... ⭐")
        threading.Timer(300, delete_message_safe, args=[GROUP_ID, not_found.message_id]).start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    

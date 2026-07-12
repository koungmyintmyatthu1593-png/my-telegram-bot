import os
import re
import threading
import sqlite3
from fastapi import FastAPI, Request
import telebot

# ----- CONFIGURATION -----
BOT_TOKEN = "8942001881:AAETgL-CvjxwH-2SZ-bQqcF_HzOGXhZaYVU"
CHANNEL_ID = -1004438806546
GROUP_ID = -1003906056351
# Render ရဲ့ /tmp folder က ပျက်တတ်လို့ အလုပ်လုပ်တဲ့ directory ထဲမှာပဲ database သိမ်းမယ်
DB_FILE = "movies.db" 
# -------------------------

bot = telebot.TeleBot(BOT_TOKEN, threaded=True)
app = FastAPI()

# Database သေချာချိတ်ဆက်ရန်
def get_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    return conn

# Table အသေဆောက်ခြင်း
conn = get_db()
conn.execute('CREATE TABLE IF NOT EXISTS movies (movie_key TEXT PRIMARY KEY, message_id INTEGER)')
conn.commit()
conn.close()

MOVIE_REGEX = re.compile(r"(?P<name>.+?)\s*\(?(?P<year>\b(19|20)\d{2}\b)\)?", re.IGNORECASE)

@app.post(f"/{BOT_TOKEN}")
async def process_webhook(request: Request):
    json_string = await request.json()
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return {"status": "ok"}

def delete_message_safe(chat_id, message_id):
    try:
        bot.delete_message(chat_id, message_id)
    except: pass

@bot.channel_post_handler(func=lambda message: message.chat.id == CHANNEL_ID)
def save_movie(message):
    text = message.text or message.caption
    if not text: return
    match = MOVIE_REGEX.search(text)
    if match:
        key = f"{match.group('name').strip().lower()} {match.group('year').strip()}"
        conn = get_db()
        conn.execute("INSERT OR REPLACE INTO movies VALUES (?, ?)", (key, message.message_id))
        conn.commit()
        conn.close()

@bot.message_handler(func=lambda message: message.chat.id == GROUP_ID and message.text)
def find_movie(message):
    match = MOVIE_REGEX.search(message.text)
    if not match: return
    
    key = f"{match.group('name').strip().lower()} {match.group('year').strip()}"
    
    conn = get_db()
    row = conn.execute("SELECT message_id FROM movies WHERE movie_key = ?", (key,)).fetchone()
    conn.close()

    if row:
        fwd = bot.forward_message(GROUP_ID, CHANNEL_ID, row[0])
        msg = bot.reply_to(message, "၅ မိနစ်နေရင် အလိုလိုပျက်ပါမယ်... 🍿")
        threading.Timer(300, delete_message_safe, args=[GROUP_ID, fwd.message_id]).start()
        threading.Timer(300, delete_message_safe, args=[GROUP_ID, msg.message_id]).start()
    else:
        msg = bot.reply_to(message, "ခနစောင့်ပေးပါ... ရုပ်ရှင်ရှာမတွေ့သေးပါ 🎬")
        threading.Timer(30, delete_message_safe, args=[GROUP_ID, msg.message_id]).start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    

import os
import re
import threading
import sqlite3
from fastapi import FastAPI, Request
import telebot

# ----- CONFIGURATION -----
BOT_TOKEN = "8942001881:AAETgL-CvjxwH-2SZ-bQqcF_HzOGXhZaYVU"
CHANNEL_ID = -1004438806546  # ရုပ်ရှင်တင်သည့် Channel ID
GROUP_ID = -1003906056351    # ရုပ်ရှင်တောင်းသည့် Group ID
DB_FILE = "movies.db"        # ရုပ်ရှင်များကို အသေသိမ်းမည့် Database File
# -------------------------

bot = telebot.TeleBot(BOT_TOKEN, threaded=True)
app = FastAPI()

# Database Setup (ဘယ်တော့မှ ဒေတာမပျောက်စေရန် အသေဆောက်ခြင်း)
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            movie_key TEXT PRIMARY KEY,
            message_id INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_db()

MOVIE_REGEX = re.compile(r"(?P<name>.+?)\s*\(?(?P<year>\b(19|20)\d{2}\b)\)?", re.IGNORECASE)

@app.get("/")
def read_root():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM movies")
    total = cursor.fetchone()[0]
    conn.close()
    return {"status": "Movie Finder Bot is running 24/7 🚀", "total_stored_movies": total}

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

# 1. Channel ထဲမှာ တင်သမျှ ရုပ်ရှင်များကို စာအုပ်ထဲမှတ်သလို အသေမှတ်သားမည့်စနစ်
@bot.channel_post_handler(func=lambda message: message.chat.id == CHANNEL_ID)
def handle_channel_movie(message):
    text = message.text or message.caption
    if not text:
        return
        
    match = MOVIE_REGEX.search(text)
    if match:
        movie_name = match.group("name").strip().lower()
        movie_name = re.sub(r"\b(ကို|ကြည့်ချင်တယ်|ရှာပေး|ကြည့်ချင်လို့)\b", "", movie_name).strip()
        movie_year = match.group("year").strip()
        
        search_key = f"{movie_name} {movie_year}"
        
        # Database ထဲသို့ အသေထည့်ခြင်း
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO movies (movie_key, message_id) VALUES (?, ?)", (search_key, message.message_id))
        conn.commit()
        conn.close()
        print(f"💾 Movie Permanently Saved: {search_key} -> {message.message_id}")

# 2. Group ထဲက တောင်းဆိုမှုများကို လုပ်ဆောင်ပေးမည့်စနစ်
@bot.message_handler(func=lambda message: message.chat.id == GROUP_ID and message.text is not None)
def handle_movie_request(message):
    text = message.text.strip()
    match = MOVIE_REGEX.search(text)
    if not match:
        return

    movie_name = match.group("name").strip().lower()
    movie_name = re.sub(r"\b(ကို|ကြည့်ချင်တယ်|ရှာပေး|ကြည့်ချင်လို့)\b", "", movie_name).strip()
    movie_year = match.group("year").strip()
    search_key = f"{movie_name} {movie_year}"

    # Function ၁ - ရှာဖွေနေဆဲ ပြန်စာပို့ခြင်း (၅ စက္ကန့်နေရင် ပျက်မည်)
    try:
        searching_msg = bot.reply_to(message, "ခနလေးနော် ... 💗 တောင်းဆိုထားတဲ့ movie ကိုရှာဖွေနေပါတယ် ... 🎬‼️")
        threading.Timer(5, delete_message_safe, args=[GROUP_ID, searching_msg.message_id]).start()
    except Exception as e:
        print(f"Error: {e}")

    # Database ထဲမှာ ရုပ်ရှင် ရှိ/မရှိ လှမ်းစစ်ခြင်း
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT message_id FROM movies WHERE movie_key = ?", (search_key,))
    row = cursor.fetchone()
    conn.close()

    # Function ၂ - ရုပ်ရှင်တွေ့ရင် လုပ်ဆောင်မည့်အပိုင်း
    if row:
        target_message_id = row[0]
        try:
            # ရုပ်ရှင်ကို Forward လုပ်ခြင်း
            forwarded_movie = bot.forward_message(chat_id=GROUP_ID, from_chat_id=CHANNEL_ID, message_id=target_message_id)
            
            # သတိပေးစာကို Reply ပြန်ခြင်း
            alert_msg = bot.reply_to(message, "movie finder bot 🔎 ပို့ထားတဲ့ post က ၅ မိနစ်နေရင် အလိုလိုပျက်ပါမယ်နော်🍿🎬 ... ‼️")
            
            # ၅ မိနစ် (၃၀၀ စက္ကန့်) ပြည့်ရင် ၎င်းနှစ်ခုလုံးကို ဖျက်ခြင်း
            threading.Timer(300, delete_message_safe, args=[GROUP_ID, forwarded_movie.message_id]).start()
            threading.Timer(300, delete_message_safe, args=[GROUP_ID, alert_msg.message_id]).start()
        except Exception as e:
            print(f"Error forwarding: {e}")
            
    # ရုပ်ရှင်မတွေ့ရင် "Admin တွေတင်ပေးနေပါတယ်" ဟု Reply ပြန်ခြင်း (၅ မိနစ်နေရင် ပျက်မည်)
    else:
        try:
            not_found_msg = bot.reply_to(message, "ခနစောင့်ပေးပါ🎬🍿 group admin တွေက movie upload နေပါတယ်... ⭐")
            threading.Timer(300, delete_message_safe, args=[GROUP_ID, not_found_msg.message_id]).start()
        except Exception as e:
            print(f"Error sending not found message: {e}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
        

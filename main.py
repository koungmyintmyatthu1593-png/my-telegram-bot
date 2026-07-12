import os
import sqlite3
from fastapi import FastAPI, Request
import telebot
import uvicorn

BOT_TOKEN = "8942001881:AAETgL-CvjxwH-2SZ-bQqcF_HzOGXhZaYVU"
CHANNEL_ID = -1004438806546
GROUP_ID = -1003906056351

# Render ရဲ့ project directory ထဲမှာ db file ကို အသေသိမ်းမယ်
DB_PATH = os.path.join(os.getcwd(), "movies.db")
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS movies (key TEXT PRIMARY KEY, msg_id INTEGER)")
conn.commit()

bot = telebot.TeleBot(BOT_TOKEN)
app = FastAPI()

@app.get("/") # UptimeRobot အတွက် ပေါ့ပါးတဲ့ Endpoint
def keep_alive():
    return {"status": "Bot is running 24/7"}

@app.post(f"/{BOT_TOKEN}")
async def handle(request: Request):
    bot.process_new_updates([telebot.types.Update.de_json(await request.json())])
    return {"status": "ok"}

@bot.channel_post_handler(func=lambda m: m.chat.id == CHANNEL_ID)
def save_movie(m):
    text = (m.text or m.caption or "").strip().lower()
    if text:
        cursor.execute("INSERT OR REPLACE INTO movies (key, msg_id) VALUES (?, ?)", (text, m.message_id))
        conn.commit()

@bot.message_handler(func=lambda m: m.chat.id == GROUP_ID and m.text)
def find_movie(m):
    key = m.text.strip().lower()
    cursor.execute("SELECT msg_id FROM movies WHERE key=?", (key,))
    row = cursor.fetchone()
    if row:
        bot.forward_message(GROUP_ID, CHANNEL_ID, row[0])
    else:
        bot.reply_to(m, "ရုပ်ရှင်မတွေ့ပါခင်ဗျာ။")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
                          

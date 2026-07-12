import os
import json
import re
from fastapi import FastAPI, Request
import telebot

BOT_TOKEN = "8942001881:AAETgL-CvjxwH-2SZ-bQqcF_HzOGXhZaYVU"
CHANNEL_ID = -1004438806546
GROUP_ID = -1003906056351
DB_FILE = "movies.json" # ဒေတာကို ဒီဖိုင်ထဲမှာ အသေသိမ်းမယ်

bot = telebot.TeleBot(BOT_TOKEN)
app = FastAPI()

# ဒေတာကို ဖိုင်ထဲကနေ ပြန်ဖတ်မယ်
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return {}

# ဒေတာကို ဖိုင်ထဲမှာ အသေသိမ်းမယ်
def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

@app.post(f"/{BOT_TOKEN}")
async def process_webhook(request: Request):
    update = telebot.types.Update.de_json(await request.json())
    bot.process_new_updates([update])
    return {"status": "ok"}

# ရုပ်ရှင်တင်ရင် ဖိုင်ထဲမှာ အော်တိုမှတ်မယ်
@bot.channel_post_handler(func=lambda message: message.chat.id == CHANNEL_ID)
def save_movie(message):
    text = message.text or message.caption
    if text:
        db = load_db()
        db[text.strip().lower()] = message.message_id
        save_db(db)
        print(f"✅ Saved: {text.strip().lower()}")

# ရုပ်ရှင်တောင်းရင် ဖိုင်ထဲကနေ ရှာပေးမယ်
@bot.message_handler(func=lambda message: message.chat.id == GROUP_ID and message.text)
def find_movie(message):
    key = message.text.strip().lower()
    db = load_db()
    if key in db:
        bot.forward_message(GROUP_ID, CHANNEL_ID, db[key])
    else:
        bot.reply_to(message, "❌ ရှာမတွေ့ပါ - ပိုမိုတိကျသော နာမည်ဖြင့် ထပ်ရှာကြည့်ပေးပါခင်ဗျာ။")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    

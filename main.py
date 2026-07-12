import os
from fastapi import FastAPI, Request
import telebot

BOT_TOKEN = "8942001881:AAETgL-CvjxwH-2SZ-bQqcF_HzOGXhZaYVU"
CHANNEL_ID = -1004438806546
GROUP_ID = -1003906056351

bot = telebot.TeleBot(BOT_TOKEN)
app = FastAPI()

# Database မလိုဘဲ မှတ်ထားမယ့် နေရာ (Dictionary)
# Render restart ကျတိုင်း ဒါက ပြန်လည်စတင်ပါမယ်
MOVIE_DB = {}

@app.post(f"/{BOT_TOKEN}")
async def handle(request: Request):
    bot.process_new_updates([telebot.types.Update.de_json(await request.json())])
    return {"status": "ok"}

# Channel ထဲမှာ Forward လုပ်တာနဲ့ မှတ်သွားမယ်
@bot.channel_post_handler(func=lambda m: m.chat.id == CHANNEL_ID)
def save_movie(m):
    text = (m.text or m.caption or "").strip().lower()
    if text:
        MOVIE_DB[text] = m.message_id
        print(f"✅ Saved: {text} -> {m.message_id}")

# Group ထဲမှာ ရှာရင် ချက်ချင်းပြန်ဖြေမယ်
@bot.message_handler(func=lambda m: m.chat.id == GROUP_ID and m.text)
def find_movie(m):
    key = m.text.strip().lower()
    if key in MOVIE_DB:
        bot.forward_message(GROUP_ID, CHANNEL_ID, MOVIE_DB[key])
    else:
        bot.reply_to(m, "❌ ရုပ်ရှင်မတွေ့ပါ - ရုပ်ရှင် Post ကို Channel ထဲမှာ Forward တစ်ချက် လုပ်ပေးလိုက်ပါ။")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
                     

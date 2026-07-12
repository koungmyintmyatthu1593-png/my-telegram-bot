import asyncio
import os
import re
from fastapi import FastAPI
import uvicorn
from pyrogram import Client, filters
from pyrogram.types import Message

# ----- CONFIGURATION -----
BOT_TOKEN = "8750561208:AAGucUHulHDIpCaFLUXpvFNHGZ9uqy1j5lY"

# ⚠️ Telegram ရဲ့ တရားဝင် အများသုံး ID တွေဖြစ်လို့ ဒါကိုပဲ သုံးထားပါတယ် (Error ကင်းစေရန်)
API_ID = 6  
API_HASH = "eb06d4abfb49dc3eeb1aeb98ae330575"

CHANNEL_ID = -1004438806546  # Movie Database Channel ID
GROUP_ID = -1003906056351  # Movie Request Group ID
# -------------------------

# FastAPI ဆောက်ခြင်း
api_app = FastAPI()

# Pyrogram Client ဆောက်ခြင်း
bot_app = Client("MovieBox_gp_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ရုပ်ရှင်နာမည်နဲ့ ခုနှစ်ကို ဖမ်းယူမယ့် Regex
MOVIE_REGEX = re.compile(r"(?P<name>.+?)\s*\(?(?P<year>\b(19|20)\d{2}\b)\)?", re.IGNORECASE)

@api_app.get("/")
def read_root():
    return {"status": "alive", "message": "Movie Finder Bot is running flawlessly! 🚀"}

async def delete_message_after(chat_id: int, message_id: int, delay: int):
    """သတ်မှတ်ထားတဲ့ စက္ကန့် ပြည့်ရင် Message ကို ပြန်ဖျက်ပေးမယ့် လုပ်ဆောင်ချက်"""
    await asyncio.sleep(delay)
    try:
        await bot_app.delete_messages(chat_id, message_id)
    except Exception as e:
        print(f"Error deleting message {message_id}: {e}")

@bot_app.on_message(filters.chat(GROUP_ID) & filters.text)
async def handle_movie_request(client: Client, message: Message):
    text = message.text.strip()
    match = MOVIE_REGEX.search(text)
    if not match:
        return

    movie_name = match.group("name").strip().lower()
    movie_year = match.group("year")

    # 1. ရှာဖွေနေဆဲ Reply စာပို့ခြင်း
    searching_msg = await message.reply_text("ခနလေးနော် ... 💗 တောင်းဆိုထားတဲ့ movie ကိုရှာဖွေနေပါတယ် ... 🎬‼️", quote=True)
    asyncio.create_task(delete_message_after(GROUP_ID, searching_msg.id, 5))

    found_msg_id = None
    
    # 2. Channel ထဲက Post တွေကို Scan ဖတ်ခြင်း
    async for msg in bot_app.get_chat_history(CHANNEL_ID):
        msg_text = msg.caption or msg.text
        if msg_text:
            if movie_name in msg_text.lower() and movie_year in msg_text:
                found_msg_id = msg.id
                break

    # ရုပ်ရှင်တွေ့ရင် Copy ကူးပို့ပြီး ၅ မိနစ်နေရင် ပြန်ဖျက်ခြင်း
    if found_msg_id:
        copied_movie = await bot_app.copy_message(chat_id=GROUP_ID, from_chat_id=CHANNEL_ID, message_id=found_msg_id, reply_to_message_id=message.id)
        notice_msg = await bot_app.send_message(chat_id=GROUP_ID, text="movie finder bot 🔎 ပို့ထားတဲ့ post က ၅ မိနစ်ရင် အလိုလိုပျက်ပါမယ်နော်🍿🎬 ... ‼️", reply_to=copied_movie.id)
        asyncio.create_task(delete_message_after(GROUP_ID, copied_movie.id, 300))
        asyncio.create_task(delete_message_after(GROUP_ID, notice_msg.id, 300))
    else:
        # ရုပ်ရှင်မတွေ့ရင် ပြမယ့်စာ
        not_found_msg = await message.reply_text("ခနစောင့်ပေးပါ🎬🍿 group admin တွေက movie upload နေပါတယ်... ⭐", quote=True)
        asyncio.create_task(delete_message_after(GROUP_ID, not_found_msg.id, 300))

@bot_app.on_message(filters.private)
async def handle_private(client: Client, message: Message):
    return

# FastAPI စပွင့်တာနဲ့ Bot ပါ တပြိုင်တည်း ပွင့်လာအောင် ချိတ်ဆက်ခြင်း
@api_app.on_event("startup")
async def startup_event():
    # အရင်ကျန်ခဲ့တဲ့ Session ဖိုင်အဟောင်းရှိရင် ရှင်းပစ်ခြင်း
    if os.path.exists("MovieBox_gp_bot.session"):
        try:
            os.remove("MovieBox_gp_bot.session")
        except:
            pass
    await bot_app.start()
    print("Telegram Bot Started Successfully! 🚀")

@api_app.on_event("shutdown")
async def shutdown_event():
    await bot_app.stop()

if __name__ == "__main__":
    # Render ရဲ့ Port ပေါ်မှာ စနစ်တကျ မောင်းနှင်ခြင်း
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:api_app", host="0.0.0.0", port=port, loop="asyncio")

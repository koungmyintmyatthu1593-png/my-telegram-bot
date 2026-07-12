import asyncio
import os
import threading
import re
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import Message

# ----- CONFIGURATION -----
BOT_TOKEN = "8750561208:AAGucUHulHDIpCaFLUXpvFNHGZ9uqy1j5lY"
API_ID = 26543187  
API_HASH = "8b9e6dc3b8e4e9ad2c2892976b9788f4"

CHANNEL_ID = -1004438806546  
GROUP_ID = -1003906056351  
# -------------------------

app = Client("MovieBox_gp_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
MOVIE_REGEX = re.compile(r"(?P<name>.+?)\s*\(?(?P<year>\b(19|20)\d{2}\b)\)?", re.IGNORECASE)

flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot is Alive and Running! 🚀"

def run_flask():
    # Render ရဲ့ Port ကို အလိုအလျောက် ဖတ်ပြီး Run ပေးမယ်
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port)

async def delete_message_after(chat_id: int, message_id: int, delay: int):
    await asyncio.sleep(delay)
    try:
        await app.delete_messages(chat_id, message_id)
    except Exception as e:
        print(f"Error deleting message {message_id}: {e}")

@app.on_message(filters.chat(GROUP_ID) & filters.text)
async def handle_movie_request(client: Client, message: Message):
    text = message.text.strip()
    match = MOVIE_REGEX.search(text)

    if not match:
        return

    movie_name = match.group("name").strip().lower()
    movie_year = match.group("year")

    searching_msg = await message.reply_text(
        "ခနလေးနော် ... 💗 တောင်းဆိုထားတဲ့ movie ကိုရှာဖွေနေပါတယ် ... 🎬‼️",
        quote=True
    )
    asyncio.create_task(delete_message_after(GROUP_ID, searching_msg.id, 5))

    found_msg_id = None

    async for msg in app.get_chat_history(CHANNEL_ID):
        msg_text = msg.caption or msg.text
        if msg_text:
            msg_text_lower = msg_text.lower()
            if movie_name in msg_text_lower and movie_year in msg_text_lower:
                found_msg_id = msg.id
                break

    if found_msg_id:
        copied_movie = await app.copy_message(
            chat_id=GROUP_ID,
            from_chat_id=CHANNEL_ID,
            message_id=found_msg_id,
            reply_to_message_id=message.id
        )

        notice_msg = await app.send_message(
            chat_id=GROUP_ID,
            text="movie finder bot 🔎 ပို့ထားတဲ့ post က ၅ မိနစ်ရင် အလိုလိုပျက်ပါမယ်နော်🍿🎬 ... ‼️",
            reply_to=copied_movie.id
        )

        asyncio.create_task(delete_message_after(GROUP_ID, copied_movie.id, 300))
        asyncio.create_task(delete_message_after(GROUP_ID, notice_msg.id, 300))
    else:
        not_found_msg = await message.reply_text(
            "ခနစောင့်ပေးပါ🎬🍿 group admin တွေက movie upload နေပါတယ်... ⭐",
            quote=True
        )
        asyncio.create_task(delete_message_after(GROUP_ID, not_found_msg.id, 300))

@app.on_message(filters.private)
async def handle_private(client: Client, message: Message):
    return

async def main():
    # Web Server ကို Background မှာ Run မယ်
    threading.Thread(target=run_flask, daemon=True).start()
    print("Movie Finder Bot က Render ပေါ်မှာ စတင်လည်ပတ်နေပါပြီ... 🚀")
    
    # Pyrogram Client ကို စနစ်တကျ အသက်သွင်းမယ်
    await app.start()
    # Bot ကို အမြဲတမ်း Live ဖြစ်နေအောင် စောင့်ကြည့်ခိုင်းမယ်
    await asyncio.Event().wait()

if __name__ == "__main__":
    # Asyncio Loop ကို အမှားကင်းဆုံး နည်းလမ်းဖြင့် Run ခြင်း
    asyncio.run(main())

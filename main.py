import asyncio
import re
import threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import Message

# ----- CONFIGURATION -----
# ⚠️ သင်ပေးပို့ထားတဲ့ TOKEN အသစ်ကို ဒီနေရာမှာ တစ်ခါတည်း ထည့်ပေးထားပါတယ်
BOT_TOKEN = "8750561208:AAGucUHulHDIpCaFLUXpvFNHGZ9uqy1j5lY"

# Pyrogram အတွက် လိုအပ်သော ID များ
API_ID = 26543187  
API_HASH = "8b9e6dc3b8e4e9ad2c2892976b9788f4"

CHANNEL_ID = -1004438806546  # Movie Database Channel ID
GROUP_ID = -1003906056351  # Movie Request Group ID
# -------------------------

app = Client("MovieBox_gp_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ရုပ်ရှင်နာမည်နဲ့ ခုနှစ် (၄ လုံးတွဲ) ကို () ပါပါ မပါပါ၊ စာလုံးကြီးသေး ခွဲခြားမှုမရှိ ဖမ်းယူမယ့် Regex
MOVIE_REGEX = re.compile(r"(?P<name>.+?)\s*\(?(?P<year>\b(19|20)\d{2}\b)\)?", re.IGNORECASE)

# --- Uptime Root (Web Server) ပုတ်နှိုးဖို့အတွက် Flask App တည်ဆောက်ခြင်း ---
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot is Alive and Running! 🚀"

def run_flask():
    # Render ရဲ့ Port 8080 မှာ Web Server ကို ဖွင့်လှစ်ပေးခြင်း
    flask_app.run(host='0.0.0.0', port=8080)
# ------------------------------------------------------------------

async def delete_message_after(chat_id: int, message_id: int, delay: int):
    """သတ်မှတ်ထားတဲ့ စက္ကန့်/မိနစ် ပြည့်ရင် Message ကို အလိုအလျောက် ပြန်ဖျက်ပေးမယ့် လုပ်ဆောင်ချက်"""
    await asyncio.sleep(delay)
    try:
        await app.delete_messages(chat_id, message_id)
    except Exception as e:
        print(f"Error deleting message {message_id}: {e}")


@app.on_message(filters.chat(GROUP_ID) & filters.text)
async def handle_movie_request(client: Client, message: Message):
    text = message.text.strip()
    match = MOVIE_REGEX.search(text)

    # စာထဲမှာ ရုပ်ရှင်နာမည်နဲ့ ခုနှစ် မပါဝင်ရင် Bot က စာမပြန်ဘဲ ကျော်သွားမယ်
    if not match:
        return

    movie_name = match.group("name").strip().lower()
    movie_year = match.group("year")

    # 1. ပထမဆုံး Function - "ရှာဖွေနေပါတယ်" စာကို Reply ပြန်ခြင်း
    searching_msg = await message.reply_text(
        "ခနလေးနော် ... 💗 တောင်းဆိုထားတဲ့ movie ကိုရှာဖွေနေပါတယ် ... 🎬‼️",
        quote=True
    )
    # ၅ စက္ကန့်ပြည့်ရင် အဲ့ဒီ Reply ကို အလိုအလိုပြန်ဖျက်မယ်
    asyncio.create_task(delete_message_after(GROUP_ID, searching_msg.id, 5))

    found_msg_id = None

    # 2. ဒုတိယ Function - Channel ထဲက Post တွေအားလုံးကို Scan ဖတ်ပြီး ရှာဖွေခြင်း
    async for msg in app.get_chat_history(CHANNEL_ID):
        msg_text = msg.caption or msg.text
        if msg_text:
            msg_text_lower = msg_text.lower()
            # နာမည်ရော ခုနှစ်ပါ ကိုက်ညီမှုရှိရင် Target အဖြစ် သတ်မှတ်မယ်
            if movie_name in msg_text_lower and movie_year in msg_text_lower:
                found_msg_id = msg.id
                break

    # ရုပ်ရှင် Post ကို ရှာဖွေတွေ့ရှိရင်
    if found_msg_id:
        # Group ထဲကို အဲ့ဒီ Post ကို Forward (Copy) ပို့ပေးပြီး User ကို Reply ထောက်ပေးမယ်
        copied_movie = await app.copy_message(
            chat_id=GROUP_ID,
            from_chat_id=CHANNEL_ID,
            message_id=found_msg_id,
            reply_to_message_id=message.id
        )

        # သတိပေးစာ ထပ်မံ ပို့ပေးခြင်း
        notice_msg = await app.send_message(
            chat_id=GROUP_ID,
            text="movie finder bot 🔎 ပို့ထားတဲ့ post က ၅ မိနစ်နေရင် အလိုလိုပျက်ပါမယ်နော်🍿🎬 ... ‼️",
            reply_to=copied_movie.id
        )

        # ၅ မိနစ် (စက္ကန့် ၃၀၀) ပြည့်ရင် ရုပ်ရှင် Post ရော သတိပေးစာပါ အလိုအလျောက် ပြန်ဖျက်မယ်
        asyncio.create_task(delete_message_after(GROUP_ID, copied_movie.id, 300))
        asyncio.create_task(delete_message_after(GROUP_ID, notice_msg.id, 300))

    # ရုပ်ရှင် Post ကို ရှာမတွေ့ခဲ့ရင်
    else:
        not_found_msg = await message.reply_text(
            "ခနစောင့်ပေးပါ🎬🍿 group admin တွေက movie upload နေပါတယ်... ⭐",
            quote=True
        )
        # ၅ မိနစ် (စက္ကန့် ၃၀၀) ပြည့်ရင် အဲ့ဒီစာကို ပြန်ဖျက်မယ်
        asyncio.create_task(delete_message_after(GROUP_ID, not_found_msg.id, 300))


# Bot ရဲ့ Private Chat ထဲ ဝင်ပြောရင် စာမပြန်အောင် ပိတ်ထားခြင်း
@app.on_message(filters.private)
async def handle_private(client: Client, message: Message):
    return


if __name__ == "__main__":
    # Web Server (Flask) ကို Background Thread အနေနဲ့ အရင်ပတ်ထားမယ်
    threading.Thread(target=run_flask, daemon=True).start()
    
    print("Movie Finder Bot က Render ပေါ်မှာ အဆင်သင့် ဖြစ်နေပါပြီ... 🚀")
    app.run()
        

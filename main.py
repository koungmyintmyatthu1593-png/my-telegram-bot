import os
import re
import threading
from fastapi import FastAPI, Request
import telebot

# ----- CONFIGURATION -----
BOT_TOKEN = "8942001881:AAETgL-CvjxwH-2SZ-bQqcF_HzOGXhZaYVU"
CHANNEL_ID = -1004438806546  # ရုပ်ရှင်တွေတင်ထားတဲ့ Channel ID
GROUP_ID = -1003906056351    # ရုပ်ရှင်တောင်းတဲ့ Group ID
# -------------------------

bot = telebot.TeleBot(BOT_TOKEN, threaded=True)
app = FastAPI()

# စာလုံးကြီးသေး၊ space၊ () ပါပါမပါပါ နှစ်ခုလုံးကို ဖမ်းပေးမယ့် အဆင့်မြင့် Regex
MOVIE_REGEX = re.compile(r"(?P<name>.+?)\s*\(?(?P<year>\b(19|20)\d{2}\b)\)?", re.IGNORECASE)

@app.get("/")
def read_root():
    return {"status": "Movie Finder Bot is running 24/7 🚀"}

@app.post(f"/{BOT_TOKEN}")
async def process_webhook(request: Request):
    json_string = await request.json()
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return {"status": "ok"}

# သတ်မှတ်မိနစ်ပြည့်ရင် Message ကို အလိုအလျောက် ဖျက်ပေးမည့် စနစ်
def delete_message_safe(chat_id, message_id):
    try:
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(f"Error deleting message: {e}")

@bot.message_handler(func=lambda message: message.text is not None)
def handle_incoming_messages(message):
    # ⚠️ ချက်တင်ထဲ သီးသန့်လာပြောရင် စာမပြန်ပါနဲ့ (Group ထဲကစာပဲ ဖြစ်ရမည်)
    if message.chat.id != GROUP_ID:
        return

    text = message.text.strip()
    match = MOVIE_REGEX.search(text)
    
    # ⚠️ ရုပ်ရှင်နာမည်နဲ့ ခုနှစ် မပါရင် လုံးဝ စာမပြန်ပါနဲ့
    if not match:
        return

    # ရိုက်လိုက်တဲ့ စာထဲကနေ ရုပ်ရှင်နာမည်နဲ့ ခုနှစ်ကို သန့်စင်ပြီး ထုတ်ယူခြင်း
    movie_name = match.group("name").strip().lower()
    movie_year = match.group("year").strip()

    # ဟာကွက်မရှိအောင် စာတိုပါတဲ့ စကားလုံးတွေကို ဖယ်ထုတ်ခြင်း (eg. "ကြည့်ချင်တယ်"၊ "ကို")
    movie_name = re.sub(r"\b(ကို|ကြည့်ချင်တယ်|ရှာပေး|ကြည့်ချင်လို့|want to watch)\b", "", movie_name).strip()

    # Function ၁ - ရှာဖွေနေဆဲ ပြန်စာပို့ခြင်း (၅ စက္ကန့်နေရင် ပျက်မည်)
    try:
        searching_msg = bot.reply_to(message, "ခနလေးနော် ... 💗 တောင်းဆိုထားတဲ့ movie ကိုရှာဖွေနေပါတယ် ... 🎬‼️")
        threading.Timer(5, delete_message_safe, args=[GROUP_ID, searching_msg.message_id]).start()
    except Exception as e:
        print(f"Error sending searching message: {e}")

    # Function ၂ - Channel ထဲက ရုပ်ရှင်တင်ထားသမျှ Post အကုန်လုံးကို Scan ဖတ်ရှာဖွေခြင်း
    movie_found = False
    target_message_id = None

    try:
        # Channel ထဲက အရင်ကကော အခုကော နောက်တင်မယ့် Post တွေကို စကန်ဖတ်ရန် (နောက်ဆုံး Post ၃၀၀ အထိ ရှာပေးမည်)
        channel_posts = bot.get_chat_history(CHANNEL_ID, limit=300)
        
        for post in channel_posts:
            post_text = post.text or post.caption
            if post_text:
                post_text_lower = post_text.lower()
                # နာမည်ရော ခုနှစ်ရော ကိုက်ညီမှု ရှိမရှိ စစ်ဆေးခြင်း
                if movie_name in post_text_lower and movie_year in post_text_lower:
                    target_message_id = post.message_id
                    movie_found = True
                    break
    except Exception as e:
        print(f"Error scanning channel: {e}")

    # ရုပ်ရှင်တွေ့ရှိပါက လုပ်ဆောင်မည့်စနစ်
    if movie_found and target_message_id:
        try:
            # ရုပ်ရှင် Post ကို Group ထဲသို့ Forward ဆွဲတင်ပေးခြင်း
            forwarded_movie = bot.forward_message(chat_id=GROUP_ID, from_chat_id=CHANNEL_ID, message_id=target_message_id)
            
            # သတိပေးစာကို ရုပ်ရှင်တောင်းတဲ့သူကို Reply ပြန်ပြီး တစ်ခါတည်း ပို့ပေးခြင်း
            alert_msg = bot.reply_to(message, "movie finder bot 🔎 ပို့ထားတဲ့ post က ၅ မိနစ်နေရင် အလိုလိုပျက်ပါမယ်နော်🍿🎬 ... ‼️")
            
            # မိနစ်ဝက် (၃၀၀ စက္ကန့် = ၅ မိနစ်) ပြည့်ပါက ရုပ်ရှင် Post ရော သတိပေးစာပါ အလိုအလျောက် ပြန်ဖျက်ခြင်း
            threading.Timer(300, delete_message_safe, args=[GROUP_ID, forwarded_movie.message_id]).start()
            threading.Timer(300, delete_message_safe, args=[GROUP_ID, alert_msg.message_id]).start()
            
        except Exception as e:
            print(f"Error handling movie forward: {e}")

    # ရုပ်ရှင်မတွေ့ရှိပါက "Admin တွေတင်ပေးနေပါတယ်" ဟု Reply ပြန်ခြင်း (၅ မိနစ်နေရင် ပ
    

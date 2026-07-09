import re
import time
import random
import threading
import telebot

BOT_TOKEN = '8986003372:AAGw_hR1vFzbWfJbhjj_kaYCyY2fTzrwFbw'  # သင့် Bot Token အမှန်ကို ဤနေရာတွင် ထည့်ပါ
bot = telebot.TeleBot(BOT_TOKEN)

# Movie တွေကို ယာယီမှတ်ထားမယ့် Database Dictionary
movie_database = {}

# စိတ်ချရဆုံး အခြေခံ Emoji များ
REACTION_EMOJIS = ["👍", "❤️", "🔥", "🎉", "🤩", "👏"]

# အချိန်ပြည့်ရင် စာကို အလိုအလျောက် ဖျက်ပေးမယ့် Function
def auto_delete_message(chat_id, message_id, delay):
    time.sleep(delay)
    try:
        bot.delete_message(chat_id, message_id)
        print(f"Deleted message {message_id} from chat {chat_id}")
    except Exception as e:
        print(f"Failed to delete message: {e}")

# စာသားထဲက ရုပ်ရှင်နာမည်နဲ့ ခုနှစ်ကို ဖြတ်ထုတ်ပေးမယ့် Function
def extract_movie_info(text):
    if not text:
        return None
    match = re.search(r'([a-zA-Z0-9\s\-\:\.]+)\s*\(?(\d{4})\)?', text)
    if match:
        movie_name = match.group(1).strip().lower()
        year = match.group(2)
        return f"{movie_name} {year}"
    return None

# ၁။ Private Channel (Movie Database) ထဲမှာ ရုပ်ရှင်တင်လိုက်ရင် ဖမ်းယူသိမ်းဆည်းမယ့်စနစ်
@bot.channel_post_handler(content_types=['text', 'photo', 'video', 'document'])
def save_movies_from_channel(message):
    text = message.text or message.caption
    movie_key = extract_movie_info(text)
    
    if movie_key:
        movie_database[movie_key] = {
            "chat_id": message.chat.id,
            "message_id": message.message_id
        }
        print(f"🎬 [DATABASE SUCCESS] Saved Movie: {movie_key.title()}")

# ၂။ Request Group ထဲက တောင်းဆိုမှုများကို စစ်ဆေးပြီး ပြန်လည်ပေးပို့ခြင်း
@bot.message_handler(func=lambda message: message.chat.type in ['group', 'supergroup'])
def handle_movie_request(message):
    if not message.text:
        return

    req_key = extract_movie_info(message.text)
    if not req_key:
        return

    # A. User ရဲ့ စာကို Reaction ပေးခြင်း (Error လုံးဝမတက်စေမယ့် ကုဒ်စနစ်ရိုးရိုး)
    try:
        chosen_emoji = random.choice(REACTION_EMOJIS)
        # Dictionary အစား string နဲ့ တိုက်ရိုက်ပစ်ပေးတဲ့ ပုံစံပြောင်းလိုက်ပါတယ်
        bot.set_message_reaction(
            chat_id=message.chat.id,
            message_id=message.message_id,
            reaction=[{"type": "emoji", "emoji": chosen_emoji}]
        )
    except Exception as e:
        print(f"Reaction Skip (API Restrict): {e}")

    # B. "ခနလေးနော်🫡 ရှာ‌ဖွေနေတယ်🔎" ဟု Reply အရင်ပြန်ခြင်း
    try:
        searching_msg = bot.reply_to(message, "ခနလေးနော်🫡 ရှာ‌ဖွေနေတယ်🔎")
    except Exception as e:
        print(f"Reply Error: {e}")
        return

    # C. ၅ စက္ကန့် စောင့်ဆိုင်းခြင်း
    time.sleep(5)

    # D. "ရှာဖွေနေတယ်" စာကို ပြန်ဖျက်ခြင်း
    try:
        bot.delete_message(message.chat.id, searching_msg.message_id)
    except Exception as e:
        print(f"Delete Searching Msg Error: {e}")

    # E. Database ထဲမှာ ရုပ်ရှင် ရှာဖွေခြင်း
    found = False
    for saved_key, movie_info in movie_database.items():
        if req_key in saved_key:
            try:
                # ရုပ်ရှင် Post ကို Forward လုပ်ပေးမယ်
                sent_msg = bot.forward_message(
                    chat_id=message.chat.id,
                    from_chat_id=movie_info["chat_id"],
                    message_id=movie_info["message_id"]
                )
                found = True
                
                # ပို့ပေးလိုက်တဲ့ ရုပ်ရှင် Post ကို ၅ မိနစ် (စက္ကန့် ၃၀၀) နေရင် အလိုအလျောက် ပြန်ဖျက်မယ်
                threading.Thread(
                    target=auto_delete_message, 
                    args=(message.chat.id, sent_msg.message_id, 300)
                ).start()
                break
            except Exception as e:
                print(f"Error forwarding: {e}")
    
    # F. ရှာမတွေ့ခဲ့ရင် ပြန်မယ့် စာသား
    if not found:
        reply_msg = bot.reply_to(message, "ခနစောင့်ပေးပါ🎬🍿 group admin တွေက movie upload နေပါတယ်... ⭐")
        
        # အဲဒီစာသားကိုပါ ၅ မိနစ် (စက္ကန့် ၃၀၀) နေရင် ပြန်ဖျက်ပေးမယ်
        threading.Thread(
                    target=auto_delete_message, 
                    args=(message.chat.id, reply_msg.message_id, 300)
                ).start()

print("MOVIE BOX group helper (Strict Stability Fixed) is running...")
bot.infinity_polling()

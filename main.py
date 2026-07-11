import os, time, threading, random, telebot
from flask import Flask
from waitress import serve

# Configuration
BOT_TOKEN = '8862915293:AAG5ZnaDdg2IDKX-LdM5AtOqENTzAQ-coDQ'
GROUP_ID = -1003906056351
CHANNEL_ID = -1004438806546 
bot = telebot.TeleBot(BOT_TOKEN)

# Web Server (Render 24/7 Run နေစေရန်)
app = Flask('')
@app.route('/')
def home(): return "Bot is Alive!"

def delete_msg(chat_id, message_id, delay):
    time.sleep(delay)
    try: bot.delete_message(chat_id, message_id)
    except: pass

def search_in_channel(query):
    # Channel ထဲက message များကို ရှာဖွေခြင်း
    try:
        messages = bot.get_chat_history(CHANNEL_ID, limit=100)
        for msg in messages:
            if msg.caption and query.lower() in msg.caption.lower():
                return msg.message_id
    except Exception as e:
        print(f"Error searching channel: {e}")
    return None

@bot.message_handler(func=lambda message: True)
def handle_requests(message):
    if message.chat.id != GROUP_ID: return 
    
    text = message.text.lower()
    # Movie name + Year ပုံစံပါမှသာ စာပြန်ပါ
    if "ကြည့်ချင်တယ်" in text and any(char.isdigit() for char in text):
        msg = bot.reply_to(message, "ခနလေးနော် ... 💗 တောင်းဆိုထားတဲ့ movie ကိုရှာဖွေနေပါတယ် ... 🎬‼️")
        threading.Thread(target=delete_msg, args=(GROUP_ID, msg.message_id, 5), daemon=True).start()
        
        post_id = search_in_channel(text)
        if post_id:
            bot.forward_message(GROUP_ID, CHANNEL_ID, post_id)
        else:
            warn = bot.reply_to(message, "ခနစောင့်ပေးပါ🎬🍿 group admin တွေက movie upload နေပါတယ်... ⭐")
            threading.Thread(target=delete_msg, args=(GROUP_ID, warn.message_id, 300), daemon=True).start()

def hourly_task():
    messages = ["ပျင်းနေပြီလား ?", "စော်ရှိလား ?", "ဘယ်ရုပ်ရှင်ကြည့်ချင်ပါလဲ ?", "အရမ်းချစ်တယ် ထားမသွားဘူးနော် 🥺", "အာဘွားပေး 🥺💗", "ဒီနေ့ ဘယ်ရုပ်ရှင်တွေကြည့်ရင်ကောင်းမလဲ ?"]
    while True:
        try:
            msg = bot.send_message(GROUP_ID, random.choice(messages))
            threading.Thread(target=delete_msg, args=(GROUP_ID, msg.message_id, 2700), daemon=True).start()
        except: pass
        time.sleep(3600)

if __name__ == "__main__":
    # Webhook Conflict မဖြစ်အောင် Webhook အဟောင်းကို ဖြုတ်ပေးပါ
    bot.remove_webhook()
    
    threading.Thread(target=lambda: serve(app, host='0.0.0.0', port=8080), daemon=True).start()
    threading.Thread(target=hourly_task, daemon=True).start()
    print("Bot စတင်နေပါပြီ...")
    bot.infinity_polling(none_stop=True)

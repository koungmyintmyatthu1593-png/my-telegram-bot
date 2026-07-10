import os
import time
from threading import Thread
from flask import Flask
import telebot

# =======================================================
# ၁။ Render အတွက် Web Server (Flask) တည်ဆောက်ခြင်း
# =======================================================
app = Flask('')

@app.route('/')
def home():
    return "MOVIE BOX Helper Bot Is Running Alive!"

# --- တစ်နာရီတစ်ခါ စာလှမ်းပို့ပေးမည့် လမ်းကြောင်းအသစ် ---
@app.route('/send-hourly')
def send_hourly():
    try:
        # သင့် Group ID (-1003906056351) ထဲကို စာလှမ်းပို့ခြင်း
        bot.send_message(-1003906056351, "ဒီနေ့ညအတွက် ဘာကားကြည့်ရမလဲ စဉ်းစားရခက်နေလား? 🍿🎬 Group ထဲမှာ ကိုယ်ကြည့်ချင်တဲ့ ရုပ်ရှင်နာမည်လေးတွေ ရိုက်ရှာပြီး MOVIE BOX မှာ အပန်းဖြေလိုက်ပါနော်။")
        return "Message sent successfully!", 200
    except Exception as e:
        return f"Error: {e}", 500

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# =======================================================
# ၂။ Telegram Bot Setup (သင့် Token ကို ဒီမှာ သေჩာထည့်ပါ)
# =======================================================
BOT_TOKEN = '8687343780:AAEEEGqXQNLz-43fcqBRnlmxb88kCOwD4G4'
bot = telebot.TeleBot(BOT_TOKEN)

# =======================================================
# ၃။ သင့် Bot ရဲ့ Functions များ
# =======================================================
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, "မင်္ဂလာပါ! MOVIE BOX Bot အဆင်သင့်ရှိနေပါပြီဗျာ။")

# =======================================================
# ၄။ Bot Error Handling Polling Loop
# =======================================================
def bot_polling():
    while True:
        try:
            print("Bot Polling စတင်နေပါပြီ...")
            bot.polling(none_stop=True, timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Error တက်သွားသဖြင့် ၅ စက္ကန့်အကြာတွင် ပြန်စပါမည်: {e}")
            time.sleep(5)

# =======================================================
# ၅။ Main Program Run ခြင်း
# =======================================================
if __name__ == "__main__":
    server_thread = Thread(target=run_flask)
    server_thread.start()
    
    bot_polling()

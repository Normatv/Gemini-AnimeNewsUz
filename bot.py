import os
import requests
import telebot
from google import genai
import random
from threading import Thread
from flask import Flask

# Render tekin tarifda portni tekshirgani uchun kichkina soxta veb-server yaratamiz
app = Flask('')

@app.route('/')
def home():
    return "Bot tirik va ishlayapti!"

def run():
    # Render avtomatik beradigan portni o'qiymiz, topilmasa 8080
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# ⚠️ KALITLARNI SHU YERGA TO'G'RIDAN-TO'G'RI QO'SHTIRNOQ ICHIGA YOZING:
BOT_TOKEN = "8979366912:AAG9mFcie-ZgpTIEGLOwg3UiWGSItxuNE38"
GEMINI_API_KEY = "AQ.Ab8RN6IajUIAILprzriwqPN-5rIHuCIt9zcqnz06kq0QKEuCKA"

bot = telebot.TeleBot(BOT_TOKEN)

# Google-ning eng so'nggi rasmiy standartida Client yaratamiz
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Gemini sozlashda xatolik: {e}")
    client = None

@bot.message_handler(commands=['start'])
def start_command(message):
    chat_id = message.chat.id
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton("🎬 Yangilik olish"))
    
    bot.send_message(
        chat_id, 
        f"Salom! Men Gemini bilan ishlaydigan Anime botman.\n\n"
        f"Pastdagi 'Yangilik olish' tugmasini bossangiz, men sizga eng so'nggi anime yangiliklarini tasodifiy tartibda o'zbekcha qilib beraman!", 
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == "🎬 Yangilik olish")
def send_anime_news(message):
    bot.reply_to(message, "⏳ Eng so'nggi anime yangiligini qidiryapman va Gemini orqali tarjima qilyapman, kuting...")
    
    try:
        url = "https://api.jikan.moe/v4/watch/episodes"
        res = requests.get(url, timeout=10)
        
        if res.status_code == 200:
            data = res.json()
            if data and 'data' in data and len(data['data']) > 0:
                # Ro'yxat ichidan tasodifiy (random) bittasini tanlaymiz
                latest = random.choice(data['data'])
                anime_name = latest['entry']['title']
                episode_title = latest['episodes'][0]['title'] if latest['episodes'] else "Yangi qism"
                full_title = f"{anime_name} - {episode_title}"
                
                # Eng so'nggi va barqaror gemini-2.5-flash modelidan foydalanamiz
                if client:
                    prompt = f"Ushbu anime yangiligini o'zbek tilida juda qiziqarli, qisqa va emojilar bilan tushuntirib ber: {full_title}"
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt,
                    )
                    uzbek_news = response.text
                else:
                    uzbek_news = f"🎬 Yangi epizod chiqdi:\n📌 Anime: {anime_name}\n📺 Qism: {episode_title}"
                
                bot.send_message(message.chat.id, uzbek_news)
            else:
                bot.send_message(message.chat.id, "❌ Hozircha yangi ma'lumot topilmadi.")
        else:
            bot.send_message(message.chat.id, "❌ Anime bazasidan ma'lumot olishda xatolik yuz berdi.")
            
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Xatolik yuz berdi: {str(e)}")

if __name__ == "__main__":
    # Veb-serverni alohida oqimda (thread) ishga tushiramiz, Render tinchlanishi uchun
    server_thread = Thread(target=run)
    server_thread.start()
    
    print("Bot muvaffaqiyatli ishga tushdi!")
    bot.infinity_polling()

import os
import requests
import telebot
from google import genai

# Kalitlarni Render tizimidan o'qiymiz
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

# Google-ning eng so'nggi standartiga ko'ra Client sozlaymiz
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Gemini Client ulashda xatolik: {e}")
    client = None

@bot.message_handler(commands=['start'])
def start_command(message):
    chat_id = message.chat.id
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton("🎬 Yangilik olish"))
    
    bot.send_message(
        chat_id, 
        f"Salom! Men Gemini bilan ishlaydigan Anime botman.\n\n"
        f"Sizning Chat ID raqamingiz: `{chat_id}`\n\n"
        f"Pastdagi 'Yangilik olish' tugmasini bossangiz, men hozirgina chiqqan eng oxirgi anime qismini tarjima qilib beraman!", 
        parse_mode="Markdown",
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
                latest = data['data'][0]
                anime_name = latest['entry']['title']
                episode_title = latest['episodes'][0]['title'] if latest['episodes'] else "Yangi qism"
                full_title = f"{anime_name} - {episode_title}"
                
                # Eng so'nggi gemini-2.5-flash modeli orqali tarjima qilish
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
    print("Bot muvaffaqiyatli ishga tushdi!")
    bot.infinity_polling()

import os
import time
import requests
import telebot
from google import genai

# Kalitlarni tizim muhitidan (Environment Variables) o'qiymiz
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Bot va Gemini mijozini ishga tushiramiz
bot = telebot.TeleBot(BOT_TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY)

# Oxirgi yuborilgan yangilik ID sini saqlash uchun o'zgaruvchi
last_news_id = None

def get_latest_anime_news():
    """Jikan API orqali so'nggi anime yangiliklarini olish"""
    try:
        # MyAnimeList bazasidan so'nggi yangiliklarni so'raymiz
        url = "https://api.jikan.moe/v4/watch/episodes"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['data']:
                # Eng oxirgi chiqqan epizod/yangilik ma'lumotini olamiz
                latest = data['data'][0]
                return latest
    except Exception as e:
        print(f"Yangilik olishda xatolik: {e}")
    return None

def translate_and_summarize_with_gemini(news_title):
    """Gemini orqali yangilikni o'zbek tiliga chiroyli o'girish"""
    try:
        prompt = (
            f"Sen anime olami bo'yicha ekspertsan. Quyidagi anime yangiligini "
            f"o'zbek tilida juda qiziqarli, qisqa va jozibali qilib tushuntirib ber. "
            f"Emojilardan foydalan. Yangilik: {news_title}"
        )
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"Gemini bilan ishlashda xatolik: {e}")
        return f"🎬 Yangi anime yangiligi chiqdi: {news_title}"

@bot.message_handler(commands=['start'])
def start_command(message):
    """Foydalanuvchi /start bosganda ishlaydi"""
    chat_id = message.chat.id
    bot.reply_to(message, f"Salom! Men Gemini bilan ishlaydigan Anime Yangiliklar botiman. "
                          f"Sizning Chat ID raqamingiz: `{chat_id}`\n\n"
                          f"Ushbu ID raqamni nusxalab menga (Gemini-ga) yuboring, "
                          f"uni serverga sozlaymiz!", parse_mode="Markdown")

def check_news_loop(chat_id):
    """Har 10 daqiqada yangiliklarni tekshirib turadigan funksiya"""
    global last_news_id
    print("Yangiliklarni kuzatish boshlandi...")
    
    while True:
        news = get_latest_anime_news()
        if news:
            # Agar bu yangilik tizimga yangi bo'lsa
            news_id = news['entry']['mal_id']
            if news_id != last_news_id:
                last_news_id = news_id
                anime_name = news['entry']['title']
                episode_title = news['episodes'][0]['title'] if news['episodes'] else "Yangi qism"
                
                full_title = f"{anime_name} - {episode_title}"
                
                # Gemini'ga tarjima qildiramiz
                uzbek_news = translate_and_summarize_with_gemini(full_title)
                
                # Foydalanuvchiga yuboramiz
                bot.send_message(chat_id, uzbek_news)
        
        # 10 daqiqa (600 soniya) kutish
        time.sleep(600)

if __name__ == "__main__":
    # Botni ishga tushirish (Render'da ishlashi uchun buni alohida boshqaramiz)
    print("Bot muvaffaqiyatli sozlangan. Endi Render-ga ulaymiz!")


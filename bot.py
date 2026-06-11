import telebot
import yt_dlp
import os

BOT_TOKEN = "8608901124:AAEVd3ijNRQw2rLvzyIFXp8NUj-T65G-Tzc"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Salom! Men endi yanada kuchliroqman. Video havolasini yuboring!")

@bot.message_handler(func=lambda message: message.text.startswith('http'))
def download(message):
    url = message.text.split('?')[0] # Havolani tozalash
    msg = bot.reply_to(message, "⏳ Videoni yuklab olyapman, biroz kuting...")
    
    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'video.mp4',
            'quiet': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        bot.send_video(message.chat.id, open('video.mp4', 'rb'))
        bot.delete_message(message.chat.id, msg.message_id)
        os.remove('video.mp4') # Yuklab bo'lgach faylni o'chirish
    except Exception as e:
        bot.edit_message_text(f"❌ Xatolik: {e}", message.chat.id, msg.message_id)

bot.infinity_polling()

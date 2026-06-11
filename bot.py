import requests
import telebot

# ⚠️ BATINGIZ TOKENINI FAQAT SHU YERGA YOZING
BOT_TOKEN = "8608901124:AAEVd3ijNRQw2rLvzyIFXp8NUj-T65G-Tzc"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(
        message.chat.id,
        "👋 Salom! Men ijtimoiy tarmoqlardan video va rasm yuklovchi botman.\n\n"
        "Menga havola (link) yuboring, men uni yuklab beraman! 🚀"
    )

@bot.message_handler(func=lambda message: message.text.startswith(('http://', 'https://')))
def download_media(message):
    url = message.text.strip()
    
    # Instagram/TikTok havolalarini tozalash (so'roq belgisi va undan keyingisini olib tashlash)
    if "?" in url:
        url = url.split("?")[0]
        
    status_msg = bot.reply_to(message, "⏳ Havola tozalandi, yuklanmoqda...")

    api_url = "https://api.cobalt.tools/api/json"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "url": url,
        "vQuality": "720"
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            res_data = response.json()
            
            if "url" in res_data:
                media_url = res_data["url"]
                # Rasm yoki video ekanligini aniqlash
                if ".jpg" in media_url or ".png" in media_url:
                    bot.send_photo(message.chat.id, media_url, caption="✨ Yuklab olindi!")
                else:
                    bot.send_video(message.chat.id, media_url, caption="🎬 Yuklab olindi!")
            elif "picker" in res_data:
                for item in res_data["picker"]:
                    bot.send_document(message.chat.id, item["url"])
            else:
                bot.send_message(message.chat.id, "❌ Ushbu havoladan media topilmadi.")
                
            bot.delete_message(message.chat.id, status_msg.message_id)
        else:
            bot.edit_message_text("⚠️ API xatolik berdi. Havolani tekshiring.", message.chat.id, status_msg.message_id)
            
    except Exception as e:
        bot.edit_message_text(f"❌ Tizim xatosi: {str(e)}", message.chat.id, status_msg.message_id)

if __name__ == "__main__":
    print("Bot ishlamoqda...")
    bot.infinity_polling()

import requests
import telebot
import random

# ⚠️ BATINGIZ TOKENINI FAQAT SHU YERGA YOZING (Qo'shtirnoq ichiga)
BOT_TOKEN = "8608901124:AAEVd3ijNRQw2rLvzyIFXp8NUj-T65G-Tzc"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(
        message.chat.id,
        "👋 Salom! Men ijtimoiy tarmoqlardan video va rasm yuklovchi botman.\n\n"
        "Menga Instagram, TikTok, YouTube, Pinterest yoki boshqa platforma havola (link) yuboring, men uni sizga yuklab beraman! 🚀"
    )

@bot.message_handler(func=lambda message: message.text.startswith(('http://', 'https://')))
def download_media(message):
    url = message.text.strip()
    status_msg = bot.reply_to(message, "⏳ Havola tekshirilmoqda va yuklanmoqda, kuting...")

    # Universal va bepul yuklovchi API manzili (Cobalt API)
    api_url = "https://api.cobalt.tools/api/json"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "url": url,
        "vQuality": "720" # Videolar sifati (720p)
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            res_data = response.json()
            
            # 1-Holat: Agar bu bitta video yoki rasm bo'lsa
            if "url" in res_data:
                media_url = res_data["url"]
                
                # Agar havola rasm bo'lsa (masalan Pinterest yoki rasm linki)
                if "picker" in url or ".jpg" in media_url or ".png" in media_url:
                    bot.send_photo(message.chat.id, media_url, caption="✨ Yuklab olindi!")
                else: # Video bo'lsa (Instagram Reel, TikTok, Shorts)
                    bot.send_video(message.chat.id, media_url, caption="🎬 Yuklab olindi!")
                    
            # 2-Holat: Agar Instagram karusel (bir nechta rasm/video) bo'lsa
            elif "picker" in res_data:
                for item in res_data["picker"]:
                    bot.send_document(message.chat.id, item["url"])
            else:
                bot.send_message(message.chat.id, "❌ Ushbu havoladan media topilmadi.")
                
            # "Kutilmoqda..." degan xabarni o'chirib tashlaymiz
            bot.delete_message(message.chat.id, status_msg.message_id)
            
        else:
            bot.edit_message_text("⚠️ Yuklashda xatolik yuz berdi. Havolani tekshirib qayta yuboring.", message.chat.id, status_msg.message_id)
            
    except Exception as e:
        bot.edit_message_text(f"❌ Tizimda xatolik: {str(e)}", message.chat.id, status_msg.message_id)

if __name__ == "__main__":
    print("Bot muvaffaqiyatli ishga tushdi...")
    bot.infinity_polling()

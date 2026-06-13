import requests
import telebot

# 🤖 Siz taqdim etgan Telegram Bot Token (O'zim joylashtirdim)
BOT_TOKEN = "8608901124:AAEVd3ijNRQw2rLvzyIFXp8NUj-T65G-Tzc"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(
        message.chat.id,
        "👋 Salom Elchinbek! Men ijtimoiy tarmoqlardan video yuklovchi universal botman.\n\n"
        "Menga Instagram, TikTok yoki YouTube Shorts havolasini yuboring, yuklab berishga harakat qilaman! 🚀"
    )

@bot.message_handler(func=lambda message: message.text.startswith(('http://', 'https://')))
def download_media(message):
    url = message.text.strip()
    
    # Havolani ortiqcha kuzatuv kodlaridan tozalash (?igsh=... qismini olib tashlash)
    if "?" in url:
        url = url.split("?")[0]
        
    status_msg = bot.reply_to(message, "⏳ Tizim ulanmoqda, iltimos kuting...")

    # Cobalt API xizmatining eng faol 3 ta rasmiy server manzili (Bittasi band bo'lsa, keyingisiga o'tadi)
    cobalt_servers = [
        "https://api.cobalt.tools/api/json",
        "https://cobalt.api.toxic.biz.id/api/json",
        "https://api.v03.api-toxic.biz.id/api/json"
    ]
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "url": url,
        "vQuality": "720"
    }

    media_sent = False

    # Serverlarni ketma-ket tekshirish zanjiri
    for server in cobalt_servers:
        try:
            response = requests.post(server, json=payload, headers=headers, timeout=15)
            
            if response.status_code == 200:
                res_data = response.json()
                
                # 1-Holat: To'g'ridan-to'g'ri bitta video yoki rasm havolasi kelsa
                if "url" in res_data:
                    media_url = res_data["url"]
                    if ".jpg" in media_url or ".png" in media_url:
                        bot.send_photo(message.chat.id, media_url, caption="✨ Rasm yuklab olindi!")
                    else:
                        bot.send_video(message.chat.id, media_url, caption="🎬 Video yuklab olindi!")
                    media_sent = True
                    break # Agar video muvaffaqiyatli jo'natilsa, sikldan chiqib ketadi
                    
                # 2-Holat: Instagram karusel (bir nechta media) kelsa
                elif "picker" in res_data:
                    for item in res_data["picker"]:
                        bot.send_document(message.chat.id, item["url"])
                    media_sent = True
                    break
        except Exception:
            continue # Agar ushbu serverda xatolik bo'lsa, keyingi muqobil serverga o'tadi

    # Natija tekshiruvi
    if media_sent:
        try:
            bot.delete_message(message.chat.id, status_msg.message_id)
        except Exception:
            pass
    else:
        bot.edit_message_text(
            "⚠️ Hozirda barcha yuklovchi serverlar band yoki Instagram xavfsizlik tizimi havolani blokladi.\n\n"
            "Iltimos, birozdan so'ng qayta urinib ko'ring yoki boshqa havola yuboring.", 
            message.chat.id, 
            status_msg.message_id
        )

if __name__ == "__main__":
    print("Bot yangi token bilan ishga tushdi...")
    bot.infinity_polling()

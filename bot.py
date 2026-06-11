import requests
import telebot

# ⚠️ BATINGIZ TOKENINI FAQAT SHU YERGA YOZING
BOT_TOKEN = "8608901124:AAEVd3ijNRQw2rLvzyIFXp8NUj-T65G-Tzc"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(
        message.chat.id,
        "👋 Salom! Men ijtimoiy tarmoqlardan video yuklovchi tezyurar botman.\n\n"
        "Menga Instagram, TikTok yoki YouTube va boshqa platformalardan havola yuboring! 🚀"
    )

@bot.message_handler(func=lambda message: message.text.startswith(('http://', 'https://')))
def download_media(message):
    url = message.text.strip()
    
    # Havolani tozalash
    if "?" in url:
        url = url.split("?")[0]
        
    status_msg = bot.reply_to(message, "⚡️ Tezkor tizim ulanmoqda, kuting...")

    # Dunyodagi eng barqaror va ochiq yuklovchi API'lardan biri
    api_url = "https://api.v03.api-toxic.biz.id/api/downloader/universal"
    params = {
        "url": url
    }

    try:
        response = requests.get(api_url, params=params, timeout=25)
        
        if response.status_code == 200:
            res_data = response.json()
            
            # API muvaffaqiyatli ishlasa va natija qaytarsa
            if res_data.get("status") == True and "result" in res_data:
                result = res_data["result"]
                
                # Agar video bo'lsa
                if "url" in result:
                    video_url = result["url"]
                    bot.send_video(message.chat.id, video_url, caption="🎬 Mana videongiz!")
                    bot.delete_message(message.chat.id, status_msg.message_id)
                # Ba'zi variantlarda "hd" yoki "mp4" formatda keladi
                elif "hd" in result:
                    bot.send_video(message.chat.id, result["hd"], caption="🎬 Mana videongiz (HD)!")
                    bot.delete_message(message.chat.id, status_msg.message_id)
                else:
                    bot.edit_message_text("⚠️ Videoni yuklab bo'lmadi. Tizim havolani tushunmadi.", message.chat.id, status_msg.message_id)
            else:
                bot.edit_message_text("⚠️ Havola tekshirildi, lekin undan video topilmadi.", message.chat.id, status_msg.message_id)
        else:
            bot.edit_message_text("⚠️ Tashqi server hozir band. Birozdan so'ng qayta urinib ko'ring.", message.chat.id, status_msg.message_id)
            
    except Exception as e:
        bot.edit_message_text(f"❌ Tarmoq xatosi: {str(e)}", message.chat.id, status_msg.message_id)

if __name__ == "__main__":
    bot.infinity_polling()

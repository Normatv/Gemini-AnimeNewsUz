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

# Zaxira (Alternativ) API orqali yuklash funksiyasi
def download_via_backup_api(url):
    # Bu API Instagram, TikTok va YouTube uchun juda barqaror ishlaydi
    backup_api = f"https://api.dreadful-dev.workers.dev/download?url={url}"
    try:
        res = requests.get(backup_api, timeout=30)
        if res.status_code == 200:
            data = res.json()
            if data.get("status") == "success" and "url" in data:
                return data["url"]
    except Exception:
        return None
    return None

@bot.message_handler(func=lambda message: message.text.startswith(('http://', 'https://')))
def download_media(message):
    url = message.text.strip()
    
    # Havolalarni tozalash
    if "?" in url:
        url = url.split("?")[0]
        
    status_msg = bot.reply_to(message, "⏳ Havola tekshirilmoqda, yuklanyapti...")

    # 1-URANISH: Asosiy Cobalt API
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
        response = requests.post(api_url, json=payload, headers=headers, timeout=20)
        
        if response.status_code == 200:
            res_data = response.json()
            if "url" in res_data:
                bot.send_video(message.chat.id, res_data["url"], caption="🎬 Yuklab olindi! (Asosiy tizim)")
                bot.delete_message(message.chat.id, status_msg.message_id)
                return
            elif "picker" in res_data:
                for item in res_data["picker"]:
                    bot.send_document(message.chat.id, item["url"])
                bot.delete_message(message.chat.id, status_msg.message_id)
                return

        # Agar asosiy API xato bersa, avtomatik zaxira API'ga o'tadi:
        bot.edit_message_text("🔄 Asosiy tizim band. Zaxira tizim ishga tushirildi, kuting...", message.chat.id, status_msg.message_id)
        backup_url = download_via_backup_api(url)
        
        if backup_url:
            bot.send_video(message.chat.id, backup_url, caption="🎬 Yuklab olindi! (Zaxira tizim)")
            bot.delete_message(message.chat.id, status_msg.message_id)
        else:
            bot.edit_message_text("⚠️ Kechirasiz, har ikkala tizim ham havolani yuklay olmadi. Havola noto'g'ri yoki serverlar band.", message.chat.id, status_msg.message_id)
            
    except Exception as e:
        # Xatolik bo'lsa ham zaxira API'ni tekshirib ko'radi
        backup_url = download_via_backup_api(url)
        if backup_url:
            bot.send_video(message.chat.id, backup_url, caption="🎬 Yuklab olindi! (Zaxira tizim)")
            bot.delete_message(message.chat.id, status_msg.message_id)
        else:
            bot.edit_message_text(f"❌ Tizim xatosi yuz berdi: {str(e)}", message.chat.id, status_msg.message_id)

if __name__ == "__main__":
    print("Bot 2 ta API tizimi bilan ishga tushdi...")
    bot.infinity_polling()

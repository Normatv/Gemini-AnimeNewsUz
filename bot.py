import os
import requests
import telebot

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
raise ValueError("BOT_TOKEN topilmadi!")

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start_command(message):
bot.send_message(
message.chat.id,
"👋 Salom! Men ijtimoiy tarmoqlardan video va rasm yuklovchi botman.\n\n"
"Instagram, TikTok yoki YouTube Shorts havolasini yuboring."
)

@bot.message_handler(func=lambda message: message.text and message.text.startswith(("http://", "https://")))
def download_media(message):
url = message.text.strip()

if "?" in url:
    url = url.split("?")[0]

status_msg = bot.reply_to(message, "⏳ Yuklanmoqda...")

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

for server in cobalt_servers:
    try:
        response = requests.post(
            server,
            json=payload,
            headers=headers,
            timeout=15
        )

        if response.status_code != 200:
            continue

        data = response.json()

        if "url" in data:
            media_url = data["url"]

            if any(ext in media_url.lower() for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                bot.send_photo(
                    message.chat.id,
                    media_url,
                    caption="📷 Rasm yuklandi!"
                )
            else:
                bot.send_video(
                    message.chat.id,
                    media_url,
                    caption="🎬 Video yuklandi!"
                )

            media_sent = True
            break

        elif "picker" in data:
            for item in data["picker"]:
                bot.send_document(
                    message.chat.id,
                    item["url"]
                )

            media_sent = True
            break

    except Exception as e:
        print(f"Xatolik: {e}")
        continue

if media_sent:
    try:
        bot.delete_message(
            message.chat.id,
            status_msg.message_id
        )
    except Exception:
        pass
else:
    bot.edit_message_text(
        "⚠️ Yuklab bo'lmadi. Birozdan keyin qayta urinib ko'ring.",
        message.chat.id,
        status_msg.message_id
    )

@bot.message_handler(func=lambda m: True)
def unknown_message(message):
bot.reply_to(
message,
"📎 Instagram, TikTok yoki YouTube havolasini yuboring."
)

if name == "main":
print("Bot ishga tushdi...")
bot.infinity_polling(
timeout=30,
long_polling_timeout=30
)

import telebot
import re
import time
from datetime import datetime, date

API_TOKEN = "8398282467:AAHIuqj3mS3bx5M-w0N8-xuGqtmPrlZGGhg"
bot = telebot.TeleBot(API_TOKEN)

user_ads = {}
chat_seen_requests = {}

phone_pattern = re.compile(r'(\+?998[-\s]?\d{2}[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2})|(\b\d{2}[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2}\b)')

def is_ad_message(message):
    if message.text:
        text = message.text.lower()
        if phone_pattern.search(text):
            return False
        if "http://" in text or "https://" in text or "t.me" in text or re.search(r'@\w+', text):
            return True
        return False
    if message.photo or message.video or message.document or message.sticker or message.animation or message.voice or message.audio:
        return True
    return False

def categorize_request_text(text):
    if not text:
        return None
    t = text.lower()
    phone_words = r'\b(telefon|tel|raqam|nomer|raqamni|raqamingiz)\b'
    price_words = r'\b(pul|narx|narxi|qancha|necha|nechi|nech)\b'
    if re.search(phone_words, t) and re.search(r'\b(nechi|necha|qancha|nech)\b', t):
        return 'phone_request'
    if re.search(price_words, t) and re.search(r'\b(nechi|necha|qancha|nech)\b', t):
        return 'price_request'
    if re.search(r'nech\s+pul', t) or re.search(r'narx.?nech', t) or re.search(r'nech\s+so\'m', t):
        return 'price_request'
    return None

@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'sticker', 'animation', 'voice', 'audio'])
def handle_message(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    today = date.today()

    if chat_id not in user_ads:
        user_ads[chat_id] = {}
    if user_id not in user_ads[chat_id]:
        user_ads[chat_id][user_id] = {"date": today, "count": 0}
    if user_ads[chat_id][user_id]["date"] != today:
        user_ads[chat_id][user_id] = {"date": today, "count": 0}

    if chat_id not in chat_seen_requests:
        chat_seen_requests[chat_id] = {"date": today, "seen": set()}
    if chat_seen_requests[chat_id]["date"] != today:
        chat_seen_requests[chat_id] = {"date": today, "seen": set()}

    text = message.text or ""

    if is_ad_message(message):
        if user_ads[chat_id][user_id]["count"] == 0:
            user_ads[chat_id][user_id]["count"] = 1
            return
        try:
            bot.delete_message(chat_id, message.message_id)
        except:
            pass
        try:
            warn = bot.send_message(chat_id, f"{message.from_user.first_name}, siz bugun allaqachon reklama tashlagansiz ❌")
            time.sleep(5)
            bot.delete_message(warn.chat.id, warn.message_id)
        except:
            pass
        return

    category = categorize_request_text(text)
    if category:
        if category in chat_seen_requests[chat_id]["seen"]:
            try:
                bot.delete_message(chat_id, message.message_id)
            except:
                pass
            try:
                warn = bot.send_message(chat_id, f"{message.from_user.first_name}, shu xabar (so‘rov) guruhda allaqachon berilgan — takrorlash mumkin emas.")
                time.sleep(5)
                bot.delete_message(warn.chat.id, warn.message_id)
            except:
                pass
            return
        else:
            chat_seen_requests[chat_id]["seen"].add(category)
            return

if __name__ == "__main__":
    print("Bot ishga tushdi...")
    bot.polling(none_stop=True)

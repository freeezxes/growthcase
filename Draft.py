import telebot
from datetime import datetime, timedelta
import json
import os
import time
import emoji
import io 
from PIL import Image

token = "8233312730:AAHOntYbW-06ARjQnixi46ZE832SWGrwxVY"

bot = telebot.TeleBot(token)

chat_history = []
chat_history = []
media_folder = "media"
def emojize_text(text):
    """Конвертирует все эмодзи в :smiley: формат"""
    return emoji.demojize(text)

def save_and_export():
    one_hour_ago = datetime.now() - timedelta(hours=1)
    chat_history[:] = [msg for msg in chat_history if datetime.fromisoformat(msg["time"]) > one_hour_ago]

    with open("history.json", "w", encoding="utf-8") as f:
        json.dump(chat_history, f, ensure_ascii=False, indent=2)

# Обработка текстовых сообщений
@bot.message_handler(content_types=['text'])
def handle_text(message):
    entry = {
        "user_id": message.from_user.id,
        "username": message.from_user.username,
        "time": datetime.now().isoformat(),
        "type": "text",
        "text": emojize_text(message.text)
    }
    chat_history.append(entry)
    save_and_export()

# Обработка фото и стикеров
@bot.message_handler(content_types=['photo', 'sticker'])
def handle_media(message):
    entry = {
        "user_id": message.from_user.id,
        "username": message.from_user.username,
        "time": datetime.now().isoformat(),
    }
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    if message.content_type == "photo":
        entry["type"] = "photo"
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        filename = f"{media_folder}/photo_{timestamp}.jpg"
        with open(filename, "wb") as f:
            f.write(downloaded_file)
        entry["file"] = filename

    elif message.content_type == "sticker":
        entry["type"] = "sticker"
        entry["sticker_file_id"] = message.sticker.file_id
        entry["sticker_type"] = message.sticker.type

        file_info = bot.get_file(message.sticker.file_id)
        file_bytes = bot.download_file(file_info.file_path)

        if message.sticker.is_animated:
            filename = f"{media_folder}/sticker_{timestamp}.tgs"
            with open(filename, "wb") as f:
                f.write(file_bytes)
        else:
            try:
                image = Image.open(io.BytesIO(file_bytes))
                filename = f"{media_folder}/sticker_{timestamp}.png"
                image.save(filename, "PNG")
            except Exception as e:
                print(f"[ERROR] Не удалось конвертировать стикер: {e}")
                filename = f"{media_folder}/sticker_{timestamp}.webp"
                with open(filename, "wb") as f:
                    f.write(file_bytes)

        entry["file"] = filename

    chat_history.append(entry)
    save_and_export()

bot.polling()
import os
import telebot
from telebot import types


API_TOKEN = '8230538624:AAE93RQ4WluRSljZd7851JWpn1uZSJen1hY'
bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(content_types=['document'])
def handle_docs(message):
    # получаем file_id
    file_id = message.document.file_id

    # информация о файле
    file_info = bot.get_file(file_id)

    # скачиваем файл
    downloaded_file = bot.download_file(file_info.file_path)


    save_path = os.path.join("data", 'data.json')
    # например, сохранить файл
    with open(save_path, "wb") as new_file:
        new_file.write(downloaded_file)

    bot.reply_to(message, "Файл получен!")

@bot.message_handler(commands=['start'])
def start(message):
    web_app = types.WebAppInfo(url="https://acea3d9fe53b.ngrok-free.app")  # ссылка на ваш Web App
    btn = types.MenuButtonWebApp("web_app", text="Открыть WebApp", web_app=web_app)
    
    bot.set_chat_menu_button(chat_id=None, menu_button=btn)

bot.infinity_polling(5)

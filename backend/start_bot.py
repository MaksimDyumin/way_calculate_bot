import os
import telebot
from telebot import types
from dotenv import load_dotenv
import requests


load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")


bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(content_types=['document'])
def handle_docs(message):
    # получаем file_id
    file_id = message.document.file_id

    # информация о файле
    file_info = bot.get_file(file_id)

    # скачиваем файл
    downloaded_file = bot.download_file(file_info.file_path)
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url='http://127.0.0.1:5000/import', data=downloaded_file, headers=headers, timeout=30)
    # if response.status_code == ''

    bot.reply_to(message, "Файл получен!")

@bot.message_handler(commands=['start'])
def start(message):
    web_app = types.WebAppInfo(url="https://acea3d9fe53b.ngrok-free.app")  # ссылка на ваш Web App
    btn = types.MenuButtonWebApp("web_app", text="Открыть WebApp", web_app=web_app)
    
    bot.set_chat_menu_button(chat_id=None, menu_button=btn)
    bot.send_message(message.chat.id, "Добро пожаловать! Нажмите на кнопку ниже, чтобы открыть WebApp.")

bot.infinity_polling(5)

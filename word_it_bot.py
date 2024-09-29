import os
from pprint import pprint
import telebot
import httplib2
from googleapiclient.discovery import build
from dotenv import load_dotenv
from telebot import types
from oauth2client.service_account import ServiceAccountCredentials


# load_dotenv()
# bot_token = os.getenv("TOKEN")
# bot = telebot.TeleBot(bot_token)



# # Handle all other messages with content_type 'text' (content_types defaults to ['text'])
# @bot.message_handler(commands=['button'])
# def button(message):
#     markup = types.InlineKeyboardMarkup(row_width=2)
#     item1 = types.InlineKeyboardButton('Как дела?', callback_data="question_1")
#     item2 = types.InlineKeyboardButton('Пока', callback_data="goodbuy")
#     markup.add(item1, item2)
    
#     bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

# @bot.message_handler(content_types=['document'])
# def excel(message):
#     bot.send_message(message.chat.id, "Принято! Мы обрабатываем вашу заявку.")


# bot.polling(non_stop=True)
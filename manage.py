import os
from dotenv import load_dotenv
import telebot
from bot_modules import new_group_handler, attendance_log_handler, find_students_handler

load_dotenv()
bot_token = os.getenv("TOKEN")
chat_id = os.getenv("CHAT_ID")
bot = telebot.TeleBot(bot_token)

# Обработчик команды /start для показа клавиатуры
@bot.message_handler(commands=['start'])
def buttons(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item1 = telebot.types.KeyboardButton('New group')
    item2 = telebot.types.KeyboardButton('Attendance log')
    item3 = telebot.types.KeyboardButton('Find student')


    markup.add(item1, item2, item3)
    bot.send_message(message.chat.id, 
        "Welcome to the Attendance Management Bot! 🎓\n\n"
        "This bot is designed to help teachers and administrators easily manage student groups and track attendance. "
        "Here’s what you can do:\n"
        "- Create and manage student groups.\n"
        "- Log attendance for each student in a group.\n"
        "- Search for students by name to quickly find their attendance records.\n\n"
        "Select an option below to get started!", 
        reply_markup=markup)

# Link handlers from modules
new_group_handler.register_handlers(bot)
attendance_log_handler.register_handlers(bot)
find_students_handler.register_handlers(bot)

# Start bot
print("Bot is running...")
bot.polling(none_stop=True)

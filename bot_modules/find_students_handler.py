from telebot import types

def register_handlers(bot):
    @bot.message_handler(func=lambda message: message.text == "🔍 Find student")
    def find_student(message):
        bot.send_message(message.chat.id, "We are working on this button")
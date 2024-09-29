import os
from dotenv import load_dotenv
import telebot
from telebot import types
from db_controller import create_connection, add_group, add_student, get_students_by_group_id, create_tables

# Загрузка переменных окружения
load_dotenv()
bot_token = os.getenv("TOKEN")
bot = telebot.TeleBot(bot_token)

# Создаем таблицы при запуске бота
create_tables()

# Переменная для хранения текущего ID группы
current_group_id = None

# Обработчик команды /button для показа клавиатуры
@bot.message_handler(commands=['button'])
def button(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item1 = types.KeyboardButton('New group')
    item2 = types.KeyboardButton('Attendance log')
    item3 = types.KeyboardButton('Find student')

    markup.add(item1, item2, item3)
    
    bot.send_message(message.chat.id, "Choose an action:", reply_markup=markup)

# Обработчик для кнопки "New group"
@bot.message_handler(func=lambda message: message.text == "New group")
def create_group(message):
    bot.send_message(message.chat.id, "Please enter the name of the new group:")
    bot.register_next_step_handler(message, process_group_name)

# Обработчик текстовых сообщений для создания группы
def process_group_name(message):
    group_name = message.text

    try:
        # Добавляем новую группу в таблицу
        add_group(group_name)
        
        # Получаем ID последней добавленной группы
        global current_group_id
        current_group_id = get_last_group_id()  # Функция, которую нужно добавить в db_controller

        bot.send_message(message.chat.id, f"Group '{group_name}' has been successfully created!")

        # Создаем кнопки для выбора способа ввода студентов
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        item1 = types.KeyboardButton('Enter students manually')
        item2 = types.KeyboardButton('Upload from Google Sheets')

        markup.add(item1, item2)
        
        bot.send_message(message.chat.id, "How would you like to add students?", reply_markup=markup)

    except Exception as e:
        bot.send_message(message.chat.id, "An error occurred while creating the group.")
        print(f"Error: {e}")  # Выводим ошибку в консоль для отладки

# Получение ID последней добавленной группы
def get_last_group_id():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM groups ORDER BY id DESC LIMIT 1')
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# Обработчик ввода студентов
@bot.message_handler(func=lambda message: message.text == "Enter students manually")
def input_students(message):
    bot.send_message(message.chat.id, "Please enter the full name of the student (Surname Name) or type 'stop' to finish:")
    bot.register_next_step_handler(message, process_students_input)

# Обработчик ввода имени и фамилии студентов
def process_students_input(message):
    student_full_name = message.text.strip()

    if student_full_name.lower() == 'stop':
        # Когда введено "stop", выводим всех студентов в группе
        students = get_students_by_group_id(current_group_id)
        
        if students:
            student_list = "\n".join([f"{s[2]} {s[1]}" for s in students])  # Форматируем список студентов
            bot.send_message(message.chat.id, f"Students in the group:\n{student_list}")
        else:
            bot.send_message(message.chat.id, "No students found in the group.")
        
        return  # Завершить выполнение функции

    # Разделение фамилии и имени
    name_parts = student_full_name.split()
    if len(name_parts) != 2:
        bot.send_message(message.chat.id, "Please enter the student's full name in the format 'Surname Name'.")
        bot.send_message(message.chat.id, "Please enter the student's full name (Surname Name) or type 'stop' to finish:")
        bot.register_next_step_handler(message, process_students_input)
        return  # Прекратить выполнение, чтобы не продолжать

    surname, name = name_parts

    # Проверяем, существует ли current_group_id
    if current_group_id is None:
        bot.send_message(message.chat.id, "No group is currently selected.")
        return

    add_student(surname, name, current_group_id)
    
    bot.send_message(message.chat.id, f"Student '{surname} {name}' has been added!")

    # Ожидаем следующий ввод
    bot.register_next_step_handler(message, process_students_input)

# Запуск бота
bot.polling(none_stop=True)

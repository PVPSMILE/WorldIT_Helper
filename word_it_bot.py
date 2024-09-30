import os
from dotenv import load_dotenv
import telebot
from telebot import types
from db_controller import create_connection, add_group, add_student, get_students_by_group_name, get_all_groups, get_students_by_group_id, get_group_id_by_name

load_dotenv()
bot_token = os.getenv("TOKEN")
bot = telebot.TeleBot(bot_token)

# Переменная для хранения текущего ID группы
current_group_id = None

# Обработчик команды /start для показа клавиатуры
@bot.message_handler(commands=['start'])
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

# Handler for processing group name
def process_group_name(message):
    global current_group_name
    group_name = message.text

    try:
        add_group(group_name)
        current_group_name = group_name
        bot.send_message(message.chat.id, f"Group '{group_name}' has been successfully created!")

        # Show options for adding students
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        item1 = types.KeyboardButton('Enter students manually')
        item2 = types.KeyboardButton('Upload from Google Sheets')

        markup.add(item1, item2)
        
        bot.send_message(message.chat.id, "How would you like to add students?", reply_markup=markup)

    except Exception as e:
        bot.send_message(message.chat.id, "An error occurred while creating the group.")
        print(f"Error: {e}")

# Handler for entering students manually
@bot.message_handler(func=lambda message: message.text == "Enter students manually")
def input_students(message):
    bot.send_message(message.chat.id, "Please enter the student's full name (Surname Name) or type 'stop' to finish:")
    bot.register_next_step_handler(message, process_students_input)

# Handler for processing student input
def process_students_input(message):
    global current_group_name
    student_full_name = message.text.strip()

    # Get the group ID based on the current group name
    current_group_id = get_group_id_by_name(current_group_name)

    if student_full_name.lower() == 'stop':
        # List all students in the group
        students = get_students_by_group_id(current_group_id)
        if students:
            student_list = "\n".join([f"{s[2]} {s[1]}" for s in students])
            bot.send_message(message.chat.id, f"Students in the group:\n{student_list}")
        else:
            bot.send_message(message.chat.id, "No students found in the group.")
        return

    name_parts = student_full_name.split()
    if len(name_parts) != 2:
        bot.send_message(message.chat.id, "Please enter the student's full name in the format 'Surname Name'.")
        bot.register_next_step_handler(message, process_students_input)
        return

    surname, name = name_parts

    if current_group_id is None:
        bot.send_message(message.chat.id, "No group is currently selected.")
        return

    add_student(surname, name, current_group_id)
    bot.send_message(message.chat.id, f"Student '{surname} {name}' has been added!")
    bot.register_next_step_handler(message, process_students_input)
# Обработчик для кнопки "Attendance log"
@bot.message_handler(func=lambda message: message.text == "Attendance log")
def show_groups_for_attendance(message):
    groups = get_all_groups()  # Fetch all group names
    if not groups:
        bot.send_message(message.chat.id, "No groups available.")
        return

    # Send each group name as a separate message
    for group_name in groups:
        bot.send_message(message.chat.id, group_name)

    # After sending all group names, ask user to select one
    bot.send_message(message.chat.id, "Please enter the name of the group to view attendance log:")
    bot.register_next_step_handler(message, process_group_selection)

# Обработчик выбора группы
def process_group_selection(message):
    group_name = message.text  # The group name the user entered
    bot.send_message(message.chat.id, f"You selected group: {group_name}")

    students = get_students_by_group_name(group_name)  # Fetch students by group name

    if not students:
        bot.send_message(message.chat.id, "No students found in this group.")
        return

    # Start processing each student
    bot.send_message(message.chat.id, "Starting attendance log. Processing students one by one.")
    process_next_student(message, students, 0)  # Start with the first student

# Helper function to process each student
def process_next_student(message, students, index):
    if index >= len(students):
        bot.send_message(message.chat.id, "Attendance log completed for this group.")
        return
    
    student = students[index]
    surname, name = student[0], student[1]  # Assuming (surname, name) format

    # Send the student's name
    bot.send_message(message.chat.id, f"Student: {surname} {name}")
    
    # Create inline buttons for actions (1, 2, 3)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("1", callback_data=f"action_1_{index}"))
    markup.add(types.InlineKeyboardButton("2", callback_data=f"action_2_{index}"))
    markup.add(types.InlineKeyboardButton("3", callback_data=f"action_3_{index}"))
    
    # Send action buttons
    bot.send_message(message.chat.id, "Choose an action:", reply_markup=markup)

# Обработчик для inline кнопок
@bot.callback_query_handler(func=lambda call: call.data.startswith("action_"))
def handle_student_action(call):
    action_data = call.data.split('_')  # Extract action type and student index
    action = action_data[1]
    index = int(action_data[2])

    # Process the action (just printing here, you can extend it as needed)
    bot.send_message(call.message.chat.id, f"Action {action} selected for student {index + 1}.")

    # Now move to the next student
    students = get_students_by_group_name(call.message.text)  # Re-fetch students by group name
    process_next_student(call.message, students, index + 1)

# Запуск бота
bot.polling(none_stop=True)

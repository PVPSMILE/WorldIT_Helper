from telebot import types
from db_controller import add_group, add_student, get_group_id_by_name, get_students_by_group_id

current_group_name = None

def register_handlers(bot):

    @bot.message_handler(func=lambda message: message.text == "New group")
    def create_group(message):
        bot.send_message(message.chat.id, "Please enter the name of the new group:")
        bot.register_next_step_handler(message, process_group_name)

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

    @bot.message_handler(func=lambda message: message.text == "Enter students manually")
    def input_students(message):
        bot.send_message(message.chat.id, "Please enter the student's full name (Surname Name) or type 'stop' to finish:")
        bot.register_next_step_handler(message, process_students_input)

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

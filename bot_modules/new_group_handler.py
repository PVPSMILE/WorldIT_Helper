from telebot import types
from db_controller.db_operators import add_group, add_student, get_group_id_by_name, get_students_by_group_id
import openpyxl
import os

current_group_name = None

def register_handlers(bot):
    def render_menu():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        item1 = types.KeyboardButton('🤓 New group')
        item2 = types.KeyboardButton('📖 Attendance log')
        item3 = types.KeyboardButton('🔍 Find student')

        markup.add(item1, item2, item3)
        return markup
        
    @bot.message_handler(func=lambda message: message.text == "🤓 New group")
    def create_group(message):
        markup = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, "Please enter the name of the new group:", reply_markup=markup)
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
        markup = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, "Please enter the student's full name (Surname Name) or type 'stop' to finish:", reply_markup=markup)
        bot.register_next_step_handler(message, process_students_input)

    def process_students_input(message):
        global current_group_name
        student_full_name = message.text.strip()

        # Get the group ID based on the current group name
        current_group_id = get_group_id_by_name(current_group_name)

        if student_full_name.lower() == 'stop' or student_full_name.lower() == "стоп":
            # List all students in the group
            students = get_students_by_group_id(current_group_id)
            if students:
                student_list = "\n".join([f"{index + 1}. {s[2]} {s[1]}" for index, s in enumerate(students)])

                
                bot.send_message(message.chat.id, f"{current_group_name}\n\n{student_list}", reply_markup=render_menu())

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


    @bot.message_handler(func=lambda message: message.text == "Upload from Google Sheets", content_types=['text'])
    def prompt_upload(message):
        bot.send_message(message.chat.id, "Please upload the Excel file with the student list.")
    
    # Обработка Excel-файла
    @bot.message_handler(content_types=['document'])
    def handle_document(message):
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Сохраняем файл на диск временно
        temp_file = "students_list.xlsx"
        with open(temp_file, 'wb') as new_file:
            new_file.write(downloaded_file)

        # Открываем Excel-файл для обработки
        try:
            wb = openpyxl.load_workbook(temp_file)
            sheet = wb.active

            # Читаем данные
            students = []
            for row in sheet.iter_rows(min_row=2, min_col=1, max_col=2, values_only=True):  # Считаем, что данные начинаются со второй строки
                print(row)
                if row[1] != "ФИО":
                    if row[1] != None:
                        rer = row[1].split(" ")
                        print(rer)
                        students.append((rer[0], rer[1]))  # (ФИО, Номер)
                    else: 
                        print(row[1])
            
            # Получаем id группы
            current_group_id = get_group_id_by_name(current_group_name)

            if current_group_id is None:
                bot.send_message(message.chat.id, "No group is currently selected.")
                return

            # Добавляем студентов в базу данных
            for student in students:
                surname, name = student
                add_student(surname, name, current_group_id)

            # os.remove(temp_file)
            
            bot.send_message(message.chat.id, f"Successfully added {len(students)} students from the file.", reply_markup=render_menu())
        
        except Exception as e:
            bot.send_message(message.chat.id, "Failed to process the Excel file.")
            print(f"Error: {e}")

        # Удаляем временный файл
        os.remove(temp_file)

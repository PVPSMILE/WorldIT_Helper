from telebot import types
from db_controller.db_operators import get_all_groups, get_students_by_group_name, record_attendance, clear_attendance, get_students_with_no_attendance

unknown_students = []
def register_handlers(bot):
    @bot.message_handler(func=lambda message: message.text == "📖 Attendance log")
    def show_groups_for_attendance(message):
        groups = get_all_groups()  # Получаем все названия групп
        if not groups:
            bot.send_message(message.chat.id, "No groups available.")
            return
        
        markup = types.InlineKeyboardMarkup()
        for group_name in groups:
            # Передаем название группы в callback_data
            markup.add(types.InlineKeyboardButton(f'{group_name}', callback_data=f"show_group_{group_name}"))

        bot.send_message(message.chat.id, "Your groups:", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("show_group_"))
    def process_group_selection(call):
        group_name = call.data.split("show_group_")[1]  # Извлекаем название группы
        bot.send_message(call.message.chat.id, f"You selected group: {group_name}")

        students = get_students_with_no_attendance(group_name)  # Получаем студентов по названию группы
        print(students)
        all_students_in_group = get_students_by_group_name(group_name)
        # print(attebdence)
        if not students and not all_students_in_group:
            bot.send_message(call.message.chat.id, "No students found in this group.")
            return
        elif not students and all_students_in_group:
            
            bot.send_message(call.message.chat.id, "You marked all students in this group")
            return


    # Начинаем обработку каждого студента
        process_next_student(call.message, students, 0, group_name, unknown_students)

    def process_next_student(message, students, index, group_name, unknown_students):
        print(students)
        print(len(students))
        if index >= len(students):
            # Когда все студенты обработаны, выводим результат
            bot.send_message(message.chat.id, "Attendance log completed for this group.")
            if unknown_students:
                bot.send_message(message.chat.id, '\n'.join([f"{s[1]} {s[2]}" for s in unknown_students]))
                unknown_students.clear()
            else:
                bot.send_message(message.chat.id, f"All students on a lesson")
            return
        
        student = students[index]
        student_id, surname, name = student  # Предполагаем формат (id, surname, name)

        # Создаем кнопки для действий (Present, Absent, Unknown)
        markup = types.InlineKeyboardMarkup(row_width=3)
        markup.add(
            types.InlineKeyboardButton("Present", callback_data=f"action_1_{student_id}_{index}_{group_name}"),
            types.InlineKeyboardButton("Absent", callback_data=f"action_2_{student_id}_{index}_{group_name}"),
            types.InlineKeyboardButton("Unknown", callback_data=f"action_3_{student_id}_{index}_{group_name}")
        )
        # Отправляем кнопки действий
        bot.send_message(message.chat.id, f"{surname} {name}", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("action_"))
    def handle_student_action(call):
        action_data = call.data.split('_')
        action = action_data[1]
        student_id = int(action_data[2])
        index = int(action_data[3])
        group_name = action_data[4]  # Получаем название группы из callback_data

        # Получаем текущего студента по его индексу (id, surname, name)
        students = get_students_with_no_attendance(group_name)  # Используем сохраненное название группы
        student = students[index]

        # Обрабатываем действие и обновляем списки в зависимости от выбора
        
        if action == "1":  # Present
            record_attendance(student_id, True)
        elif action == "2":  # Absent
            record_attendance(student_id, False)
        elif action == "3":  # Unknown
            unknown_students.append(student)
        # Переход к следующему студенту
        process_next_student(call.message, students, index + 1, group_name, unknown_students)

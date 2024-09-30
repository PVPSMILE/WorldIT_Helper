from telebot import types
from db_controller.db_operators import get_all_groups, get_students_by_group_name

def register_handlers(bot):
    @bot.message_handler(func=lambda message: message.text == "Attendance log")
    def show_groups_for_attendance(message):
        groups = get_all_groups()  # Fetch all group names
        if not groups:
            bot.send_message(message.chat.id, "No groups available.")
            return
        
        markup = types.InlineKeyboardMarkup()
        # Send each group name as a separate message
        for group_name in groups:
            
            markup.add(types.InlineKeyboardButton(f'group_name', callback_data=f"show_group_{group_name}"))

        bot.send_message(message.chat.id, "Your groups", reply_markup=markup)
        # After sending all group names, ask user to select one
        
    # Inline button handler for group selection
    @bot.callback_query_handler(func=lambda call: call.data.startswith("show_group_"))
    def process_group_selection(call):
        group_name = call.data.split("show_group_")[1]  # Extract group name
        bot.send_message(call.message.chat.id, f"You selected group: {group_name}")

        students = get_students_by_group_name(group_name)  # Fetch students by group name

        if not students:
            bot.send_message(call.message.chat.id, "No students found in this group.")
            return

        # Start processing each student
        bot.send_message(call.message.chat.id, "Starting attendance log. Processing students one by one.")
        process_next_student(call.message, students, 0)  # Start with the first student

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

    # Handler for inline action buttons for each student
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

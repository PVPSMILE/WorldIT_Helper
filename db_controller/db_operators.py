from datetime import datetime, timedelta
import threading
from .db_init import create_connection

def add_group(name):
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute('INSERT INTO groups (name) VALUES (?)', (name,))
    conn.commit()
    conn.close()

def add_student(surname, name, group_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute('INSERT INTO students (surname, name, group_id) VALUES (?, ?, ?)', (surname, name, group_id))
    conn.commit()
    conn.close()

def get_students_by_group_id(group_id):
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM students WHERE group_id = ?', (group_id,))
    students = cursor.fetchall()
    conn.close()
    return students

def get_students_by_group_name(group_name):
    conn = create_connection()
    cursor = conn.cursor()

    # Fetch students by group name
    cursor.execute('''
    SELECT s.id AS student_id, s.surname, s.name
    FROM students s
    JOIN groups g ON s.group_id = g.id
    WHERE g.name = ?
    ''', (group_name,))

    students = cursor.fetchall()
    conn.close()
    return students

def record_attendance(student_id, status):
    conn = create_connection()
    cursor = conn.cursor()
    current_date = datetime.now().date()

    cursor.execute("""
    INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)
    ON CONFLICT(student_id, date) DO UPDATE SET status = ?
    """, (student_id, current_date, status, status))

    conn.commit()
    conn.close()

# Получение ID последней добавленной группы
def get_group_id_by_name(group_name):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM groups WHERE name = ?', (group_name,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_all_groups():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM groups')
    groups = cursor.fetchall()  # Fetch all group names
    conn.close()
    return [group[0] for group in groups]  # Return only the names

def get_students_with_no_attendance(group_name):
    conn = create_connection()
    cursor = conn.cursor()

    # Получаем id группы по названию
    cursor.execute("SELECT id FROM groups WHERE name = ?", (group_name,))
    group = cursor.fetchone()

    if not group:
        conn.close()
        return []

    group_id = group[0]

    # Получаем студентов без отметок
    cursor.execute("""
    SELECT s.id, s.surname, s.name 
    FROM students s 
    LEFT JOIN attendance a ON s.id = a.student_id AND a.date = ?
    WHERE a.student_id IS NULL AND s.group_id = ?
    """, (datetime.now().date(), group_id))

    students_with_no_attendance = cursor.fetchall()
    conn.close()
    return students_with_no_attendance

def clear_attendance(group_id):
    conn = create_connection()
    cursor = conn.cursor()

    # Удаляем все отметки для группы
    cursor.execute('DELETE FROM attendance WHERE student_id IN (SELECT id FROM students WHERE group_id = ?)', (group_id,))
    conn.commit()
    conn.close()
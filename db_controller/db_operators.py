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
    SELECT s.surname, s.name
    FROM students s
    JOIN groups g ON s.group_id = g.id
    WHERE g.name = ?
    ''', (group_name,))

    students = cursor.fetchall()
    conn.close()
    return students

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

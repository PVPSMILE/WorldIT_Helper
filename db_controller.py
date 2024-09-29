import sqlite3

def create_connection():
    conn = sqlite3.connect("data.db")
    return conn

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        surname TEXT NOT NULL,
        group_id INTEGER,
        FOREIGN KEY (group_id) REFERENCES groups(id)
    );
    ''')

    conn.commit()
    conn.close()

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

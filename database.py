import sqlite3

def init_db():
    conn=sqlite3.connect('notes.db')
    cursor=conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_note(title,content):
    conn=sqlite3.connect('notes.db')
    cursor=conn.cursor()
    cursor.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (title, content))
    conn.commit()
    conn.close()

def get_all_notes():
    conn=sqlite3.connect('notes.db')
    cursor=conn.cursor()
    cursor.execute('SELECT id,title,content FROM notes')
    notes=cursor.fetchall()
    conn.close()
    return notes

def update_note(note_id, new_title, new_content):
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE notes
        SET title = ?, content = ?
        WHERE id = ?
    ''', (new_title, new_content, note_id))

    conn.commit()
    conn.close()

import sqlite3
import os
from datetime import datetime

def init_db():
    """Initialize the database with proper error handling"""
    conn = None
    try:
        # Delete existing database if it exists to ensure clean schema
        if os.path.exists('notes.db'):
            os.remove('notes.db')
            
        conn = sqlite3.connect('notes.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

def add_note(title, content):
    """Add a new note with timestamp"""
    conn = None
    try:
        conn = sqlite3.connect('notes.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO notes (title, content) VALUES (?, ?)", 
            (title, content)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_all_notes():
    """Get all notes sorted by last updated"""
    conn = None
    try:
        conn = sqlite3.connect('notes.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, title, content, created_at, updated_at 
            FROM notes 
            ORDER BY updated_at DESC
        ''')
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_note_by_id(note_id):
    """Get a single note by ID"""
    conn = None
    try:
        conn = sqlite3.connect('notes.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, title, content, created_at, updated_at 
            FROM notes 
            WHERE id = ?
        ''', (note_id,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()

def update_note(note_id, new_title, new_content):
    """Update a note with new content and update timestamp"""
    conn = None
    try:
        conn = sqlite3.connect('notes.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE notes
            SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (new_title, new_content, note_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def delete_note(note_id):
    """Delete a note by ID"""
    conn = None
    try:
        conn = sqlite3.connect('notes.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def search_notes(query):
    """Search notes by title or content"""
    conn = None
    try:
        conn = sqlite3.connect('notes.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, title, content, created_at, updated_at 
            FROM notes 
            WHERE title LIKE ? OR content LIKE ?
            ORDER BY updated_at DESC
        ''', (f'%{query}%', f'%{query}%'))
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()
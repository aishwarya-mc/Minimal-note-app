import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from database import init_db, add_note, get_all_notes, update_note

init_db()

app = ttk.Window(title="Minimal Note App", themename="darkly", size=(700, 700))

# ------------------ UI Components ------------------

title_label = ttk.Label(app, text="Name")
title_label.pack(pady=(20, 5))

title_entry = ttk.Entry(app, width=40)
title_entry.pack(pady=(0, 15))

content_label = ttk.Label(app, text="Content:")
content_label.pack(pady=(10, 5))

content_text = ttk.Text(app, width=60, height=20)
content_text.pack(pady=(0, 15))

# ------------------ Note Editor ------------------

def open_note_editor(note_id):
    notes = get_all_notes()
    selected_note = next((note for note in notes if note[0] == note_id), None)

    if not selected_note:
        Messagebox.show_error("Error", "Note not found.")
        return

    _, title, content = selected_note

    editor = ttk.Toplevel()
    editor.title("Edit Note")
    editor.geometry("600x500")
    editor.resizable(False, False)

    title_label = ttk.Label(editor, text="Title:")
    title_label.pack(pady=(10, 5))
    title_entry = ttk.Entry(editor, width=50)
    title_entry.insert(0, title)
    title_entry.pack(pady=(0, 10))

    content_label = ttk.Label(editor, text="Content:")
    content_label.pack(pady=(10, 5))
    content_text = ttk.Text(editor, width=60, height=20)
    content_text.insert("1.0", content)
    content_text.pack(pady=(0, 15))

    def save_changes():
        new_title = title_entry.get().strip()
        new_content = content_text.get("1.0", "end-1c").strip()

        if not new_title or not new_content:
            Messagebox.show_warning("Empty Fields", "Title and content cannot be empty.")
            return

        update_note(note_id, new_title, new_content)
        Messagebox.show_info("Updated", "Note updated successfully!")
        editor.destroy()

    save_btn = ttk.Button(editor, text="Save Changes", command=save_changes, bootstyle="success")
    save_btn.pack(pady=10)

# ------------------ Add Note ------------------

def handle_add_note():
    title = title_entry.get()
    content = content_text.get("1.0", "end-1c")
    if title.strip() and content.strip():
        add_note(title, content)
        title_entry.delete(0, "end")
        content_text.delete("1.0", "end")
        Messagebox.show_info("Note Saved", "Your note was saved successfully!")
    else:
        Messagebox.show_warning("Empty Fields", "No contents.")

# ------------------ View Notes ------------------

def handle_view_notes():
    notes = get_all_notes()
    if not notes:
        Messagebox.show_info("No Notes", "Seems like you haven't saved any notes yet.")
        return

    viewer = ttk.Toplevel()
    viewer.title("Your Notes")
    viewer.geometry("600x400")
    viewer.resizable(False, False)

    container = ttk.Frame(viewer)
    container.pack(fill='both', expand=True, padx=10, pady=10)

    canvas = ttk.Canvas(container)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scroll_frame = ttk.Frame(canvas)

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    for note in notes:
        note_id, title, _ = note
        btn = ttk.Button(scroll_frame, text=title, width=50, bootstyle="secondary",
                         command=lambda nid=note_id: open_note_editor(nid))
        btn.pack(pady=5)

# ------------------ Buttons ------------------

add_btn = ttk.Button(app, text="Add Note", command=handle_add_note, bootstyle="success")
add_btn.pack(pady=10)

view_btn = ttk.Button(app, text="View Notes", command=handle_view_notes, bootstyle="info")
view_btn.pack(pady=5)

app.mainloop()

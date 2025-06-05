import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from database import init_db, add_note, get_all_notes

init_db()

app = ttk.Window(title="Minimal Note App", themename="darkly", size=(700, 700))

title_label = ttk.Label(app, text="Name")
title_label.pack(pady=(20, 5))

title_entry = ttk.Entry(app, width=40)
title_entry.pack(pady=(0, 15))

content_label = ttk.Label(app, text="Content:")
content_label.pack(pady=(10, 5))

content_text = ttk.Text(app, width=60, height=20)
content_text.pack(pady=(0, 15))


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


def handle_view_notes():
    notes = get_all_notes()
    if not notes:
        Messagebox.show_info("No Notes", "Seems like you haven't saved any notes yet.")
        return

    viewer = ttk.Toplevel()
    viewer.title("your notes")
    viewer.geometry("600x400")
    viewer.resizable(False, False)

    text_widget = ttk.Text(viewer, width=70, height=20)
    text_widget.pack(padx=10, pady=10)

    for note in notes:
        note_id, title, content = note
        text_widget.insert("end", f"[{note_id}] {title}\n{content}\n{'-'*50}\n")

    text_widget.config(state="disabled")


add_btn = ttk.Button(app, text="Add Note", command=handle_add_note, bootstyle="success")
add_btn.pack(pady=10)

view_btn = ttk.Button(app, text="View Notes", command=handle_view_notes, bootstyle="info")
view_btn.pack(pady=5)

app.mainloop()

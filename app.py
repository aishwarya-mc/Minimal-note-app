import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from database import init_db, add_note


init_db()


app = ttk.Window(title="Minimal Note App", themename="minty", size=(500, 500))


title_label = ttk.Label(app, text="Title:")
title_label.pack(pady=(20, 5))

title_entry = ttk.Entry(app, width=40)
title_entry.pack(pady=(0, 15))


content_label = ttk.Label(app, text="Content:")
content_label.pack(pady=(10, 5))

content_text = ttk.Text(app, width=40, height=10)
content_text.pack(pady=(0, 15))


def handle_add_note():
    title = title_entry.get()
    content = content_text.get("1.0", "end-1c")  # from line 1, char 0 to last char
    if title.strip() and content.strip():
        add_note(title, content)
        title_entry.delete(0, "end")
        content_text.delete("1.0", "end")
        ttk.Messagebox.show_info("Note Saved", "Your note was saved successfully!")
    else:
        ttk.Messagebox.show_warning("Empty Fields", "Both title and content are required.")

add_btn = ttk.Button(app, text="Add Note", command=handle_add_note, bootstyle="success")
add_btn.pack(pady=10)


app.mainloop()

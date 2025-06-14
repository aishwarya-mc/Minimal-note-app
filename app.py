import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from database import (
    init_db, add_note, get_all_notes, 
    update_note, delete_note, get_note_by_id,
    search_notes
)
from datetime import datetime
import time


init_db()

# Create main application window
app = ttk.Window(
    title="Enhanced Notes App", 
    themename="darkly", 
    size=(900, 800),
    resizable=(False, False)
)


# ------------------ Styling Constants ------------------
PAD_X = 20
PAD_Y = 10
ENTRY_WIDTH = 70
TEXT_WIDTH = 80
TEXT_HEIGHT = 15
CARD_PADDING = 15
ANIMATION_DURATION = 300  # milliseconds

# Custom styles
style = ttk.Style()
style.configure('Card.TFrame', background='#2c2c2c', relief='flat')
style.configure('Title.TLabel', font=('Helvetica', 24, 'bold'))
style.configure('Subtitle.TLabel', font=('Helvetica', 12))
style.configure('NoteTitle.TLabel', font=('Helvetica', 12, 'bold'))
style.configure('NoteContent.TLabel', font=('Helvetica', 10))

# ------------------ Main Frame ------------------
main_frame = ttk.Frame(app, padding=20)
main_frame.pack(fill=BOTH, expand=YES)

# ------------------ Header Frame ------------------
header_frame = ttk.Frame(main_frame)
header_frame.pack(fill=X, pady=(0, 20))

# Title with animation
title_label = ttk.Label(
    header_frame, 
    text="✨ Enhanced Notes", 
    style='Title.TLabel'
)
title_label.pack(side=LEFT)

# Theme toggle with animation
def toggle_theme():
    current_theme = app.style.theme.name
    new_theme = 'litera' if current_theme == 'darkly' else 'darkly'
    theme_btn.configure(text="🌙" if new_theme == 'darkly' else "☀️")
    app.style.theme_use(new_theme)
    # Add smooth transition effect
    for widget in main_frame.winfo_children():
        widget.configure(style='Card.TFrame')

theme_btn = ttk.Button(
    header_frame, 
    text="🌙", 
    command=toggle_theme,
    bootstyle="outline-toolbutton",
    width=3
)
theme_btn.pack(side=RIGHT, padx=5)

# ------------------ Note Creation Frame ------------------
create_frame = ttk.Frame(
    main_frame, 
    style='Card.TFrame',
    padding=CARD_PADDING
)
create_frame.pack(fill=X, pady=PAD_Y)

# Title with icon
title_header = ttk.Frame(create_frame)
title_header.pack(fill=X, pady=(0, PAD_Y))
ttk.Label(
    title_header, 
    text="📝 Create New Note",
    style='Subtitle.TLabel'
).pack(side=LEFT)

# Title entry with placeholder
title_entry = ttk.Entry(
    create_frame, 
    width=ENTRY_WIDTH,
    font=('Segoe UI', 11)
)
title_entry.insert(0, "Enter note title...")
title_entry.bind('<FocusIn>', lambda e: title_entry.delete(0, END) if title_entry.get() == "Enter note title..." else None)
title_entry.bind('<FocusOut>', lambda e: title_entry.insert(0, "Enter note title...") if not title_entry.get() else None)
title_entry.pack(fill=X, pady=PAD_Y)

# Content with placeholder
content_text = ttk.Text(
    create_frame, 
    width=TEXT_WIDTH, 
    height=10,
    wrap=WORD,
    font=('Segoe UI', 11)
)
content_text.insert('1.0', "Write your note content here...")
content_text.bind('<FocusIn>', lambda e: content_text.delete('1.0', END) if content_text.get('1.0', END).strip() == "Write your note content here..." else None)
content_text.bind('<FocusOut>', lambda e: content_text.insert('1.0', "Write your note content here...") if not content_text.get('1.0', END).strip() else None)
content_text.pack(fill=X, pady=PAD_Y)

# Button Frame with modern styling
button_frame = ttk.Frame(create_frame)
button_frame.pack(fill=X, pady=(10, 0))

def clear_fields():
    """Clear the input fields with animation"""
    title_entry.delete(0, END)
    content_text.delete('1.0', END)
    title_entry.insert(0, "Enter note title...")
    content_text.insert('1.0', "Write your note content here...")

def handle_add_note():
    """Handle adding a new note with animation"""
    title = title_entry.get().strip()
    content = content_text.get('1.0', END).strip()
    
    if title == "Enter note title..." or content == "Write your note content here...":
        title = ""
        content = ""
    
    if not title or not content:
        Messagebox.show_warning(
            "Empty Fields", 
            "Both title and content are required.",
            parent=app
        )
        return
    
    # Add loading animation
    add_btn.configure(state='disabled', text="Saving...")
    app.update()
    
    note_id = add_note(title, content)
    if note_id:
        # Success animation
        add_btn.configure(text="✓ Saved!", bootstyle="success")
        app.after(1000, lambda: add_btn.configure(text="Save Note", bootstyle="success", state='normal'))
        clear_fields()
        if hasattr(app, 'notes_viewer') and app.notes_viewer.winfo_exists():
            refresh_notes_list()
    else:
        add_btn.configure(text="Save Note", bootstyle="success", state='normal')
        Messagebox.show_error(
            "Error", 
            "Failed to save note. Please try again.",
            parent=app
        )

# Add Note Button with modern style
add_btn = ttk.Button(
    button_frame, 
    text="Save Note", 
    command=handle_add_note, 
    bootstyle="success",
    width=15
)
add_btn.pack(side=RIGHT, padx=5)

# Clear Button with modern style
clear_btn = ttk.Button(
    button_frame, 
    text="Clear", 
    command=clear_fields, 
    bootstyle="outline-secondary",
    width=15
)
clear_btn.pack(side=RIGHT, padx=5)

# ------------------ Notes Viewer Functions ------------------
def refresh_notes_list(search_query=None):
    """Refresh the notes list with animations"""
    if not hasattr(app, 'notes_scroll_frame'):
        return
    
    # Clear existing notes with fade out
    for widget in app.notes_scroll_frame.winfo_children():
        widget.destroy()
    
    notes = search_notes(search_query) if search_query else get_all_notes()
    
    if not notes:
        no_notes_label = ttk.Label(
            app.notes_scroll_frame, 
            text="✨ No notes found" if search_query else "✨ Start creating your first note!",
            style='Subtitle.TLabel'
        )
        no_notes_label.pack(pady=30)
        return
    
    for note in notes:
        note_id, title, content, created_at, updated_at = note
        note_frame = ttk.Frame(
            app.notes_scroll_frame, 
            style='Card.TFrame',
            padding=CARD_PADDING
        )
        note_frame.pack(fill=X, pady=5)
        
        # Format dates
        created = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S').strftime('%b %d, %Y')
        updated = datetime.strptime(updated_at, '%Y-%m-%d %H:%M:%S').strftime('%b %d, %Y')
        
        # Note title with dates
        title_frame = ttk.Frame(note_frame)
        title_frame.pack(fill=X)
        
        title_label = ttk.Label(
            title_frame, 
            text=title,
            style='NoteTitle.TLabel'
        )
        title_label.pack(side=LEFT)
        
        date_label = ttk.Label(
            title_frame,
            text=f"📅 {created}",
            style='Subtitle.TLabel'
        )
        date_label.pack(side=RIGHT)
        
        # Content preview with modern styling
        preview = (content[:150] + '...') if len(content) > 150 else content
        content_label = ttk.Label(
            note_frame, 
            text=preview,
            style='NoteContent.TLabel',
            wraplength=800
        )
        content_label.pack(fill=X, pady=(5, 10))
        
        # Button frame with modern styling
        btn_frame = ttk.Frame(note_frame)
        btn_frame.pack(fill=X)
        
        # View/Edit button with icon
        ttk.Button(
            btn_frame, 
            text="✏️ Edit", 
            bootstyle="info-outline",
            command=lambda nid=note_id: open_note_editor(nid),
            width=10
        ).pack(side=LEFT, padx=2)
        
        # Delete button with icon
        ttk.Button(
            btn_frame, 
            text="🗑️ Delete", 
            bootstyle="danger-outline",
            command=lambda nid=note_id: confirm_delete_note(nid),
            width=10
        ).pack(side=LEFT, padx=2)

def confirm_delete_note(note_id):
    """Confirm before deleting a note"""
    result = Messagebox.show_question(
        "Confirm Delete",
        "Are you sure you want to delete this note?",
        parent=app.notes_viewer if hasattr(app, 'notes_viewer') else app,
        buttons=['No:secondary', 'Yes:danger']
    )
    
    if result == 'Yes':
        if delete_note(note_id):
            Messagebox.show_info(
                "Deleted", 
                "Note deleted successfully.",
                parent=app.notes_viewer if hasattr(app, 'notes_viewer') else app
            )
            refresh_notes_list()
        else:
            Messagebox.show_error(
                "Error", 
                "Failed to delete note.",
                parent=app.notes_viewer if hasattr(app, 'notes_viewer') else app
            )

def open_note_editor(note_id):
    """Open a window to edit an existing note"""
    note = get_note_by_id(note_id)
    if not note:
        Messagebox.show_error(
            "Error", 
            "Note not found.",
            parent=app.notes_viewer if hasattr(app, 'notes_viewer') else app
        )
        return
    
    _, title, content, created_at, updated_at = note
    
    editor = ttk.Toplevel(title="Edit Note")
    editor.geometry("700x600")
    editor.resizable(False, False)
    
    # Main frame
    editor_frame = ttk.Frame(editor, padding=10)
    editor_frame.pack(fill=BOTH, expand=YES)
    
    # Title
    ttk.Label(editor_frame, text="Title:").pack(anchor=NW, pady=PAD_Y)
    title_entry = ttk.Entry(editor_frame, width=ENTRY_WIDTH)
    title_entry.insert(0, title)
    title_entry.pack(fill=X, pady=PAD_Y)
    
    # Content
    ttk.Label(editor_frame, text="Content:").pack(anchor=NW, pady=PAD_Y)
    content_text = ttk.Text(
        editor_frame, 
        width=TEXT_WIDTH, 
        height=TEXT_HEIGHT,
        wrap=WORD,
        font=('Segoe UI', 10)
    )
    content_text.insert('1.0', content)
    content_text.pack(fill=BOTH, expand=YES, pady=PAD_Y)
    
    # Dates
    created = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S').strftime('%b %d, %Y %H:%M')
    updated = datetime.strptime(updated_at, '%Y-%m-%d %H:%M:%S').strftime('%b %d, %Y %H:%M')
    dates_frame = ttk.Frame(editor_frame)
    dates_frame.pack(fill=X, pady=PAD_Y)
    
    ttk.Label(
        dates_frame, 
        text=f"Created: {created}",
        font=('Helvetica', 8)
    ).pack(side=LEFT)
    
    ttk.Label(
        dates_frame, 
        text=f"Last Updated: {updated}",
        font=('Helvetica', 8)
    ).pack(side=RIGHT)
    
    # Button frame
    btn_frame = ttk.Frame(editor_frame)
    btn_frame.pack(fill=X, pady=(10, 0))
    
    def save_changes():
        """Save the edited note"""
        new_title = title_entry.get().strip()
        new_content = content_text.get('1.0', END).strip()
        
        if not new_title or not new_content:
            Messagebox.show_warning(
                "Empty Fields", 
                "Both title and content are required.",
                parent=editor
            )
            return
        
        if update_note(note_id, new_title, new_content):
            Messagebox.show_info(
                "Success", 
                "Note updated successfully!",
                parent=editor
            )
            editor.destroy()
            refresh_notes_list()
        else:
            Messagebox.show_error(
                "Error", 
                "Failed to update note.",
                parent=editor
            )
    
    # Save button
    ttk.Button(
        btn_frame, 
        text="Save Changes", 
        command=save_changes, 
        bootstyle=SUCCESS,
        width=15
    ).pack(side=RIGHT, padx=5)
    
    # Cancel button
    ttk.Button(
        btn_frame, 
        text="Cancel", 
        command=editor.destroy, 
        bootstyle=SECONDARY,
        width=15
    ).pack(side=RIGHT, padx=5)

def handle_view_notes():
    """Open the notes viewer window with animations"""
    if hasattr(app, 'notes_viewer') and app.notes_viewer.winfo_exists():
        app.notes_viewer.lift()
        return
    
    viewer = ttk.Toplevel(title="Your Notes")
    viewer.geometry("900x700")
    viewer.resizable(False, False)
    
    app.notes_viewer = viewer
    
    # Main frame with modern styling
    viewer_frame = ttk.Frame(viewer, padding=20)
    viewer_frame.pack(fill=BOTH, expand=YES)
    
    # Search frame with modern styling
    search_frame = ttk.Frame(viewer_frame)
    search_frame.pack(fill=X, pady=(0, 20))
    
    ttk.Label(
        search_frame, 
        text="🔍 Search Notes",
        style='Subtitle.TLabel'
    ).pack(side=LEFT, padx=(0, 10))
    
    search_var = ttk.StringVar()
    search_entry = ttk.Entry(
        search_frame, 
        textvariable=search_var,
        width=50,
        font=('Segoe UI', 11)
    )
    search_entry.pack(side=LEFT, fill=X, expand=YES)
    
    def perform_search(*args):
        refresh_notes_list(search_var.get())
    
    search_var.trace_add('write', perform_search)
    
    # Clear search button with icon
    ttk.Button(
        search_frame, 
        text="🗑️ Clear", 
        command=lambda: search_var.set(''),
        bootstyle="outline-secondary",
        width=10
    ).pack(side=LEFT, padx=5)
    
    # Notes container with modern scrollbar
    container = ttk.Frame(viewer_frame)
    container.pack(fill=BOTH, expand=YES)
    
    canvas = ttk.Canvas(container)
    scrollbar = ttk.Scrollbar(container, orient=VERTICAL, command=canvas.yview)
    app.notes_scroll_frame = ttk.Frame(canvas)
    
    app.notes_scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=app.notes_scroll_frame, anchor=NW)
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side=LEFT, fill=BOTH, expand=YES)
    scrollbar.pack(side=RIGHT, fill=Y)
    
    refresh_notes_list()
    
    def on_close():
        if hasattr(app, 'notes_viewer'):
            del app.notes_viewer
        viewer.destroy()
    
    viewer.protocol("WM_DELETE_WINDOW", on_close)

# ------------------ Main Buttons ------------------
action_frame = ttk.Frame(main_frame)
action_frame.pack(fill=X, pady=(20, 0))

# View Notes Button with icon
ttk.Button(
    action_frame, 
    text="📚 View Notes", 
    command=handle_view_notes, 
    bootstyle="info",
    width=15
).pack(side=LEFT, padx=5)

# Exit Button with icon
ttk.Button(
    action_frame, 
    text="🚪 Exit", 
    command=app.quit, 
    bootstyle="danger",
    width=15
).pack(side=RIGHT, padx=5)

# ------------------ Run Application ------------------
app.mainloop()
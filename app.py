import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from database import (
    init_db, add_note, get_all_notes, 
    update_note, delete_note, get_note_by_id,
    search_notes
)
from datetime import datetime


init_db()

# Create main application window
app = ttk.Window(
    title="Enhanced Notes App", 
    themename="darkly", 
    size=(800, 700),
    resizable=(False, False)
)


# ------------------ Styling Constants ------------------
PAD_X = 15
PAD_Y = 5
ENTRY_WIDTH = 60
TEXT_WIDTH = 70
TEXT_HEIGHT = 15

# ------------------ Main Frame ------------------
main_frame = ttk.Frame(app, padding=10)
main_frame.pack(fill=BOTH, expand=YES)

# ------------------ Header Frame ------------------
header_frame = ttk.Frame(main_frame)
header_frame.pack(fill=X, pady=(0, 10))

# Title
title_label = ttk.Label(
    header_frame, 
    text="Enhanced Notes", 
    font=('Helvetica', 16, 'bold')
)
title_label.pack(side=LEFT)

# Theme toggle
def toggle_theme():
    current_theme = app.style.theme.name
    new_theme = 'litera' if current_theme == 'darkly' else 'darkly'
    app.style.theme_use(new_theme)

theme_btn = ttk.Button(
    header_frame, 
    text="☀️/🌙", 
    command=toggle_theme,
    bootstyle="outline",
    width=3
)
theme_btn.pack(side=RIGHT, padx=5)

# ------------------ Note Creation Frame ------------------
create_frame = ttk.LabelFrame(
    main_frame, 
    text="Create New Note", 
    padding=(PAD_X, 10)
)
create_frame.pack(fill=X, pady=PAD_Y)

# Title
ttk.Label(create_frame, text="Title:").pack(anchor=NW, pady=PAD_Y)
title_entry = ttk.Entry(create_frame, width=ENTRY_WIDTH)
title_entry.pack(fill=X, pady=PAD_Y)

# Content
ttk.Label(create_frame, text="Content:").pack(anchor=NW, pady=PAD_Y)
content_text = ttk.Text(
    create_frame, 
    width=TEXT_WIDTH, 
    height=10,
    wrap=WORD,
    font=('Segoe UI', 10)
)
content_text.pack(fill=X, pady=PAD_Y)

# Button Frame
button_frame = ttk.Frame(create_frame)
button_frame.pack(fill=X, pady=(10, 0))

def clear_fields():
    """Clear the input fields"""
    title_entry.delete(0, END)
    content_text.delete('1.0', END)

def handle_add_note():
    """Handle adding a new note"""
    title = title_entry.get().strip()
    content = content_text.get('1.0', END).strip()
    
    if not title or not content:
        Messagebox.show_warning(
            "Empty Fields", 
            "Both title and content are required.",
            parent=app
        )
        return
    
    note_id = add_note(title, content)
    if note_id:
        Messagebox.show_info(
            "Success", 
            f"Note saved successfully! (ID: {note_id})",
            parent=app
        )
        clear_fields()
        # Refresh notes list if viewer is open
        if hasattr(app, 'notes_viewer') and app.notes_viewer.winfo_exists():
            refresh_notes_list()
    else:
        Messagebox.show_error(
            "Error", 
            "Failed to save note. Please try again.",
            parent=app
        )

# Add Note Button
add_btn = ttk.Button(
    button_frame, 
    text="Save Note", 
    command=handle_add_note, 
    bootstyle=SUCCESS,
    width=12
)
add_btn.pack(side=RIGHT, padx=5)

# Clear Button
clear_btn = ttk.Button(
    button_frame, 
    text="Clear", 
    command=clear_fields, 
    bootstyle=WARNING,
    width=12
)
clear_btn.pack(side=RIGHT, padx=5)

# ------------------ Notes Viewer Functions ------------------
def refresh_notes_list(search_query=None):
    """Refresh the notes list with optional search"""
    if not hasattr(app, 'notes_viewer') or not app.notes_viewer.winfo_exists():
        return
    
    # Clear existing notes
    for widget in app.notes_scroll_frame.winfo_children():
        widget.destroy()
    
    # Get notes based on search or all notes
    notes = search_notes(search_query) if search_query else get_all_notes()
    
    if not notes:
        no_notes_label = ttk.Label(
            app.notes_scroll_frame, 
            text="No notes found" if search_query else "No notes yet",
            font=('Helvetica', 10, 'italic')
        )
        no_notes_label.pack(pady=20)
        return
    
    for note in notes:
        note_id, title, content, created_at, updated_at = note
        note_frame = ttk.Frame(app.notes_scroll_frame, padding=5)
        note_frame.pack(fill=X, pady=2)
        
        # Format dates
        created = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S').strftime('%b %d, %Y')
        updated = datetime.strptime(updated_at, '%Y-%m-%d %H:%M:%S').strftime('%b %d, %Y')
        
        # Note title with dates
        title_label = ttk.Label(
            note_frame, 
            text=f"{title} (Created: {created}, Updated: {updated})",
            font=('Helvetica', 10, 'bold'),
            anchor=W
        )
        title_label.pack(fill=X)
        
        # Content preview (first 100 chars)
        preview = (content[:100] + '...') if len(content) > 100 else content
        content_label = ttk.Label(
            note_frame, 
            text=preview,
            font=('Helvetica', 9),
            anchor=W,
            wraplength=700
        )
        content_label.pack(fill=X)
        
        # Button frame
        btn_frame = ttk.Frame(note_frame)
        btn_frame.pack(fill=X, pady=(5, 0))
        
        # View/Edit button
        ttk.Button(
            btn_frame, 
            text="Edit", 
            bootstyle=INFO,
            command=lambda nid=note_id: open_note_editor(nid),
            width=8
        ).pack(side=LEFT, padx=2)
        
        # Delete button
        ttk.Button(
            btn_frame, 
            text="Delete", 
            bootstyle=DANGER,
            command=lambda nid=note_id: confirm_delete_note(nid),
            width=8
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
    """Open the notes viewer window"""
    # Check if viewer exists and is visible
    if hasattr(app, 'notes_viewer') and app.notes_viewer.winfo_exists():
        app.notes_viewer.lift()
        return
    
    viewer = ttk.Toplevel(title="Your Notes")
    viewer.geometry("800x600")
    viewer.resizable(False, False)
    
    # Store viewer reference
    app.notes_viewer = viewer
    
    # Main frame
    viewer_frame = ttk.Frame(viewer, padding=10)
    viewer_frame.pack(fill=BOTH, expand=YES)
    
    # Search frame
    search_frame = ttk.Frame(viewer_frame)
    search_frame.pack(fill=X, pady=(0, 10))
    
    ttk.Label(search_frame, text="Search:").pack(side=LEFT, padx=(0, 5))
    
    search_var = ttk.StringVar()
    search_entry = ttk.Entry(
        search_frame, 
        textvariable=search_var,
        width=40
    )
    search_entry.pack(side=LEFT, fill=X, expand=YES)
    
    def perform_search(*args):
        """Perform search as user types"""
        refresh_notes_list(search_var.get())
    
    search_var.trace_add('write', perform_search)
    
    # Clear search button
    ttk.Button(
        search_frame, 
        text="Clear", 
        command=lambda: search_var.set(''),
        bootstyle=SECONDARY,
        width=8
    ).pack(side=LEFT, padx=5)
    
    # Notes container with scrollbar
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
    
    # Initial load of notes
    refresh_notes_list()
    
    # Close handler
    def on_close():
        if hasattr(app, 'notes_viewer'):
            del app.notes_viewer
        viewer.destroy()
    
    viewer.protocol("WM_DELETE_WINDOW", on_close)

# ------------------ Main Buttons ------------------
action_frame = ttk.Frame(main_frame)
action_frame.pack(fill=X, pady=(10, 0))

# View Notes Button
ttk.Button(
    action_frame, 
    text="View Notes", 
    command=handle_view_notes, 
    bootstyle=INFO,
    width=15
).pack(side=LEFT, padx=5)

# Exit Button
ttk.Button(
    action_frame, 
    text="Exit", 
    command=app.quit, 
    bootstyle=DANGER,
    width=15
).pack(side=RIGHT, padx=5)

# ------------------ Run Application ------------------
app.mainloop()
import tkinter as tk
from datetime import datetime
import sqlite3
from tkinter import messagebox
from settings_prj import open_settings, open_full_screen_history, open_logout_window
from emotion_detection_nlplib import analyze_mood, get_sentiment_score
from PIL import Image, ImageTk
from eunoia_report import report_view

def initialize_db():
    conn = sqlite3.connect("eunoia.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT UNIQUE,
        full_name TEXT,
        age INTEGER,
        gender TEXT,
        contact TEXT,
        bio TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS diary_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        entry_date TEXT,
        content TEXT,
        mood TEXT,
        sentiment_score REAL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)
    
    conn.commit()
    conn.close()

initialize_db()
def update_db_schema():
    conn = sqlite3.connect("eunoia.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'full_name' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
        if 'age' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN age INTEGER")
        if 'gender' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN gender TEXT")
        if 'contact' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN contact TEXT")
        if 'email' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN email TEXT UNIQUE")
        if 'bio' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN bio TEXT")
        if 'created_at' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            
        conn.commit()
    except Exception as e:
        print(f"Error updating schema: {e}")
    finally:
        conn.close()


initialize_db()
update_db_schema()

def save_entry(user_id, text_widget, history_listbox, diary_frame):
    entry_text = text_widget.get(1.0, tk.END).strip()
    if not entry_text:
        messagebox.showwarning("Empty Entry", "Cannot save an empty entry.")
        return

    mood = analyze_mood(entry_text)
    sentiment_score = get_sentiment_score(entry_text)['compound']
    entry_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect("eunoia.db")
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO diary_entries (user_id, entry_date, content, mood, sentiment_score) VALUES (?, ?, ?, ?, ?)", 
            (user_id, entry_date, entry_text, mood, sentiment_score)
        )
        conn.commit()
        
        load_history(user_id, history_listbox)
        text_widget.delete(1.0, tk.END)

        success_label = tk.Label(diary_frame, text="✅ Entry saved!", font=("Arial", 10, "bold"), fg="green", bg="#fffaf0")
        success_label.pack()
        diary_frame.after(2000, success_label.destroy)
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to save entry: {str(e)}")
    finally:
        conn.close()

def load_history(user_id, history_listbox):
    history_listbox.delete(0, tk.END)
    
    conn = sqlite3.connect("eunoia.db")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT entry_date FROM diary_entries WHERE user_id=? ORDER BY entry_date DESC", (user_id,))
        entries = cursor.fetchall()

        for entry in entries:
            formatted_date = entry[0]
            history_listbox.insert(tk.END, formatted_date)
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to load history: {str(e)}")
    finally:
        conn.close()

def apply_background(window, image_path):
    def resize_background(event=None):
        window.after(50, lambda: update_background())

    def update_background():
        try:
            image = Image.open(image_path)
            image = image.resize((window.winfo_width(), window.winfo_height()), Image.LANCZOS)
            bg_image = ImageTk.PhotoImage(image)
            bg_label.config(image=bg_image)
            bg_label.image = bg_image
        except Exception as e:
            print(f"Error updating background: {str(e)}")

    try:
        image = Image.open(image_path)
        image = image.resize((window.winfo_width(), window.winfo_height()), Image.LANCZOS)
        bg_image = ImageTk.PhotoImage(image)

        bg_label = tk.Label(window, image=bg_image)
        bg_label.image = bg_image
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.lower()

        window.bind("<Configure>", resize_background)
    except Exception as e:
        print(f"Error setting background: {str(e)}")

def show_selected_entry(event, user_id, history_listbox):
    selected_index = history_listbox.curselection()
    if not selected_index:
        return

    selected_date = history_listbox.get(selected_index[0])
    conn = sqlite3.connect("eunoia.db")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM diary_entries WHERE user_id=? AND entry_date=?", (user_id, selected_date))
        entry = cursor.fetchone()

        if entry:
            entry_window = tk.Toplevel(history_listbox.winfo_toplevel())
            entry_window.geometry("500x350")
            entry_window.attributes('-fullscreen', True)
            
            try:
                image_path = "view_history_bg.jpg"
                entry_window.after(100, lambda: apply_background(entry_window, image_path))
            except:
                pass

            tk.Label(entry_window, text=f"Date: {selected_date}", font=("Arial", 12, "bold"), bg="#FFF5E1").pack(pady=10)

            entry_text = tk.Text(entry_window, wrap=tk.WORD, font=("Courier", 10), bg="#FFF5E1", height=10, width=50)
            entry_text.insert(tk.END, entry[0])
            entry_text.config(state=tk.DISABLED)
            entry_text.pack(pady=5, padx=10)

            tk.Button(entry_window, text="Close", bg="#8C4A2F", fg="white", command=entry_window.destroy).pack(side=tk.BOTTOM, pady=10)
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to load entry: {str(e)}")
    finally:
        conn.close()

def diary_ui_setup(root, username, user_id):
    diary_window = tk.Toplevel()
    diary_window.attributes("-fullscreen", True)

    try:
        image_path = "D:/Semester 2/spyder/package/final/eunoia_theme_bg.jpg"
        diary_window.after(100, lambda: apply_background(diary_window, image_path))
    except:
        pass

    tk.Label(diary_window, text=f"Hello {username}!", font=("Arial", 16, "italic"), fg="#5C4033", bg="SystemButtonFace").place(x=20, y=10)

    tk.Button(diary_window, text="⚙ Settings", font=("Arial", 12, "bold"), bg="#D9A066",
              command=lambda: open_settings(diary_window, user_id)).place(x=30, y=100)
    
    tk.Button(diary_window, text="📜 View History", font=("Arial", 12, "bold"), bg="#A67B5B",
              command=lambda: open_full_screen_history(diary_window, user_id)).place(x=30, y=200)
    
    tk.Button(diary_window, text="🚪 Logout", font=("Arial", 12, "bold"), bg="#E74C3C", fg="white",
              command=lambda: open_logout_window(diary_window)).place(x=30, y=400)
   
    tk.Button(diary_window, text="🔍Analyse myself", font=("Arial", 12, "bold"), bg="#D9A066", fg="white",
              command=lambda: report_view(user_id)).place(x=30, y=300)

    history_frame = tk.Frame(diary_window, bg="#F5F5DC")
    history_listbox = tk.Listbox(history_frame, bg="white", fg="black", font=("Arial", 10))
    history_listbox.pack(expand=True, fill="both")
    load_history(user_id, history_listbox)

    history_listbox.bind("<Double-Button-1>", lambda event: show_selected_entry(event, user_id, history_listbox))

    diary_frame = tk.Frame(diary_window, bg="#fffaf0", relief="ridge", bd=2)
    diary_frame.place(relx=0.7, rely=0.5, anchor="center")

    tk.Label(diary_frame, text="My Diary Journal", font=("Arial", 14, "bold"), fg="#333", bg="#fffaf0").pack()
    text_widget = tk.Text(diary_frame, width=40, height=15, font=("Courier", 12), bd=2, relief="groove")
    text_widget.pack(pady=10)

    save_button = tk.Button(diary_frame, text="💾 Save Entry", font=("Arial", 12, "bold"), bg="#A67B5B", fg="white",
                        command=lambda: save_entry(user_id, text_widget, history_listbox, diary_frame))
    save_button.pack(pady=10)
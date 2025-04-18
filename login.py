import tkinter as tk
from tkinter import messagebox
import sqlite3
import hashlib
import os
from diary import diary_ui_setup

class DatabaseManager:
    def __init__(self):
        self.db_path = "eunoia.db"
        self.ensure_database()
        
    def ensure_database(self):
        if not os.path.exists(self.db_path):
            self.create_database()
            
    def create_database(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
           # In login1.py, modify the users table creation:
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
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to create database: {str(e)}")
            
    def get_connection(self):
        try:
            return sqlite3.connect(self.db_path)
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to connect to database: {str(e)}")
            return None

db_manager = DatabaseManager()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def collect_personal_details(root, username):
    details_window = tk.Toplevel(root)
    details_window.title("Personal Details")
    details_window.geometry("450x550")
    details_window.configure(bg="#F5F5DC")
    details_window.grab_set()
    
    tk.Label(details_window, text="Complete Your Profile", 
             font=("Arial", 16, "bold"), bg="#F5F5DC", fg="#5C4033").pack(pady=10)
    
    fields = [
        {"label": "Full Name*:", "key": "full_name", "type": "entry", "required": True},
        {"label": "Email*:", "key": "email", "type": "entry", "required": True},
        {"label": "Age:", "key": "age", "type": "spinbox", "from_": 10, "to": 100, "required": False},
        {"label": "Gender:", "key": "gender", "type": "combobox", "values": ["Male", "Female", "Other", "Prefer not to say"], "required": False},
        {"label": "Contact Number:", "key": "contact", "type": "entry", "required": False},
        {"label": "Bio (max 200 chars):", "key": "bio", "type": "text", "height": 4, "required": False}
    ]
    
    entries = {}
    
    for field in fields:
        frame = tk.Frame(details_window, bg="#F5F5DC")
        frame.pack(pady=5, fill="x", padx=20)
        
        tk.Label(frame, text=field["label"], font=("Arial", 10), 
                bg="#F5F5DC", fg="#5B3A29", width=15, anchor="w").pack(side="left")
        
        if field["type"] == "entry":
            entry = tk.Entry(frame, width=30, font=("Arial", 10))
            entry.pack(side="right", padx=10)
        elif field["type"] == "spinbox":
            entry = tk.Spinbox(frame, from_=field["from_"], to=field["to"], width=28, font=("Arial", 10))
            entry.pack(side="right", padx=10)
        elif field["type"] == "combobox":
            entry = tk.StringVar(value=field["values"][0])
            option_menu = tk.OptionMenu(frame, entry, *field["values"])
            option_menu.config(width=27, font=("Arial", 10))
            option_menu.pack(side="right", padx=10)
        elif field["type"] == "text":
            entry = tk.Text(frame, width=30, height=field.get("height", 3), font=("Arial", 10))
            entry.pack(side="right", padx=10)
        
        entries[field["key"]] = entry
    
    def save_details():
        details = {}
        error_fields = []
        
        for field in fields:
            key = field["key"]
            if field["type"] in ["entry", "spinbox"]:
                value = entries[key].get()
            elif field["type"] == "combobox":
                value = entries[key].get()
            elif field["type"] == "text":
                value = entries[key].get("1.0", "end-1c")
            
            details[key] = value.strip()
            
            if field["required"] and not details[key]:
                error_fields.append(field["label"].replace("*:", ""))
        
        if error_fields:
            messagebox.showerror("Validation Error", 
                                f"Please fill in all required fields:\n{', '.join(error_fields)}")
            return
        
        if details["email"] and "@" not in details["email"]:
            messagebox.showerror("Validation Error", "Please enter a valid email address")
            return
        
        if details.get("bio") and len(details["bio"]) > 200:
            messagebox.showerror("Validation Error", "Bio should be 200 characters or less")
            return
        
        conn = sqlite3.connect("eunoia.db")
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET full_name=?, email=?, age=?, gender=?, contact=?, bio=?
                WHERE username=?
            """, (
                details["full_name"],
                details["email"],
                int(details["age"]) if details["age"] else None,
                details["gender"],
                details["contact"],
                details["bio"],
                username
            ))
            conn.commit()
            messagebox.showinfo("Success", "Personal details saved successfully!")
            details_window.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "This email is already registered with another account")
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to save details: {str(e)}")
        finally:
            conn.close()
    
    button_frame = tk.Frame(details_window, bg="#F5F5DC")
    button_frame.pack(pady=20)
    
    tk.Button(button_frame, text="Save Details", font=("Arial", 12), 
             fg="white", bg="#4C7031", command=save_details).pack(side="left", padx=10)
    
    tk.Button(button_frame, text="Skip for Now", font=("Arial", 12), 
             fg="white", bg="#8C4A2F", command=details_window.destroy).pack(side="right", padx=10)
    
def setup_login(root):
    login_frame = tk.Frame(root, bg="#A67B5B", padx=30, pady=20, bd=2, relief="ridge")
    login_frame.place(relx=0.5, rely=0.5, anchor="center")
    
    # App title
    tk.Label(root, text="Eunoia", font=("Arial", 30, "italic"), 
            fg="#5C4033", bg="SystemButtonFace").place(relx=0.5, y=15, anchor="n")
    
    # Username field
    tk.Label(login_frame, text="Enter Username:", font=("Arial", 12), 
            fg="#5B3A29", bg="#F5F5DC").pack(pady=(10, 5), fill="x")
    username_entry = tk.Entry(login_frame, width=30, font=("Arial", 12), 
                            bd=2, relief="groove")
    username_entry.pack(pady=(0, 10), ipadx=5, ipady=5)
    username_entry.focus_set()
    
    # Password field
    tk.Label(login_frame, text="Enter Password:", font=("Arial", 12), 
            fg="#5B3A29", bg="#F5F5DC").pack(pady=(10, 5), fill="x")
    password_entry = tk.Entry(login_frame, width=30, font=("Arial", 12), 
                            bd=2, relief="groove", show="*")
    password_entry.pack(pady=(0, 10), ipadx=5, ipady=5)

    def register():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Username and Password cannot be empty")
            return
        
        if len(username) < 4:
            messagebox.showerror("Error", "Username must be at least 4 characters")
            return
        
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters")
            return
        
        conn = db_manager.get_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                         (username, hash_password(password)))
            conn.commit()
            messagebox.showinfo("Success", "Registration successful! Please complete your profile.")
            login_frame.after(100, lambda: collect_personal_details(root, username))
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists. Please choose a different one.")
        except Exception as e:
            messagebox.showerror("Database Error", f"Registration failed: {str(e)}")
        finally:
            conn.close()

    def authenticate():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        conn = db_manager.get_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username=? AND password=?", 
                         (username, hash_password(password)))
            user = cursor.fetchone()
            
            if user:
                messagebox.showinfo("Login Success", f"Welcome {username}!")
                login_frame.destroy()
                diary_ui_setup(root, username, user[0])  # Pass user_id
            else:
                messagebox.showerror("Login Failed", "Invalid username or password")
        except Exception as e:
            messagebox.showerror("Database Error", f"Login failed: {str(e)}")
        finally:
            conn.close()
    
    # Buttons
    button_frame = tk.Frame(login_frame, bg="#A67B5B")
    button_frame.pack(fill="x", pady=(10, 0))
    
    tk.Button(button_frame, text="Register", font=("Arial", 12), 
             fg="white", bg="#4C7031", command=register).pack(side="left", expand=True, fill="x")
    
    tk.Button(button_frame, text="Login", font=("Arial", 14, "bold"), 
             fg="white", bg="#8C4A2F", command=authenticate).pack(side="right", expand=True, fill="x")
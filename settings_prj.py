import tkinter as tk
from tkinter import messagebox, filedialog
import sqlite3
import hashlib
from PIL import Image, ImageTk
import os

conn = sqlite3.connect("eunoia.db")
cursor = conn.cursor()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def show_personal_details_embed(settings_window, user_id):
    for widget in settings_window.winfo_children():
        if getattr(widget, "_is_details_frame", False):
            widget.destroy()

    conn = sqlite3.connect("eunoia.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT username, full_name, age, gender, contact, email, bio
        FROM users
        WHERE id=?
    """, (user_id,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        tk.Label(settings_window, text="User not found.", fg="red").pack()
        return

    fields = [
        ("Username", user[0]),
        ("Full Name", user[1]),
        ("Age", user[2]),
        ("Gender", user[3]),
        ("Contact", user[4]),
        ("Email", user[5]),
        ("Bio", user[6])
    ]

    details_frame = tk.Frame(settings_window, bg="#f0f0f0", bd=2, relief="groove", padx=10, pady=10)
    details_frame._is_details_frame = True
    details_frame.pack(padx=20, pady=10, fill="x")

    tk.Label(details_frame, text="Personal Details", font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=5)

    for label, value in fields:
        frame = tk.Frame(details_frame, bg="#f0f0f0")
        frame.pack(fill="x", pady=2)
        tk.Label(frame, text=label + ":", font=("Arial", 10, "bold"), 
                bg="#f0f0f0", width=15, anchor="w").pack(side="left")
        tk.Label(frame, text=value if value else "Not provided", 
                font=("Arial", 10), bg="#f0f0f0", anchor="w").pack(side="left")

    tk.Button(details_frame, text="✏️ Edit Profile", 
             command=lambda: edit_profile(settings_window, user_id)).pack(pady=10)
def edit_profile(parent_window, user_id):
    edit_win = tk.Toplevel(parent_window)
    edit_win.title("Edit Profile")
    edit_win.geometry("400x500")
    edit_win.configure(bg="#F5F5DC")

    conn = sqlite3.connect("eunoia.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT full_name, age, gender, contact, email, bio
        FROM users WHERE id=?
    """, (user_id,))
    profile = cursor.fetchone()
    conn.close()

    fields = [
        {"label": "Full Name:", "key": "full_name", "value": profile[0] if profile and profile[0] else ""},
        {"label": "Email:", "key": "email", "value": profile[4] if profile and profile[4] else ""},
        {"label": "Age:", "key": "age", "value": profile[1] if profile and profile[1] else ""},
        {"label": "Gender:", "key": "gender", "value": profile[2] if profile and profile[2] else ""},
        {"label": "Contact:", "key": "contact", "value": profile[3] if profile and profile[3] else ""},
        {"label": "Bio:", "key": "bio", "value": profile[5] if profile and profile[5] else ""}
    ]

    entries = {}
    for field in fields:
        frame = tk.Frame(edit_win, bg="#F5F5DC")
        frame.pack(pady=5, fill="x", padx=20)
        
        tk.Label(frame, text=field["label"], font=("Arial", 10), 
                bg="#F5F5DC", fg="#5B3A29", width=15, anchor="w").pack(side="left")
        
        if field["key"] == "gender":
            gender_var = tk.StringVar(value=field["value"] if field["value"] else "Prefer not to say")
            option_menu = tk.OptionMenu(frame, gender_var, "Male", "Female", "Other", "Prefer not to say")
            option_menu.config(width=25, font=("Arial", 10))
            option_menu.pack(side="right")
            entries[field["key"]] = gender_var
        elif field["key"] == "bio":
            entry = tk.Text(frame, width=30, height=4, font=("Arial", 10))
            entry.insert("1.0", field["value"])
            entry.pack(side="right")
            entries[field["key"]] = entry
        else:
            entry = tk.Entry(frame, width=30, font=("Arial", 10))
            entry.insert(0, field["value"])
            entry.pack(side="right")
            entries[field["key"]] = entry

    def save_profile():
        updated_data = {
            "full_name": entries["full_name"].get(),
            "email": entries["email"].get(),
            "age": entries["age"].get(),
            "gender": entries["gender"].get(),
            "contact": entries["contact"].get(),
            "bio": entries["bio"].get("1.0", "end-1c") if hasattr(entries["bio"], "get") else entries["bio"].get(),
            "user_id": user_id
        }

        if not updated_data["full_name"] or not updated_data["email"]:
            messagebox.showerror("Error", "Full Name and Email are required fields")
            return

        conn = sqlite3.connect("eunoia.db")
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET full_name=?, email=?, age=?, gender=?, contact=?, bio=?
                WHERE id=?
            """, (
                updated_data["full_name"],
                updated_data["email"],
                int(updated_data["age"]) if updated_data["age"] else None,
                updated_data["gender"],
                updated_data["contact"],
                updated_data["bio"],
                updated_data["user_id"]
            ))
            conn.commit()
            messagebox.showinfo("Success", "Profile updated successfully!")
            edit_win.destroy()
            show_personal_details_embed(parent_window, user_id)
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "This email is already registered with another account")
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update profile: {str(e)}")
        finally:
            conn.close()

    tk.Button(edit_win, text="Save", font=("Arial", 12), 
             fg="white", bg="#4C7031", command=save_profile).pack(pady=10)

def reset_password(user_id):
    def update_password():
        new_password = new_password_entry.get()
        if new_password:
            hashed_password = hash_password(new_password)
            cursor.execute("UPDATE users SET password=? WHERE id=?", (hashed_password, user_id))
            conn.commit()
            messagebox.showinfo("Success", "Password reset successfully. You can now log in with your new password.")
            reset_window.destroy()
        else:
            messagebox.showerror("Error", "Password cannot be empty.")

    reset_window = tk.Toplevel()
    reset_window.title("Reset Password")
    reset_window.geometry("300x150")

    tk.Label(reset_window, text="Enter New Password:").pack(pady=5)
    new_password_entry = tk.Entry(reset_window, show="*")
    new_password_entry.pack(pady=5)

    tk.Button(reset_window, text="Update Password", command=update_password).pack(pady=10)

def fade_in(window):
    alpha = 0.0
    window.attributes('-alpha', alpha)
    def increase_alpha():
        nonlocal alpha
        alpha += 0.05
        if alpha <= 1.0:
            window.attributes('-alpha', alpha)
            window.after(10, increase_alpha)
    increase_alpha()

def show_loading_animation(canvas, size=30):
    angle = 0
    arc = canvas.create_arc(150-size, 100-size, 150+size, 100+size, start=0, extent=45, outline='#3498DB', width=6)
    animation_running = True

    def animate():
        nonlocal angle
        if animation_running:
            angle = (angle + 10) % 360
            canvas.itemconfig(arc, start=angle)
            canvas.after(50, animate)
    animate()

    return lambda: canvas.delete(arc)

def open_logout_window(root):
    overlay = tk.Toplevel(root)
    overlay.geometry(f"{root.winfo_width()}x{root.winfo_height()}+{root.winfo_x()}+{root.winfo_y()}")
    overlay.configure(bg="black")
    overlay.attributes('-alpha', 0.3)
    overlay.overrideredirect(True)

    # Create a larger confirmation dialog
    logout_window = tk.Toplevel(root)
    logout_window.title("Logout Confirmation")
    logout_window.geometry("450x300")
    logout_window.configure(bg="#F5F5DC", bd=2, relief="groove")
    logout_window.resizable(False, False)
    logout_window.attributes('-topmost', True)

 
    x_position = root.winfo_x() + (root.winfo_width() // 2) - 225
    y_position = root.winfo_y() + (root.winfo_height() // 2) - 150
    logout_window.geometry(f"450x300+{x_position}+{y_position}")

    fade_in(logout_window)


    message = "Are you sure you want to log out?"
    label = tk.Label(logout_window, text=message, font=("Arial", 18, "bold"), bg="#F5F5DC", fg="#4A4A4A", wraplength=400, justify="center")
    label.pack(pady=40)

    def confirm_logout():
        label.config(text="Logging you out... Please wait.", font=("Arial", 14))
        button_frame.pack_forget()
        canvas = tk.Canvas(logout_window, width=400, height=200, bg="#F5F5DC", highlightthickness=0)
        canvas.pack()
        stop_animation = show_loading_animation(canvas)
        root.after(2000, lambda: complete_logout(stop_animation))

    def complete_logout(stop_animation):
        stop_animation()
        logout_window.destroy()
        overlay.destroy()
        os._exit(0)

    def cancel_logout():
        logout_window.destroy()
        overlay.destroy()

    button_frame = tk.Frame(logout_window, bg="#F5F5DC")
    button_frame.pack(pady=20)

    confirm_button = tk.Button(button_frame, text="Yes, Logout", command=confirm_logout, bg="#D9534F", fg="white", width=12, relief=tk.FLAT, bd=2, font=("Arial", 12))
    confirm_button.pack(side=tk.LEFT, padx=30)

    cancel_button = tk.Button(button_frame, text="No, Cancel", command=cancel_logout, bg="#5CB85C", fg="white", width=12, relief=tk.FLAT, bd=2, font=("Arial", 12))
    cancel_button.pack(side=tk.LEFT, padx=30)


def open_full_screen_history(root, user_id):
    from diary import show_selected_entry

    full_screen = tk.Toplevel(root)
    full_screen.title("Full History")
    full_screen.geometry("800x500")
    tk.Label(full_screen, text="Full History", font=("Arial", 16, "bold")).pack()
    history_listbox = tk.Listbox(full_screen, bg="white", fg="black", font=("Arial", 12))
    history_listbox.pack(expand=True, fill="both", padx=10, pady=10)

    cursor.execute("SELECT entry_date FROM diary_entries WHERE user_id=? ORDER BY entry_date DESC", (user_id,))
    entries = cursor.fetchall()
    for entry in entries:
        history_listbox.insert(tk.END, entry[0])

    history_listbox.bind("<Double-Button-1>", lambda event: show_selected_entry(event, user_id, history_listbox))

def open_settings(root, user_id):
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("800x500")

    tk.Button(settings_window, text="👤 Personal Details", command=lambda: show_personal_details_embed(settings_window, user_id)).pack(pady=5)
    tk.Button(settings_window, text="🔑 Reset Password", command=lambda: reset_password(user_id)).pack(pady=5)

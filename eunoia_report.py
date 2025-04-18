import tkinter as tk
from time_analysis import plot_mood_trend
from mood_frequency_distibution import plot_mood_frequency_distribution
from load_mood_data import fetch_mood_data

def generate_mood_message(user_id, db_path="eunoia.db"):
    """Fetch latest mood and return a predefined message."""
    df = fetch_mood_data(user_id, db_path)
    
    if df.empty:
        return "No mood data found. How about writing a journal entry today? 😊"

    latest_mood_score = df.iloc[-1]["sentiment_score"]

    if latest_mood_score > 0.3:
        return "You are doing great today! Keep spreading positivity and enjoy the moment. 😊"
    elif latest_mood_score < -0.2:
        return "I know things might feel tough right now, but you're stronger than you think. Hang in there, brighter days are ahead. 💪"
    else:
        return "It's okay to have neutral days. Take it slow and let yourself recharge for what's ahead. 💫"

def report_view(user_id):
    from diary import apply_background
    report_window = tk.Toplevel()
    report_window.attributes("-fullscreen", True)
    
    image_path = "D:/Semester 2/spyder/package/final/report_bg.jpg"
    report_window.after(100, lambda: apply_background(report_window, image_path))

    mood_message = generate_mood_message(user_id)

    message_frame = tk.Frame(report_window, bg="#f3e1c9", bd=2, relief="ridge")
    message_frame.place(relx=0.5, rely=0.75, anchor="n")  # Moved below the buttons

    message_label = tk.Label(
        message_frame,
        text=mood_message,
        font=("Arial", 12, "bold"),
        bg="#f3e1c9",
        wraplength=600,  
        justify="center",
        padx=20,
        pady=10  
    )
    message_label.pack(fill="both", expand=True)

    message_frame.update_idletasks()
    message_frame.configure(
        width=message_label.winfo_width() + 20,
        height=message_label.winfo_height() + 5
    )


    message_frame.update_idletasks()  
    message_frame.configure(width=message_label.winfo_width(), height=message_label.winfo_height())

    button_style = {
        "font": ("Arial", 12, "bold"),
        "bg": "#f5e6cc",  
        "fg": "black",
        "bd": 3,  
        "relief": "raised",  
        "width": 25,  
        "height": 2 
    }

    btn_time_analysis = tk.Button(report_window, text="📊 Track your mood", command=lambda: plot_mood_trend(user_id), **button_style)
    btn_time_analysis.place(x=800, y=400)  

    btn_mood_distribution = tk.Button(report_window, text="📈Your peak emotion", command=lambda: plot_mood_frequency_distribution(user_id), **button_style)
    btn_mood_distribution.place(x=800, y=460)  

    btn_exit = tk.Button(report_window, text="❌ Exit", command=report_window.destroy, **button_style)
    btn_exit.place(x=800, y=520)
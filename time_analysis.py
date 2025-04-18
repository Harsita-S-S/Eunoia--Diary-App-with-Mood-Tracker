import matplotlib.pyplot as plt
from load_mood_data import fetch_mood_data  
def plot_mood_trend(user_id, db_path="eunoia.db"):
    df = fetch_mood_data(user_id, db_path)
    dates = df['entry_date']
    sentiment_scores = df['sentiment_score']
    colors = ["green" if score > 0.3 else "red" if score < -0.2 else "gray" for score in sentiment_scores]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

 
    ax1.plot(dates, sentiment_scores, marker='o', color='blue', label="Mood Trend")
    ax1.set_title("Mood Trend (Line Chart)")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Sentiment Score")
    ax1.grid(True)
    ax1.axhline(0, color='black', linestyle='--', linewidth=1)
    ax1.legend()

  
    ax2.bar(dates, sentiment_scores, color=colors, alpha=0.7)
    ax2.set_title("Mood Trend (Bar Chart)")
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Sentiment Score")
    ax2.axhline(0, color='black', linestyle='--', linewidth=1)  

    plt.xticks(rotation=45)
   
    plt.tight_layout()

    plt.show()


import matplotlib.pyplot as plt
from load_mood_data import fetch_mood_data

def categorize_mood(score):
    if score > 0.3:
        return 'Happy'
    elif score < -0.2:
        return 'Sad'
    else:
        return 'Neutral'

def plot_mood_frequency_distribution(user_id, db_path="eunoia.db"):
    df = fetch_mood_data(user_id, db_path="eunoia.db")
    df['mood_category'] = df['sentiment_score'].apply(categorize_mood)
    mood_counts = df['mood_category'].value_counts()

    most_frequent_mood = mood_counts.idxmax()

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(mood_counts, labels=mood_counts.index, autopct='%1.1f%%', startangle=90, colors=['green', 'gray', 'red'])
    ax.set_title("Mood Frequency Distribution")

    ax.text(0, -1.2, f"Most Frequent Mood: {most_frequent_mood}", 
            ha='center', va='center', fontsize=12, color='black', fontweight='bold')

    plt.show()


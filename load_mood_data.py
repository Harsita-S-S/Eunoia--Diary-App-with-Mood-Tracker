import sqlite3
import pandas as pd

def fetch_mood_data(user_id, db_path="eunoia.db"):
    """Fetches mood data and sentiment scores for visualization."""
    conn = sqlite3.connect(db_path)
    query = """
    SELECT entry_date, mood, sentiment_score FROM diary_entries 
    WHERE user_id = ? ORDER BY entry_date
    """
    df = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()
    
    df["entry_date"] = pd.to_datetime(df["entry_date"]) 
   

    return df


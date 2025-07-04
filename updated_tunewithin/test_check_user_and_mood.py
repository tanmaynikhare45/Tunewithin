import sqlite3
from datetime import datetime, timedelta

db_path = "C://Users//hp//Desktop//Nirmayee//updated_tunewithin//instance//tanmaydb.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

user_id = 3  # Change this to your real user ID!

today = datetime.today()
moods = ["positive", "neutral", "negative", "positive", "neutral", "negative", "positive"]

for i in range(7):
    mood_date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
    cursor.execute("""
        INSERT INTO mood_log (user_id, date, mood_label, entry_count, average_sentiment)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, mood_date, moods[i], 1, 0.5 if moods[i] == "positive" else -0.5 if moods[i] == "negative" else 0.0))

conn.commit()
conn.close()

print("✅ Inserted 7 mood logs.")

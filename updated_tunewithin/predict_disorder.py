# 📁 File: predict_disorder.py
import numpy as np
import os
import sqlite3
from keras.models import load_model
from sklearn.preprocessing import LabelEncoder
from datetime import datetime, timedelta

from utils import send_email_report

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

#emailinf function
def send_email_report(to_email, subject, body):
    from_email = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(from_email, password)
            server.send_message(msg)
        print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Email failed: {e}")



'''def insert_dummy_mood_logs(user_id=1):
    moods = ['Positive', 'Neutral', 'Negative', 'Positive', 'Neutral', 'Positive', 'Negative']
    today = datetime.now()
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "instance", "tanmaydb.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for i, mood in enumerate(moods):
        date_str = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        cursor.execute("""
            INSERT INTO mood_log (user_id, mood_label, date)
            VALUES (?, ?, ?)
        """, (user_id, mood, date_str))

    conn.commit()
    conn.close()
    print(f"✅ Inserted dummy mood logs for User {user_id}")

# Call it once to insert data
insert_dummy_mood_logs()'''

def run_disorder_prediction():

    # ✅ STEP 1: Construct model path and load GRU model
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, "ml_models", "gru_disorder.h5")
    gru_model = load_model(model_path)

    # ✅ STEP 2: Connect to the database
    db_path = os.path.join(base_dir, "instance", "tanmaydb.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # ✅ STEP 3: Define mood label to numeric value mapping
    mood_map = {"negative": -1, "neutral": 0, "positive": 1}

    # ✅ STEP 4: Select all users
    cursor.execute("SELECT id FROM user")
    users = cursor.fetchall()

    # ✅ STEP 5: Loop through users and make prediction
    for (user_id,) in users:
        # Get last 7 mood logs (most recent first)
        cursor.execute("""
            SELECT mood_label FROM mood_log
            WHERE user_id = ?
            ORDER BY date DESC
            LIMIT 7
        """, (user_id,))

        moods = cursor.fetchall()
        if len(moods) < 7:
            print(f"❌ User {user_id}: Not enough data for prediction.")
            continue

        # Map moods to numerical values
        mood_values = [mood_map.get(label[0].lower() if label[0] is not None else "neutral", 0) for label in moods]
        mood_values.reverse()  # GRU expects chronological order

        # Prepare input for GRU
        X_user = np.array(mood_values).reshape(1, 7, 1)

        # Make prediction
        gru_pred = gru_model.predict(X_user)

        # Decode prediction
        label_encoder = LabelEncoder()
        label_encoder.classes_ = np.array(["Bipolar", "Depression", "GAD", "NA"])
        predicted_index = np.argmax(gru_pred[0])
        predicted_label = label_encoder.inverse_transform([predicted_index])[0]

        # ✅ STEP 6: Store result in disorder table
        cursor.execute("""
            INSERT INTO disorder_prediction (user_id, predicted_disorder, probability_bipolar, probability_depression, probability_gad, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            predicted_label,
            float(gru_pred[0][0]),
            float(gru_pred[0][1]),
            float(gru_pred[0][2]),
            datetime.utcnow()
        ))


        # Step: Get last 7 mood logs (date + label)
        cursor.execute("""
            SELECT date, mood_label FROM mood_log
            WHERE user_id = ? 
            ORDER BY date DESC 
            LIMIT 7
        """, (user_id,))
        weekly_moods = cursor.fetchall()


        # Compose email report body (mood table + prediction)
        message_body = f"""
        🧠 Weekly Mental Health Report for User {user_id}

        📅 Mood Log (Last 7 Days):
        ---------------------------------------
        |     Date     |      Mood Label      |
        ---------------------------------------
        """
        for date, mood in weekly_moods:
            message_body += f"| {date:<12} | {mood:<20} |\n"

        message_body += f"""---------------------------------------

        📊 Disorder Prediction:
        Predicted Disorder: {predicted_label}
        Probabilities:
        - Bipolar: {gru_pred[0][0]:.2f}
        - Depression: {gru_pred[0][1]:.2f}
        - GAD: {gru_pred[0][2]:.2f}
        """

        # Preview report (for now)
        print(message_body)

        # Fetch trusted contact's email for this user
        cursor.execute("SELECT email FROM trusted_contact WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        to_email = result[0] if result and result[0] else None

        # Send email if address is available
        if to_email:
            send_email_report(
                to_email=to_email,
                subject="🧠 Weekly Mental Health Report",
                body=message_body
            )
        else:
            print(f"⚠️ No trusted email set for User {user_id}. Skipping email.")

        # 🔄 Send report to the user as well
        cursor.execute("SELECT email FROM user WHERE id = ?", (user_id,))
        user_email_result = cursor.fetchone()
        user_email = user_email_result[0] if user_email_result else None

        if user_email:
            send_email_report(
                to_email=user_email,
                subject="🧠 Your Weekly Mental Health Report",
                body=message_body
            )
            print(f"📩 Sent to user: {user_email}")
        else:
            print(f"⚠️ No email found for User {user_id}. Skipping user email.")


        conn.commit()
        print(f"✅ User {user_id}: Predicted {predicted_label}")

    conn.close()





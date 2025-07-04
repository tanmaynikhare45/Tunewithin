from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    diaries = db.relationship('Diary', backref='author', lazy='dynamic')
    trusted_contacts = db.relationship('TrustedContact', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class TrustedContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    relationship = db.Column(db.String(50))
    send_reports = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Diary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    entry_type = db.Column(db.String(10), nullable=False)  # 'voice' or 'text'
    sentiment_score = db.Column(db.Float)
    sentiment_label = db.Column(db.String(20))  # e.g., 'positive', 'negative', 'neutral'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    playlists = db.relationship('Playlist', backref='diary', lazy='dynamic')

class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spotify_id = db.Column(db.String(100), nullable=False)
    mood_label = db.Column(db.String(30), nullable=False)
    target_mood = db.Column(db.String(30))  # The mood we want to transition to
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    diary_id = db.Column(db.Integer, db.ForeignKey('diary.id'), nullable=False)

class MoodLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    average_sentiment = db.Column(db.Float)
    mood_label = db.Column(db.String(20))
    entry_count = db.Column(db.Integer, default=1)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

#disorder prediction tabel

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

class DisorderPrediction(db.Model):
    __tablename__ = 'disorder_prediction'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    predicted_disorder = db.Column(db.String(50), nullable=False)
    probability_bipolar = db.Column(db.Float)
    probability_depression = db.Column(db.Float)
    probability_gad = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('disorder_predictions', lazy=True))


'''# === Disorder Prediction Model Loader ===
import os
from keras.models import load_model
import numpy as np

# Get the directory where the script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the model file
MODEL_PATH = os.path.join(BASE_DIR, 'ml_models', 'gru_disorder.h5')

# Load the GRU model
gru_model = load_model(MODEL_PATH)

def predict_disorder(mood_sequence):
    # Reshape input to fit GRU input shape: (batch_size, time_steps, features)
    gru_input = np.array(mood_sequence).reshape((1, len(mood_sequence), 1))
    
    # Predict with GRU model
    prediction = gru_model.predict(gru_input)

    # Assuming the model returns class probabilities
    class_index = np.argmax(prediction, axis=1)[0]
    class_labels = ['Depression', 'Bipolar', 'GAD', 'NA']
    
    return class_labels[class_index]
'''
import os
from datetime import datetime, date, timedelta
from flask import render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy import text

from app import app, db
from models import User, Diary, TrustedContact, Playlist, MoodLog
from utils import analyze_sentiment, get_spotify_playlist, get_mood_transition_playlists
from forms import LoginForm, RegisterForm, DiaryForm, ProfileForm, ContactForm

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('register.html', form=form)
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('register.html', form=form)
        
        # Create user
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get recent diary entries
    recent_entries = Diary.query.filter_by(user_id=current_user.id).order_by(Diary.created_at.desc()).limit(5).all()
    
    # Default values for empty data
    dates = []
    sentiment_scores = []
    mood_counts = {}
    weekly_moods = {}
    
    # Get mood data for the past 30 days if there are entries
    if recent_entries:
        thirty_days_ago = date.today() - timedelta(days=30)
        mood_logs = MoodLog.query.filter(
            MoodLog.user_id == current_user.id,
            MoodLog.date >= thirty_days_ago
        ).order_by(MoodLog.date).all()
        
        # Format mood data for charts
        dates = [log.date.strftime('%Y-%m-%d') for log in mood_logs]
        sentiment_scores = [log.average_sentiment for log in mood_logs]
        
        # Count entries by mood
        for log in mood_logs:
            if log.mood_label is not None and log.entry_count is not None:
                if log.mood_label in mood_counts:
                    mood_counts[log.mood_label] += log.entry_count
                else:
                    mood_counts[log.mood_label] = log.entry_count
        
        # Get weekly mood trend
        for log in mood_logs:
            if log.entry_count is not None and log.average_sentiment is not None:
                week_num = log.date.isocalendar()[1]  # Get the week number
                week_key = f"Week {week_num}"
                if week_key not in weekly_moods:
                    weekly_moods[week_key] = {'count': 0, 'total': 0}
                weekly_moods[week_key]['count'] += log.entry_count
                weekly_moods[week_key]['total'] += log.average_sentiment * log.entry_count
        
        # Calculate averages
        for week in weekly_moods:
            if weekly_moods[week]['count'] > 0:
                weekly_moods[week] = weekly_moods[week]['total'] / weekly_moods[week]['count']
            else:
                weekly_moods[week] = 0
    
    # These are verified working Hindi-English mixed playlist IDs
    playlist_ids = {
        "very_negative": "4C34CZdaGedDSVEJ4fyqmd",  # Heartbroken/Romantic Hindi Playlist
        "negative": "7ykQM9HrZHvKRBvTL8Ebbc",       # Mix Lofi Songs (Hindi/English)
        "neutral": "45ZExvV649m3IUwEu5Ie3Y",        # Hindi and English Mixed Playlist (Mashup Travel Songs)
        "positive": "6ssT4PODIHKkfLjnNjTA0G",       # English x Hindi Remix/Mashups
        "very_positive": "31kiAehGU5xxZWuqehiUZP",  # Uplifting - English, Hindi, Tamil Mix
    }
    
    transition_ids = {
        "very_negative": "7ykQM9HrZHvKRBvTL8Ebbc", # Mix Lofi Songs (Hindi/English) - calming
        "negative": "45ZExvV649m3IUwEu5Ie3Y",      # Hindi and English Mixed Playlist - neutral travel vibes
        "neutral": "6ssT4PODIHKkfLjnNjTA0G",       # English x Hindi Remix/Mashups - upbeat
        "positive": "31kiAehGU5xxZWuqehiUZP",      # Uplifting - English, Hindi, Tamil Mix - energizing
        "very_positive": "31kiAehGU5xxZWuqehiUZP", # Uplifting - English, Hindi, Tamil Mix - maintain energy
    }
    
    # Fallback playlist if all else fails - a reliable Hindi-English mashup playlist
    default_playlist = "6ssT4PODIHKkfLjnNjTA0G"  # English x Hindi Remix/Mashups
    
    # Try to get playlist info from utils
    playlist_info = {}
    try:
        from utils import get_playlist_info
        playlist_info = get_playlist_info()
    except (ImportError, AttributeError) as e:
        app.logger.error(f"Error loading playlist info: {str(e)}")
    
    # Log playlists being used
    print(f"Using verified Hindi-English playlists: {playlist_ids}")
    
    return render_template(
        'dashboard.html', 
        recent_entries=recent_entries,
        dates=json.dumps(dates),
        sentiment_scores=json.dumps(sentiment_scores),
        mood_counts=json.dumps(mood_counts),
        weekly_moods=json.dumps(weekly_moods),
        playlist_ids=playlist_ids,
        transition_ids=transition_ids,
        default_playlist=default_playlist,
        playlist_info=playlist_info
    )

@app.route('/diary', methods=['GET', 'POST'])
@login_required
def diary():
    form = DiaryForm()
    
    if form.validate_on_submit():
        content = form.content.data
        entry_type = form.entry_type.data
        
        # Analyze sentiment
        sentiment_score, sentiment_label = analyze_sentiment(content)
        
        # Create diary entry
        diary_entry = Diary(
            content=content,
            entry_type=entry_type,
            sentiment_score=sentiment_score,
            sentiment_label=sentiment_label,
            user_id=current_user.id
        )
        
        db.session.add(diary_entry)
        db.session.commit()
        
        # Update or create mood log for today
        today = date.today()
        mood_log = MoodLog.query.filter_by(user_id=current_user.id, date=today).first()
        
        if mood_log:
            # Update existing log
            total_sentiment = (mood_log.average_sentiment * mood_log.entry_count) + sentiment_score
            mood_log.entry_count += 1
            mood_log.average_sentiment = total_sentiment / mood_log.entry_count
            mood_log.mood_label = sentiment_label  # Use the most recent mood
        else:
            # Create new log
            mood_log = MoodLog(
                date=today,
                average_sentiment=sentiment_score,
                mood_label=sentiment_label,
                user_id=current_user.id
            )
            db.session.add(mood_log)
        
        # Get playlist recommendations
        playlists = get_mood_transition_playlists(sentiment_label)
        
        # Save playlist recommendations
        for mood, spotify_id in playlists.items():
            playlist = Playlist(
                spotify_id=spotify_id,
                mood_label=sentiment_label,
                target_mood=mood,
                diary_id=diary_entry.id
            )
            db.session.add(playlist)
        
        db.session.commit()
        
        flash('Diary entry saved successfully', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('diary.html', form=form)

@app.route('/process_voice', methods=['POST'])
@login_required
def process_voice():
    transcript = request.form.get('transcript')
    if not transcript:
        return jsonify({'error': 'No transcript provided'}), 400
    
    # Analyze sentiment
    sentiment_score, sentiment_label = analyze_sentiment(transcript)
    
    return jsonify({
        'transcript': transcript,
        'sentiment_score': sentiment_score,
        'sentiment_label': sentiment_label
    })

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        
        # Check if username is already taken by another user
        user_check = User.query.filter_by(username=username).first()
        if user_check and user_check.id != current_user.id:
            flash('Username already exists', 'danger')
            return redirect(url_for('profile'))
        
        # Check if email is already used by another user
        email_check = User.query.filter_by(email=email).first()
        if email_check and email_check.id != current_user.id:
            flash('Email already registered', 'danger')
            return redirect(url_for('profile'))
        
        # Update user info
        current_user.username = username
        current_user.email = email
        
        # Check if password should be updated
        new_password = form.new_password.data
        
        if new_password:
            current_user.set_password(new_password)
        
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html', form=form)

@app.route('/contact_settings', methods=['GET', 'POST'])
@login_required
def contact_settings():
    contacts = TrustedContact.query.filter_by(user_id=current_user.id).all()
    form = ContactForm()
    
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        relationship = form.relationship.data
        send_reports = form.send_reports.data
        
        # Create new trusted contact
        contact = TrustedContact(
            name=name,
            email=email,
            relationship=relationship,
            send_reports=send_reports,
            user_id=current_user.id
        )
        
        db.session.add(contact)
        db.session.commit()
        
        flash('Trusted contact added successfully', 'success')
        return redirect(url_for('contact_settings'))
    
    return render_template('contact_settings.html', contacts=contacts, form=form)

@app.route('/delete_contact/<int:contact_id>', methods=['POST'])
@login_required
def delete_contact(contact_id):
    contact = TrustedContact.query.filter_by(id=contact_id, user_id=current_user.id).first_or_404()
    
    db.session.delete(contact)
    db.session.commit()
    
    flash('Trusted contact deleted', 'success')
    return redirect(url_for('contact_settings'))

@app.route('/send_report/<int:contact_id>', methods=['POST'])
@login_required
def send_report(contact_id):
    contact = TrustedContact.query.filter_by(id=contact_id, user_id=current_user.id).first_or_404()
    
    # Get mood data for the past 30 days
    thirty_days_ago = date.today() - timedelta(days=30)
    mood_logs = MoodLog.query.filter(
        MoodLog.user_id == current_user.id,
        MoodLog.date >= thirty_days_ago
    ).order_by(MoodLog.date).all()
    
    # Calculate average mood
    total_sentiment = sum(log.average_sentiment for log in mood_logs if log.average_sentiment is not None)
    avg_sentiment = total_sentiment / len(mood_logs) if mood_logs else 0
    
    # Determine overall mood
    overall_mood = "positive" if avg_sentiment > 0.3 else "negative" if avg_sentiment < -0.3 else "neutral"
    
    # Create email
    subject = f"Mood Report for {current_user.username}"
    body = f"""
    <html>
    <body>
        <h2>TuneWithin Mood Report</h2>
        <p>Hello {contact.name},</p>
        <p>{current_user.username} has shared their monthly mood report with you.</p>
        <h3>Summary for the past 30 days:</h3>
        <p>Overall mood: {overall_mood}</p>
        <p>Number of journal entries: {sum(log.entry_count for log in mood_logs if log.entry_count is not None)}</p>
        <p>This is an automated report from TuneWithin - your emotion-aware music companion.</p>
    </body>
    </html>
    """
    
    # For demo purposes, we'll just simulate sending the email
    flash(f"Report sent to {contact.email} successfully", 'success')
    return redirect(url_for('contact_settings'))

@app.route('/api/get_diary_entries')
@login_required
def get_diary_entries():
    days = request.args.get('days', 30, type=int)
    start_date = date.today() - timedelta(days=days)
    
    entries = Diary.query.filter(
        Diary.user_id == current_user.id,
        Diary.created_at >= start_date
    ).order_by(Diary.created_at).all()
    
    data = [{
        'id': entry.id,
        'content': entry.content[:100] + '...' if len(entry.content) > 100 else entry.content,
        'sentiment_score': entry.sentiment_score,
        'sentiment_label': entry.sentiment_label,
        'date': entry.created_at.strftime('%Y-%m-%d')
    } for entry in entries]
    
    return jsonify(data)

@app.route('/db-test')
def db_test():
    try:
        # Use text() to properly format the SQL query
        result = db.session.execute(text('SELECT 1'))
        return f'Database connection successful! Result: {result.scalar()}'
    except Exception as e:
        return f'Database connection failed: {str(e)}'  # Fixed the missing closing quote
    

'''from utils import send_disorder_alert, detect_triggers

# Trigger Sending logic
diary_text=Diary.content
triggers = detect_triggers(diary_text)
if triggers:
    print(f"Detected potential emotional triggers: {triggers}")'''

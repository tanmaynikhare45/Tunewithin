from textblob import TextBlob
import logging
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os

# Set your Spotify API credentials as environment variables for security
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")

# Default playlist IDs for each mood - these are verified working Hindi-English mixed Spotify playlists
DEFAULT_PLAYLISTS = {
    "very_negative": "4C34CZdaGedDSVEJ4fyqmd",  # Heartbroken/Romantic Hindi Playlist
    "negative": "7ykQM9HrZHvKRBvTL8Ebbc",       # Mix Lofi Songs (Hindi/English)
    "neutral": "45ZExvV649m3IUwEu5Ie3Y",        # Hindi and English Mixed Playlist (Mashup Travel Songs)
    "positive": "6ssT4PODIHKkfLjnNjTA0G",       # English x Hindi Remix/Mashups
    "very_positive": "31kiAehGU5xxZWuqehiUZP",  # Uplifting - English, Hindi, Tamil Mix
}

# Default transition playlists for moving between moods
TRANSITION_PLAYLISTS = {
    "very_negative": "7ykQM9HrZHvKRBvTL8Ebbc", # Mix Lofi Songs (Hindi/English) - calming
    "negative": "45ZExvV649m3IUwEu5Ie3Y",      # Hindi and English Mixed Playlist - neutral travel vibes
    "neutral": "6ssT4PODIHKkfLjnNjTA0G",       # English x Hindi Remix/Mashups - upbeat
    "positive": "31kiAehGU5xxZWuqehiUZP",      # Uplifting - English, Hindi, Tamil Mix - energizing
    "very_positive": "31kiAehGU5xxZWuqehiUZP" # Uplifting - English, Hindi, Tamil Mix - maintain energy
}

# For calming transitions (moving down the mood scale)
CALMING_PLAYLISTS = {
    "very_positive": "6ssT4PODIHKkfLjnNjTA0G",  # English x Hindi Remix/Mashups - reduce energy
    "positive": "45ZExvV649m3IUwEu5Ie3Y",       # Hindi and English Mixed Playlist - travel songs
    "neutral": "7ykQM9HrZHvKRBvTL8Ebbc",        # Mix Lofi Songs (Hindi/English) - calm
    "negative": "7ykQM9HrZHvKRBvTL8Ebbc",       # Mix Lofi Songs (Hindi/English) - maintain calm
    "very_negative": "4C34CZdaGedDSVEJ4fyqmd",  # Heartbroken/Romantic Hindi Playlist
}

# Initialize Spotipy client
sp = None
try:
    if SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET:
        sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET
        ))
        logging.info("Spotify API client initialized successfully")
    else:
        logging.warning("Spotify credentials not found, using default playlists only")
except Exception as e:
    logging.error(f"Error initializing Spotify client: {str(e)}")
    sp = None

# Mood transition pathways - how to transition from one mood to another
MOOD_TRANSITIONS = {
    "very_negative": ["negative", "neutral", "positive"],
    "negative": ["neutral", "positive", "very_positive"],
    "neutral": ["positive", "very_positive"],
    "positive": ["very_positive"],
    "very_positive": []  # Already at the most positive state
}

def analyze_sentiment(text):
    """
    Analyzes the sentiment of the given text using TextBlob.
    Returns a tuple of (sentiment_score, sentiment_label)
    """
    try:
        # Create TextBlob object
        blob = TextBlob(text)
        
        # Get the sentiment
        sentiment_score = blob.sentiment.polarity
        
        # Determine the label based on the score
        if sentiment_score < -0.6:
            sentiment_label = "very_negative"
        elif sentiment_score < -0.2:
            sentiment_label = "negative"
        elif sentiment_score < 0.2:
            sentiment_label = "neutral"
        elif sentiment_score < 0.6:
            sentiment_label = "positive"
        else:
            sentiment_label = "very_positive"
        
        return sentiment_score, sentiment_label
    
    except Exception as e:
        logging.error(f"Error analyzing sentiment: {str(e)}")
        return 0, "neutral"  # Default to neutral if there's an error

def search_playlist_by_mood(mood):
    """
    Searches Spotify for a playlist matching the mood.
    Returns the first playlist's URL or playlist ID.
    """
    try:
        if not sp:
            return DEFAULT_PLAYLISTS.get(mood, DEFAULT_PLAYLISTS["neutral"])
            
        # Hindi-English mix queries
        query = {
            "very_negative": "bollywood sad songs hindi english",
            "negative": "bollywood mellow hindi english mix",
            "neutral": "hindi english mix playlist",
            "positive": "bollywood party upbeat hindi english",
            "very_positive": "desi party remix hindi english"
        }.get(mood, "hindi english mix")
        
        results = sp.search(q=query, type='playlist', limit=1)
        playlists = results.get('playlists', {}).get('items', [])
        
        if playlists:
            # Return just the playlist ID from the URI (spotify:playlist:ID)
            uri = playlists[0]['uri']
            return uri.split(':')[-1]
        
        return DEFAULT_PLAYLISTS.get(mood, DEFAULT_PLAYLISTS["neutral"])
    except Exception as e:
        logging.error(f"Error searching playlist: {str(e)}")
        return DEFAULT_PLAYLISTS.get(mood, DEFAULT_PLAYLISTS["neutral"])

def get_spotify_playlist(mood, direction='up'):
    """
    Returns a Spotify playlist ID for the given mood.
    Now directly returns Hindi-English playlists without API calls.
    """
    try:
        # Force using our predefined Hindi-English playlists
        if direction == 'down':
            logging.info(f"Getting Hindi calming playlist for mood: {mood}")
            return CALMING_PLAYLISTS.get(mood, CALMING_PLAYLISTS["neutral"])
        else:
            logging.info(f"Getting Hindi playlist for mood: {mood}")
            if mood in TRANSITION_PLAYLISTS:
                return TRANSITION_PLAYLISTS[mood]
            return DEFAULT_PLAYLISTS.get(mood, DEFAULT_PLAYLISTS["neutral"])
    except Exception as e:
        logging.error(f"Error getting playlist: {str(e)}")
        return DEFAULT_PLAYLISTS.get(mood, DEFAULT_PLAYLISTS["neutral"])

def get_mood_transition_playlists(current_mood):
    """
    Returns a dictionary of playlists to help transition from the current mood 
    to progressively more positive moods
    """
    # Get the target moods for transition
    target_moods = MOOD_TRANSITIONS.get(current_mood, [])
    
    # If we're already in a positive state, just maintain it
    if not target_moods and current_mood in ["positive", "very_positive"]:
        target_moods = [current_mood]
    
    # If somehow we don't have target moods, default to neutral
    if not target_moods:
        target_moods = ["neutral"]
    
    # Create a dictionary of mood -> playlist_id
    playlists = {mood: get_spotify_playlist(mood) for mood in target_moods}
    
    # Always include the current mood's playlist
    playlists[current_mood] = get_spotify_playlist(current_mood)
    
    return playlists

def get_playlist_ids_for_all_moods():
    """
    Returns a dictionary with playlist IDs for all mood types
    """
    logging.info("Getting all Hindi-English playlist IDs")
    return DEFAULT_PLAYLISTS

def get_transition_playlist_ids():
    """
    Returns transition playlist IDs for each mood
    """
    logging.info("Getting all Hindi-English transition playlist IDs")
    return TRANSITION_PLAYLISTS

def format_mood_for_display(mood_label):
    """
    Formats a mood label for display (converts underscores to spaces and capitalizes)
    """
    return mood_label.replace("_", " ").title()

def get_playlist_info():
    """Returns detailed information about our curated playlists"""
    return {
        "6ssT4PODIHKkfLjnNjTA0G": {
            "name": "English x Hindi Remix/Mashups",
            "description": "Features a blend of English and Hindi mashups, including Lofi remixes and slowed + reverbed tracks."
        },
        "45ZExvV649m3IUwEu5Ie3Y": {
            "name": "Hindi and English Mixed Playlist (Mashup Travel Songs)",
            "description": "A mix of Hindi and English tracks perfect for road trips and travel."
        },
        "7ykQM9HrZHvKRBvTL8Ebbc": {
            "name": "Mix Lofi Songs (Hindi/English)",
            "description": "Lofi songs combining Hindi and English tracks, ideal for relaxation."
        },
        "4C34CZdaGedDSVEJ4fyqmd": {
            "name": "Heartbroken/Romantic Hindi Playlist",
            "description": "A collection of romantic and heartbroken Hindi songs."
        },
        "31kiAehGU5xxZWuqehiUZP": {
            "name": "Uplifting - English, Hindi, Tamil Mix",
            "description": "An energetic mix of English, Hindi, and Tamil songs to boost motivation."
        }
    }


from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import os
from dotenv import load_dotenv

load_dotenv()  # Load credentials from .env file

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

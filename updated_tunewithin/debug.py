from dotenv import load_dotenv
load_dotenv()

from utils import get_spotify_playlist, get_playlist_ids_for_all_moods, get_transition_playlist_ids
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_hindi_playlist_recommendations():
    """Test that we're getting Hindi-English mixed playlists"""
    
    # Test individual mood playlists
    moods = ["very_negative", "negative", "neutral", "positive", "very_positive"]
    
    logger.info("Testing Hindi playlist recommendations:")
    
    for mood in moods:
        playlist_id = get_spotify_playlist(mood)
        logger.info(f"Mood: {mood:15} | Playlist ID: {playlist_id}")
    
    # Test getting all playlists
    all_playlists = get_playlist_ids_for_all_moods()
    logger.info(f"\nAll Hindi playlists: {all_playlists}")
    
    # Test transition playlists
    transition_playlists = get_transition_playlist_ids()
    logger.info(f"\nAll Hindi transition playlists: {transition_playlists}")
    
    # Verify against known values
    expected_playlist_id = "37i9dQZF1DXdSjVZQzv2tl"  # Hindi Party for positive mood
    actual_playlist_id = get_spotify_playlist("positive")
    
    if actual_playlist_id == expected_playlist_id:
        logger.info("\n✅ SUCCESS: Hindi playlist recommendations are working correctly")
    else:
        logger.error(f"\n❌ ERROR: Expected Hindi playlist {expected_playlist_id} but got {actual_playlist_id}")

if __name__ == "__main__":
    test_hindi_playlist_recommendations()

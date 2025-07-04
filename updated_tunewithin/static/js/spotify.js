/**
 * Spotify integration for TuneWithin
 * Handles playlist loading and mood transitions
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Spotify integration initialized with verified Hindi-English playlists');
    
    // Initialize playlist tabs
    initPlaylistTabs();
    
    // Add event listeners for mood direction buttons
    document.getElementById('elevate-mood')?.addEventListener('click', function() {
        changeMoodDirection('up');
    });
    
    document.getElementById('calm-mood')?.addEventListener('click', function() {
        changeMoodDirection('down');
    });
});

/**
 * Initializes the playlist tabs
 */
function initPlaylistTabs() {
    console.log('Initializing playlist tabs');
    
    // Bootstrap 5 has built-in tab functionality, but we'll add our own for robustness
    const tabButtons = document.querySelectorAll('.playlist-tab-button');
    const tabContents = document.querySelectorAll('.tab-pane');
    
    // Ensure the tab system is correctly set up
    tabButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get the target panel
            const targetSelector = this.getAttribute('data-bs-target');
            const targetPanel = document.querySelector(targetSelector);
            
            if (!targetPanel) return;
            
            // Deactivate all tabs and panels
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(panel => {
                panel.classList.remove('show', 'active');
            });
            
            // Activate this tab and panel
            this.classList.add('active');
            targetPanel.classList.add('show', 'active');
        });
    });
    
    // Ensure at least one tab is active
    const activeTab = document.querySelector('.playlist-tab-button.active');
    if (!activeTab && tabButtons.length > 0) {
        tabButtons[0].click(); // Trigger click on first tab
    }
}

/**
 * Changes the mood direction for playlists
 * @param {string} direction - 'up' for elevating mood, 'down' for calming
 */
function changeMoodDirection(direction) {
    console.log(`Changing mood direction: ${direction}`);
    
    // Update active state of buttons
    const elevateBtn = document.getElementById('elevate-mood');
    const calmBtn = document.getElementById('calm-mood');
    
    if (elevateBtn && calmBtn) {
        if (direction === 'up') {
            elevateBtn.classList.add('active');
            calmBtn.classList.remove('active');
        } else {
            calmBtn.classList.add('active');
            elevateBtn.classList.remove('active');
        }
    }
    
    // Get current mood from the page
    const moodLabelElement = document.getElementById('current-mood-label');
    if (!moodLabelElement) return;
    
    const currentMood = moodLabelElement.textContent.toLowerCase().replace(' ', '_');
    console.log(`Current mood: ${currentMood}`);
    
    // Get the iframe container
    const container = document.getElementById('transition-playlist-container');
    if (!container) return;
    
    // Get the iframe
    const iframe = container.querySelector('iframe');
    if (!iframe) return;
    
    // Hard-coded verified Hindi-English mixed playlists for different moods
    const playlistIds = {
        up: {
            very_negative: "7ykQM9HrZHvKRBvTL8Ebbc", // Mix Lofi Songs (Hindi/English) - calming
            negative: "45ZExvV649m3IUwEu5Ie3Y",      // Hindi and English Mixed Playlist - travel vibes
            neutral: "6ssT4PODIHKkfLjnNjTA0G",       // English x Hindi Remix/Mashups - upbeat
            positive: "31kiAehGU5xxZWuqehiUZP",      // Uplifting - English, Hindi, Tamil Mix
            very_positive: "31kiAehGU5xxZWuqehiUZP", // Uplifting - English, Hindi, Tamil Mix - maintain
        },
        down: {
            very_positive: "6ssT4PODIHKkfLjnNjTA0G", // English x Hindi Remix/Mashups - reduce energy
            positive: "45ZExvV649m3IUwEu5Ie3Y",      // Hindi and English Mixed Playlist - travel songs
            neutral: "7ykQM9HrZHvKRBvTL8Ebbc",       // Mix Lofi Songs (Hindi/English) - calm 
            negative: "7ykQM9HrZHvKRBvTL8Ebbc",      // Mix Lofi Songs (Hindi/English) - maintain calm
            very_negative: "4C34CZdaGedDSVEJ4fyqmd", // Heartbroken/Romantic Hindi Playlist
        }
    };
    
    // Get the right playlist ID
    const directionType = direction === 'up' ? 'up' : 'down';
    const playlistId = playlistIds[directionType][currentMood] || "6ssT4PODIHKkfLjnNjTA0G"; // Default to English x Hindi Remix/Mashups
    
    console.log(`Selected Hindi playlist ID: ${playlistId} for ${direction} direction`);
    
    // Update the iframe src
    const newSrc = `https://open.spotify.com/embed/playlist/${playlistId}`;
    if (iframe.src !== newSrc) {
        console.log(`Updating iframe to Hindi playlist: ${newSrc}`);
        iframe.src = newSrc;
        // Add animation to show change
        iframe.classList.add('playlist-changed');
        setTimeout(() => iframe.classList.remove('playlist-changed'), 1000);
    }
}

/**
 * Try to fix any broken Spotify embeds on the page
 */
function fixSpotifyEmbeds() {
    // Get all Spotify iframes
    const spotifyIframes = document.querySelectorAll('iframe[src*="spotify.com"]');
    
    // Check each iframe
    spotifyIframes.forEach(iframe => {
        // Verified working Hindi-English playlists
        const verifiedPlaylists = [
            "6ssT4PODIHKkfLjnNjTA0G", // English x Hindi Remix/Mashups
            "45ZExvV649m3IUwEu5Ie3Y", // Hindi and English Mixed Playlist (Mashup Travel Songs)
            "7ykQM9HrZHvKRBvTL8Ebbc", // Mix Lofi Songs (Hindi/English)
            "4C34CZdaGedDSVEJ4fyqmd", // Heartbroken/Romantic Hindi Playlist
            "31kiAehGU5xxZWuqehiUZP"  // Uplifting - English, Hindi, Tamil Mix
        ];
        
        // Get current playlist ID from the iframe src
        const currentSrc = iframe.src;
        const playlistIdMatch = currentSrc.match(/playlist\/([a-zA-Z0-9]+)/);
        
        if (playlistIdMatch && playlistIdMatch[1]) {
            const currentPlaylistId = playlistIdMatch[1];
            
            // If current playlist is not in our verified list, replace with a random verified one
            if (!verifiedPlaylists.includes(currentPlaylistId)) {
                // Pick a random verified playlist
                const randomPlaylist = verifiedPlaylists[Math.floor(Math.random() * verifiedPlaylists.length)];
                const newSrc = currentSrc.replace(currentPlaylistId, randomPlaylist);
                console.log(`Replacing unverified playlist ${currentPlaylistId} with verified ${randomPlaylist}`);
                iframe.src = newSrc;
            }
        }
    });
}

/**
 * Handles errors with Spotify embeds
 */
window.addEventListener('error', function(e) {
    if (e.target.tagName === 'IFRAME' && e.target.src.includes('spotify.com')) {
        console.error('Spotify iframe error:', e);
        
        e.preventDefault();
        
        try {
            const iframe = e.target;
            // Use our verified playlist that definitely works
            iframe.src = "https://open.spotify.com/embed/playlist/6ssT4PODIHKkfLjnNjTA0G"; // English x Hindi Remix/Mashups
            
            // Show error message
            const container = iframe.parentElement;
            if (container) {
                const errorMsg = document.createElement('div');
                errorMsg.className = 'alert alert-warning mt-2 mb-0 py-2';
                errorMsg.innerHTML = 'Switched to English x Hindi Remix/Mashups playlist.';
                container.appendChild(errorMsg);
                
                setTimeout(() => errorMsg.remove(), 5000);
            }
        } catch (err) {
            console.error('Error recovering from Spotify iframe error:', err);
        }
    }
}, true);
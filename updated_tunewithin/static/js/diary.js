// Diary entry functionality

document.addEventListener('DOMContentLoaded', function() {
    // Setup voice recording
    setupVoiceRecording();
    
    // Setup textual sentiment analysis
    setupTextualSentimentAnalysis();
});

function setupVoiceRecording() {
    const recordButton = document.getElementById('record-button');
    const stopButton = document.getElementById('stop-button');
    const recordingIndicator = document.getElementById('recording-indicator');
    const audioPlayback = document.getElementById('audio-playback');
    const transcriptContainer = document.getElementById('transcript-container');
    const transcriptText = document.getElementById('transcript-text');
    const saveVoiceButton = document.getElementById('save-voice-button');
    const voiceContentInput = document.querySelector('#voice-entry #content');
    
    // Check if elements exist
    if (!recordButton || !stopButton || !recordingIndicator || 
        !audioPlayback || !transcriptContainer || !transcriptText || 
        !saveVoiceButton || !voiceContentInput) {
        console.error('Voice recording elements not found');
        return;
    }
    
    let mediaRecorder;
    let audioChunks = [];
    let recognition;
    let isRecording = false;
    
    // Check if browser supports speech recognition
    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        
        recognition.onresult = function(event) {
            let finalTranscript = '';
            let interimTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }
            
            // Update the transcript text
            transcriptText.textContent = finalTranscript || interimTranscript;
            
            // If we have a final transcript, update the content input
            if (finalTranscript) {
                voiceContentInput.value = finalTranscript;
                saveVoiceButton.disabled = false;
                analyzeSentiment(finalTranscript);
            }
        };
        
        recognition.onerror = function(event) {
            console.error('Speech recognition error:', event.error);
            if (event.error === 'no-speech') {
                alert('No speech was detected. Please try again.');
            } else if (event.error === 'audio-capture') {
                alert('No microphone was found. Please ensure your microphone is properly connected.');
            } else if (event.error === 'not-allowed') {
                alert('Permission to use microphone was denied. Please allow microphone access.');
            }
            stopRecording();
        };
        
        recognition.onend = function() {
            if (isRecording) {
                recognition.start();
            }
        };
    } else {
        console.error('Speech recognition is not supported in your browser. Please use Chrome or Edge.');
        recordButton.disabled = true;
    }
    
    // Initial state
    stopButton.style.display = 'none';
    recordingIndicator.style.display = 'none';
    
    function startRecording() {
        // Request permission to use the microphone
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                // Show recording UI
                recordButton.style.display = 'none';
                stopButton.style.display = 'inline-block';
                recordingIndicator.style.display = 'block';
                
                // Initialize media recorder
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];
                
                // Collect audio chunks
                mediaRecorder.addEventListener('dataavailable', event => {
                    audioChunks.push(event.data);
                });
                
                // When recording stops
                mediaRecorder.addEventListener('stop', () => {
                    // Create and play audio blob
                    const audioBlob = new Blob(audioChunks);
                    const audioUrl = URL.createObjectURL(audioBlob);
                    audioPlayback.src = audioUrl;
                    audioPlayback.classList.remove('d-none');
                });
                
                // Start recording
                mediaRecorder.start();
                isRecording = true;
                
                // Start speech recognition
                if (recognition) {
                    recognition.start();
                }
                
                // Show transcript container
                transcriptContainer.classList.remove('d-none');
                transcriptText.textContent = 'Listening...';
            })
            .catch(error => {
                console.error('Error accessing microphone:', error);
                alert('Error accessing microphone. Please ensure you have granted permission.');
            });
    }
    
    function stopRecording() {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
            isRecording = false;
            
            // Stop speech recognition
            if (recognition) {
                recognition.stop();
            }
            
            // Reset UI
            recordButton.style.display = 'inline-block';
            stopButton.style.display = 'none';
            recordingIndicator.style.display = 'none';
            
            // Stop all tracks
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
        }
    }
    
    // Record button click handler
    recordButton.addEventListener('click', startRecording);
    
    // Stop button click handler
    stopButton.addEventListener('click', stopRecording);
}

function setupTextualSentimentAnalysis() {
    const textInput = document.querySelector('#text-entry #content');
    const sentimentDisplay = document.querySelector('#text-entry #sentiment-display');
    
    if (!textInput || !sentimentDisplay) {
        return;
    }
    
    // Add input event listener with debounce
    let timeout;
    textInput.addEventListener('input', function() {
        clearTimeout(timeout);
        
        // Only analyze if there's meaningful content
        if (this.value.trim().length > 20) {
            timeout = setTimeout(() => {
                analyzeSentiment(this.value);
            }, 1000);
        } else {
            sentimentDisplay.innerHTML = '';
        }
    });
}

function analyzeSentiment(text) {
    // Find the active tab's sentiment display
    const activeTab = document.querySelector('.tab-pane.active');
    if (!activeTab) return;
    
    const sentimentDisplay = activeTab.querySelector('#sentiment-display');
    if (!sentimentDisplay) return;
    
    // Show loading state
    sentimentDisplay.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div><p class="mt-2">Analyzing your emotions...</p></div>';
    
    // Send the text to the server for analysis
    fetch('/process_voice', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCsrfToken()
        },
        body: 'transcript=' + encodeURIComponent(text)
    })
    .then(response => response.json())
    .then(data => {
        let displayHTML = '';
        
        // Display support messages if any flags were found
        if (data.support_resources) {
            data.support_resources.forEach(resource => {
                displayHTML += `
                    <div class="alert alert-warning mt-3">
                        <h5 class="alert-heading">${resource.title}</h5>
                        <p>${resource.message}</p>
                        <hr>
                        <p class="mb-0"><strong>Resources:</strong></p>
                        <ul class="mb-0">
                            ${resource.resources.map(r => `<li>${r}</li>`).join('')}
                        </ul>
                    </div>
                `;
            });
        }
        
        // Display the sentiment
        let moodClass;
        let moodIcon;
        
        if (data.sentiment_label === 'very_negative') {
            moodClass = 'danger';
            moodIcon = 'fa-sad-tear';
        } else if (data.sentiment_label === 'negative') {
            moodClass = 'warning';
            moodIcon = 'fa-sad-cry';
        } else if (data.sentiment_label === 'neutral') {
            moodClass = 'secondary';
            moodIcon = 'fa-meh';
        } else if (data.sentiment_label === 'positive') {
            moodClass = 'success';
            moodIcon = 'fa-smile';
        } else if (data.sentiment_label === 'very_positive') {
            moodClass = 'info';
            moodIcon = 'fa-laugh-beam';
        }
        
        const moodLabel = data.sentiment_label.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
        
        displayHTML += `
            <div class="alert alert-${moodClass} d-flex align-items-center">
                <i class="fas ${moodIcon} fa-2x me-3"></i>
                <div>
                    <strong>Detected Mood:</strong> ${moodLabel}
                    <div class="progress mt-2" style="height: 8px;">
                        <div class="progress-bar bg-${moodClass}" role="progressbar" style="width: ${Math.abs(data.sentiment_score * 100)}%" 
                            aria-valuenow="${Math.abs(data.sentiment_score * 100)}" aria-valuemin="0" aria-valuemax="100"></div>
                    </div>
                </div>
            </div>
        `;
        
        sentimentDisplay.innerHTML = displayHTML;
    })
    .catch(error => {
        console.error('Error analyzing sentiment:', error);
        sentimentDisplay.innerHTML = '<div class="alert alert-danger"></div>';
    });
}

function getCsrfToken() {
    // Get CSRF token from meta tag
    return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
}
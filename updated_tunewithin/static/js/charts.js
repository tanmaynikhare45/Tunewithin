// Enhanced interactive charts for TuneWithin

document.addEventListener('DOMContentLoaded', function() {
    // Get mood data from the hidden element
    const moodDataElement = document.getElementById('mood-data');
    
    if (!moodDataElement) {
        console.warn('Mood data element not found');
        return;
    }
    
    try {
        // Parse the data
        const dates = JSON.parse(moodDataElement.getAttribute('data-dates') || '[]');
        const sentimentScores = JSON.parse(moodDataElement.getAttribute('data-sentiment-scores') || '[]');
        const moodCounts = JSON.parse(moodDataElement.getAttribute('data-mood-counts') || '{}');
        const weeklyMoods = JSON.parse(moodDataElement.getAttribute('data-weekly-moods') || '{}');
        
        // Initialize charts
        if (document.getElementById('mood-trend-chart')) {
            initMoodTrendChart(dates, sentimentScores);
        }
        
        if (document.getElementById('mood-distribution-chart')) {
            initMoodDistributionChart(moodCounts);
        }
        
        if (document.getElementById('weekly-mood-chart')) {
            initWeeklyMoodChart(weeklyMoods);
        }
    } catch (error) {
        console.error('Error initializing charts:', error);
        displayChartError();
    }
    
    // Initialize time range dropdown
    const timeRangeDropdown = document.getElementById('timeRangeDropdown');
    if (timeRangeDropdown) {
        timeRangeDropdown.addEventListener('click', function(e) {
            if (e.target.classList.contains('dropdown-item')) {
                // Update button text
                document.querySelector('#timeRangeDropdown').innerText = e.target.innerText;
                
                // Remove active class from all items
                document.querySelectorAll('.dropdown-item').forEach(item => {
                    item.classList.remove('active');
                });
                
                // Add active class to selected item
                e.target.classList.add('active');
                
                // In a real app, we would fetch data for the selected time range
                // For now, we'll just show a notification
                showNotification(`Data updated for ${e.target.innerText}`, 'info');
            }
        });
    }
});

function displayChartError() {
    const containers = document.querySelectorAll('.chart-container');
    containers.forEach(container => {
        container.innerHTML = `
            <div class="text-center py-5">
                <div class="text-danger mb-3">
                    <i class="fas fa-exclamation-circle fa-3x"></i>
                </div>
                <h5>Error Loading Chart</h5>
                <p class="text-muted">There was a problem loading the chart data.</p>
                <button class="btn btn-sm btn-outline-secondary mt-2" onclick="window.location.reload()">
                    <i class="fas fa-sync-alt"></i> Retry
                </button>
            </div>
        `;
    });
}

function showNotification(message, type = 'success') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} notification-toast`;
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-info-circle me-2"></i>
            <span>${message}</span>
            <button type="button" class="btn-close ms-auto" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    // Add to the document
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => notification.classList.add('show'), 10);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function initMoodTrendChart(dates, sentimentScores) {
    if (dates.length === 0 || sentimentScores.length === 0) {
        const chartContainer = document.getElementById('mood-trend-chart')?.parentElement;
        if (chartContainer) {
            chartContainer.innerHTML = `
                <div class="text-center py-5">
                    <div class="text-muted mb-3">
                        <i class="fas fa-chart-line fa-3x"></i>
                    </div>
                    <h5>No Mood Data Yet</h5>
                    <p class="text-muted">Add some diary entries to see your mood trends.</p>
                    <a href="/diary" class="btn btn-sm btn-primary mt-2">
                        <i class="fas fa-plus"></i> Create Entry
                    </a>
                </div>
            `;
        }
        return;
    }
    
    const ctx = document.getElementById('mood-trend-chart');
    
    if (!ctx) {
        console.error('Mood trend chart canvas not found');
        return;
    }
    
    // Create gradient for the chart area
    const gradientFill = ctx.getContext('2d').createLinearGradient(0, 0, 0, 300);
    gradientFill.addColorStop(0, 'rgba(116, 96, 238, 0.5)');
    gradientFill.addColorStop(1, 'rgba(116, 96, 238, 0.0)');
    
    // Prepare annotations for mood zones
    const annotations = {
        zones: [{
            type: 'box',
            yScaleID: 'y',
            yMin: 0.6,
            yMax: 1,
            backgroundColor: 'rgba(33, 150, 243, 0.1)',
            borderColor: 'transparent',
        }, {
            type: 'box',
            yScaleID: 'y',
            yMin: 0.2,
            yMax: 0.6,
            backgroundColor: 'rgba(76, 175, 80, 0.1)',
            borderColor: 'transparent',
        }, {
            type: 'box',
            yScaleID: 'y',
            yMin: -0.2,
            yMax: 0.2,
            backgroundColor: 'rgba(158, 158, 158, 0.1)',
            borderColor: 'transparent',
        }, {
            type: 'box',
            yScaleID: 'y',
            yMin: -0.6,
            yMax: -0.2,
            backgroundColor: 'rgba(255, 152, 0, 0.1)',
            borderColor: 'transparent',
        }, {
            type: 'box',
            yScaleID: 'y',
            yMin: -1,
            yMax: -0.6,
            backgroundColor: 'rgba(255, 82, 82, 0.1)',
            borderColor: 'transparent',
        }]
    };
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Mood Score',
                data: sentimentScores,
                borderColor: 'rgba(116, 96, 238, 1)',
                backgroundColor: gradientFill,
                tension: 0.4,
                fill: true,
                pointBackgroundColor: sentimentScores.map(score => {
                    if (score >= 0.6) return '#2196F3';
                    if (score >= 0.2) return '#4CAF50';
                    if (score >= -0.2) return '#9E9E9E';
                    if (score >= -0.6) return '#FF9800';
                    return '#FF5252';
                }),
                pointBorderColor: 'white',
                pointRadius: 5,
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            scales: {
                y: {
                    min: -1,
                    max: 1,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    },
                    ticks: {
                        callback: function(value) {
                            if (value === 1) return 'Very Positive';
                            if (value === 0.5) return 'Positive';
                            if (value === 0) return 'Neutral';
                            if (value === -0.5) return 'Negative';
                            if (value === -1) return 'Very Negative';
                            return '';
                        },
                        color: 'rgba(255, 255, 255, 0.7)'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)',
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            },
            plugins: {
                annotation: {
                    annotations: annotations
                },
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.7)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    borderColor: 'rgba(255, 255, 255, 0.2)',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            const score = context.raw;
                            let label = '';
                            
                            if (score >= 0.6) label = 'Very Positive';
                            else if (score >= 0.2) label = 'Positive';
                            else if (score >= -0.2) label = 'Neutral';
                            else if (score >= -0.6) label = 'Negative';
                            else label = 'Very Negative';
                            
                            return `Mood: ${label} (${score.toFixed(2)})`;
                        }
                    }
                }
            }
        }
    });
}

function initMoodDistributionChart(moodCounts) {
    const ctx = document.getElementById('mood-distribution-chart');
    
    if (!ctx) {
        console.error('Mood distribution chart canvas not found');
        return;
    }
    
    // If no data, display a message
    if (Object.keys(moodCounts).length === 0) {
        ctx.parentElement.innerHTML = `
            <div class="text-center py-5">
                <div class="text-muted mb-3">
                    <i class="fas fa-chart-pie fa-3x"></i>
                </div>
                <h5>No Mood Data Yet</h5>
                <p class="text-muted">Add some diary entries to see your mood distribution.</p>
                <a href="/diary" class="btn btn-sm btn-primary mt-2">
                    <i class="fas fa-plus"></i> Create Entry
                </a>
            </div>
        `;
        return;
    }
    
    // Format the mood labels for display
    const labels = [];
    const data = [];
    const backgroundColor = [];
    const borderColor = [];
    
    // Define colors and order for each mood
    const moodOrder = ['very_negative', 'negative', 'neutral', 'positive', 'very_positive'];
    const moodColors = {
        'very_negative': ['rgba(255, 82, 82, 0.8)', 'rgba(255, 82, 82, 1)'],
        'negative': ['rgba(255, 152, 0, 0.8)', 'rgba(255, 152, 0, 1)'],
        'neutral': ['rgba(158, 158, 158, 0.8)', 'rgba(158, 158, 158, 1)'],
        'positive': ['rgba(76, 175, 80, 0.8)', 'rgba(76, 175, 80, 1)'],
        'very_positive': ['rgba(33, 150, 243, 0.8)', 'rgba(33, 150, 243, 1)']
    };
    
    // Sort the moods in our predefined order
    moodOrder.forEach(mood => {
        if (mood in moodCounts) {
            labels.push(mood.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()));
            data.push(moodCounts[mood]);
            backgroundColor.push(moodColors[mood][0]);
            borderColor.push(moodColors[mood][1]);
        }
    });
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: backgroundColor,
                borderColor: borderColor,
                borderWidth: 2,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: 'rgba(255, 255, 255, 0.7)',
                        padding: 15,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.7)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    borderColor: 'rgba(255, 255, 255, 0.2)',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${value} entries (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function initWeeklyMoodChart(weeklyMoods) {
    const ctx = document.getElementById('weekly-mood-chart');
    
    if (!ctx) {
        console.error('Weekly mood chart canvas not found');
        return;
    }
    
    // If no data, display a message
    if (Object.keys(weeklyMoods).length === 0) {
        ctx.parentElement.innerHTML = `
            <div class="text-center py-5">
                <div class="text-muted mb-3">
                    <i class="fas fa-calendar-week fa-3x"></i>
                </div>
                <h5>No Weekly Mood Data Yet</h5>
                <p class="text-muted">Add diary entries from different weeks to see your weekly mood trends.</p>
                <a href="/diary" class="btn btn-sm btn-primary mt-2">
                    <i class="fas fa-plus"></i> Create Entry
                </a>
            </div>
        `;
        return;
    }
    
    // Prepare data
    const weeks = Object.keys(weeklyMoods).sort();
    const scores = weeks.map(week => weeklyMoods[week]);
    
    // Prepare color arrays for bars
    const backgroundColors = scores.map(score => {
        if (score >= 0.6) return 'rgba(33, 150, 243, 0.8)';
        if (score >= 0.2) return 'rgba(76, 175, 80, 0.8)';
        if (score >= -0.2) return 'rgba(158, 158, 158, 0.8)';
        if (score >= -0.6) return 'rgba(255, 152, 0, 0.8)';
        return 'rgba(255, 82, 82, 0.8)';
    });
    
    const borderColors = scores.map(score => {
        if (score >= 0.6) return 'rgba(33, 150, 243, 1)';
        if (score >= 0.2) return 'rgba(76, 175, 80, 1)';
        if (score >= -0.2) return 'rgba(158, 158, 158, 1)';
        if (score >= -0.6) return 'rgba(255, 152, 0, 1)';
        return 'rgba(255, 82, 82, 1)';
    });
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: weeks,
            datasets: [{
                label: 'Average Mood',
                data: scores,
                backgroundColor: backgroundColors,
                borderColor: borderColors,
                borderWidth: 2,
                borderRadius: 5,
                hoverBackgroundColor: scores.map(score => {
                    if (score >= 0.6) return 'rgba(33, 150, 243, 1)';
                    if (score >= 0.2) return 'rgba(76, 175, 80, 1)';
                    if (score >= -0.2) return 'rgba(158, 158, 158, 1)';
                    if (score >= -0.6) return 'rgba(255, 152, 0, 1)';
                    return 'rgba(255, 82, 82, 1)';
                })
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            scales: {
                y: {
                    min: -1,
                    max: 1,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    },
                    ticks: {
                        callback: function(value) {
                            if (value === 1) return 'Very Positive';
                            if (value === 0.5) return 'Positive';
                            if (value === 0) return 'Neutral';
                            if (value === -0.5) return 'Negative';
                            if (value === -1) return 'Very Negative';
                            return '';
                        },
                        color: 'rgba(255, 255, 255, 0.7)'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.7)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    borderColor: 'rgba(255, 255, 255, 0.2)',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            const score = context.raw;
                            let label = '';
                            
                            if (score >= 0.6) label = 'Very Positive';
                            else if (score >= 0.2) label = 'Positive';
                            else if (score >= -0.2) label = 'Neutral';
                            else if (score >= -0.6) label = 'Negative';
                            else label = 'Very Negative';
                            
                            return `Average Mood: ${label} (${score.toFixed(2)})`;
                        }
                    }
                }
            }
        }
    });
}
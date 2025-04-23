// Function to fetch data from API endpoints
async function fetchData(endpoint) {
    try {
        const response = await fetch(`/api/${endpoint}`);
        if (!response.ok) throw new Error('Network response was not ok');
        return await response.json();
    } catch (error) {
        console.error(`Error fetching ${endpoint}:`, error);
        return null;
    }
}

// Function to update weekly report
async function updateWeeklyReport() {
    const data = await fetchData('weekly-report');
    if (!data) return;

    const reportHtml = `
        <div class="mb-3">
            <h6>Total Reviews: ${data.total_reviews}</h6>
            <h6>Average Rating: ${data.average_rating.toFixed(1)}</h6>
        </div>
        <div>
            <h6>Sentiment Distribution:</h6>
            <div class="d-flex justify-content-between">
                <span class="positive">Positive: ${data.sentiment_distribution.positive}%</span>
                <span class="neutral">Neutral: ${data.sentiment_distribution.neutral}%</span>
                <span class="negative">Negative: ${data.sentiment_distribution.negative}%</span>
            </div>
        </div>
    `;
    document.getElementById('weeklyReport').innerHTML = reportHtml;
}

// Function to update sentiment trends
async function updateSentimentTrends() {
    const data = await fetchData('sentiment-trends');
    if (!data) return;

    const trace = {
        x: data.dates,
        y: data.sentiment_scores,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Sentiment Score'
    };

    const layout = {
        title: 'Sentiment Trend Over Time',
        xaxis: { title: 'Date' },
        yaxis: { title: 'Sentiment Score' }
    };

    Plotly.newPlot('sentimentTrends', [trace], layout);
}

// Function to update complaints
async function updateComplaints() {
    const data = await fetchData('complaints');
    if (!data) return;

    const complaintsHtml = data.map(complaint => `
        <div class="mb-3">
            <p class="mb-1">${complaint.text}</p>
            <small class="text-muted">${complaint.date}</small>
        </div>
    `).join('');
    document.getElementById('complaints').innerHTML = complaintsHtml;
}

// Function to update top themes
async function updateTopThemes() {
    const data = await fetchData('top-themes');
    if (!data) return;

    const themesHtml = data.map(theme => `
        <span class="theme-tag">${theme}</span>
    `).join('');
    document.getElementById('topThemes').innerHTML = themesHtml;
}

// Function to update review categories
async function updateReviewCategories() {
    const data = await fetchData('review-categories');
    if (!data) return;

    const categoriesHtml = Object.entries(data).map(([category, count]) => `
        <div class="mb-2">
            <h6>${category}: ${count}</h6>
        </div>
    `).join('');
    document.getElementById('reviewCategories').innerHTML = categoriesHtml;
}

// Function to update visualization
async function updateVisualization() {
    const data = await fetchData('weekly-report');
    if (!data) return;

    const trace = {
        values: [
            data.sentiment_distribution.positive,
            data.sentiment_distribution.neutral,
            data.sentiment_distribution.negative
        ],
        labels: ['Positive', 'Neutral', 'Negative'],
        type: 'pie',
        marker: {
            colors: ['#28a745', '#6c757d', '#dc3545']
        }
    };

    const layout = {
        title: 'Sentiment Distribution',
        height: 400
    };

    Plotly.newPlot('visualization', [trace], layout);
}

// Initialize dashboard
async function initializeDashboard() {
    await Promise.all([
        updateWeeklyReport(),
        updateSentimentTrends(),
        updateComplaints(),
        updateTopThemes(),
        updateReviewCategories(),
        updateVisualization()
    ]);
}

// Run when the page loads
document.addEventListener('DOMContentLoaded', initializeDashboard); 
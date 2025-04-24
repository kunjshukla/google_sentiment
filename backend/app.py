from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from review_analyzer import ReviewAnalyzer

app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for all routes
analyzer = ReviewAnalyzer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_sentiment():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Review text is required'}), 400
    
    text = data['text']
    # Get similar reviews for context
    similar_reviews = analyzer._get_similar_reviews(text)
    
    # Analyze sentiment with context
    sentiment_result = analyzer._analyze_sentiment_with_context(text, similar_reviews)
    
    # Convert sentiment to match schema
    sentiment_map = {
        'POSITIVE': 'positive',
        'NEGATIVE': 'negative',
        'NEUTRAL': 'neutral'
    }
    
    # Calculate scores
    score = sentiment_result['score']
    positive_score = score if sentiment_result['label'] == 'POSITIVE' else 0
    negative_score = -score if sentiment_result['label'] == 'NEGATIVE' else 0
    neutral_score = 1 - abs(score)
    compound_score = score
    
    # Extract key phrases
    doc = analyzer.nlp(text)
    positive_keywords = ['good', 'great', 'excellent', 'amazing', 'wonderful']
    negative_keywords = ['bad', 'terrible', 'horrible', 'awful', 'poor']
    
    positive_phrases = []
    negative_phrases = []
    
    for sent in doc.sents:
        if any(word in sent.text.lower() for word in positive_keywords):
            positive_phrases.append(sent.text.strip())
        if any(word in sent.text.lower() for word in negative_keywords):
            negative_phrases.append(sent.text.strip())
    
    response = {
        'text': text,
        'sentiment': sentiment_map.get(sentiment_result['label'], 'neutral'),
        'score': {
            'positive': positive_score,
            'negative': negative_score,
            'neutral': neutral_score,
            'compound': compound_score
        },
        'keyPhrases': {
            'positive': positive_phrases[:5],
            'negative': negative_phrases[:5]
        }
    }
    
    return jsonify(response)

@app.route('/api/analyze/batch', methods=['POST'])
def analyze_batch():
    data = request.get_json()
    if not data or 'reviews' not in data:
        return jsonify({'error': 'Reviews array is required'}), 400
    
    results = []
    for text in data['reviews']:
        # Reuse the single analysis endpoint logic
        response = app.test_client().post('/api/analyze', json={'text': text})
        results.append(response.get_json())
    
    return jsonify(results)

@app.route('/api/weekly-report')
def weekly_report():
    report = analyzer.generate_weekly_report()
    return jsonify(report)

@app.route('/api/sentiment-trends')
def sentiment_trends():
    trends = analyzer.get_sentiment_trends()
    return jsonify(trends)

@app.route('/api/complaints')
def complaints():
    complaints = analyzer.get_recent_complaints()
    return jsonify(complaints)

@app.route('/api/top-themes')
def top_themes():
    themes = analyzer.get_top_themes()
    return jsonify(themes)

@app.route('/api/review-categories')
def review_categories():
    categories = analyzer.get_review_categories()
    return jsonify(categories)

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Run on port 5001 
from flask import Flask, render_template, jsonify
from review_analyzer import ReviewAnalyzer

app = Flask(__name__, static_folder='static')
analyzer = ReviewAnalyzer()

@app.route('/')
def index():
    return render_template('index.html')

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
    app.run(debug=True) 
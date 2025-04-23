import json
from datetime import datetime
from review_analyzer import ReviewAnalyzer
import time
import os

def load_sample_reviews():
    """Load reviews from sample_reviews.json"""
    with open('sample_reviews.json', 'r') as f:
        data = json.load(f)
    return data['reviews']

def analyze_reviews():
    """Analyze sample reviews and generate reports"""
    analyzer = ReviewAnalyzer()
    reviews = load_sample_reviews()
    
    # Process all reviews
    for review in reviews:
        # Convert ISO format string to datetime
        review_date = datetime.fromisoformat(review['date'].replace('Z', '+00:00'))
        analyzer.add_review(
            text=review['text'],
            rating=review['rating'],
            date=review_date
        )
    
    # Generate weekly report
    report_path = analyzer.generate_weekly_report()
    print(f"\nWeekly report generated: {report_path}")
    
    # Show sentiment summary
    print("\nSentiment Summary:")
    positive_reviews = len(analyzer.reviews_df[analyzer.reviews_df['sentiment'] == 'POSITIVE'])
    negative_reviews = len(analyzer.reviews_df[analyzer.reviews_df['sentiment'] == 'NEGATIVE'])
    print(f"Positive Reviews: {positive_reviews}")
    print(f"Negative Reviews: {negative_reviews}")
    
    # Show complaints
    complaints = analyzer.get_complaints()
    if not complaints.empty:
        print("\nComplaints found:")
        for _, row in complaints.iterrows():
            print(f"\nDate: {row['date']}")
            print(f"Review: {row['text']}")
            print(f"Rating: {row['rating']}")
    
    # Show sentiment trend
    print("\nSentiment Trend (Last 7 days):")
    weekly_data = analyzer.reviews_df.sort_values('date')
    for _, row in weekly_data.iterrows():
        print(f"\nDate: {row['date'].strftime('%Y-%m-%d')}")
        print(f"Sentiment: {row['sentiment']} (Score: {row['sentiment_score']:.2f})")
        print(f"Review: {row['text'][:50]}...")

if __name__ == "__main__":
    print("Starting review analysis with sample data...")
    analyze_reviews() 
import json
from datetime import datetime
from review_analyzer import ReviewAnalyzer
from review_fetcher import ReviewFetcher
import time
import os

def analyze_reviews(file_data: bytes):
    """
    Analyze reviews from uploaded file and generate reports
    
    Args:
        file_data (bytes): The uploaded file data in bytes format
    
    Returns:
        dict: Analysis results including status, report, and metrics
    """
    # Initialize the review fetcher and analyzer
    fetcher = ReviewFetcher()
    analyzer = ReviewAnalyzer()
    
    try:
        # Load reviews from the uploaded file
        fetcher.load_reviews_from_file(file_data)
        
        # Get all reviews from the file
        reviews_df = fetcher.get_reviews()
        
        # Process all reviews
        for _, review in reviews_df.iterrows():
            analyzer.add_review(
                text=review['text'],
                rating=review['rating'],
                date=review['date']
            )
        
        # Generate weekly report
        report = analyzer.generate_weekly_report()
        
        # Calculate sentiment summary
        positive_reviews = len(analyzer.reviews_df[analyzer.reviews_df['sentiment'] == 'POSITIVE'])
        negative_reviews = len(analyzer.reviews_df[analyzer.reviews_df['sentiment'] == 'NEGATIVE'])
        neutral_reviews = len(analyzer.reviews_df[analyzer.reviews_df['sentiment'] == 'NEUTRAL'])
        
        # Get complaints
        complaints = analyzer.get_complaints()
        
        # Get sentiment trend
        weekly_data = analyzer.reviews_df.sort_values('date')
        
        return {
            'status': 'success',
            'report': report,
            'sentiment_summary': {
                'positive': positive_reviews,
                'negative': negative_reviews,
                'neutral': neutral_reviews
            },
            'complaints': complaints.to_dict('records') if not complaints.empty else [],
            'sentiment_trend': weekly_data[['date', 'sentiment', 'sentiment_score', 'text']].to_dict('records')
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }

# Remove the test code since we'll be handling file uploads from the frontend
if __name__ == "__main__":
    print("This module is designed to be imported and used with file uploads from the frontend.")
    print("Please use the analyze_reviews() function with file data from an upload.") 
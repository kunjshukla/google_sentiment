import requests
import json
from datetime import datetime
from review_analyzer import ReviewAnalyzer
import time
from dotenv import load_dotenv
import os

load_dotenv()

class GoogleReviewsFetcher:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api/place/details/json"
        self.analyzer = ReviewAnalyzer()
    
    def get_place_reviews(self, place_id):
        """Fetch reviews for a specific place"""
        params = {
            'place_id': place_id,
            'key': self.api_key,
            'fields': 'reviews'
        }
        
        response = requests.get(self.base_url, params=params)
        data = response.json()
        
        if data['status'] == 'OK':
            reviews = data['result'].get('reviews', [])
            for review in reviews:
                # Convert timestamp to datetime
                review_date = datetime.fromtimestamp(review['time'])
                
                # Add review to analyzer
                self.analyzer.add_review(
                    text=review['text'],
                    rating=review['rating'],
                    date=review_date
                )
            
            return len(reviews)
        else:
            print(f"Error fetching reviews: {data['status']}")
            return 0
    
    def monitor_reviews(self, place_id, interval_minutes=60):
        """Monitor reviews at regular intervals"""
        while True:
            print(f"\nFetching reviews at {datetime.now()}")
            review_count = self.get_place_reviews(place_id)
            print(f"Processed {review_count} reviews")
            
            # Generate weekly report if it's the end of the week
            if datetime.now().weekday() == 6:  # Sunday
                report_path = self.analyzer.generate_weekly_report()
                print(f"Weekly report generated: {report_path}")
            
            # Check for urgent complaints
            complaints = self.analyzer.get_complaints()
            if not complaints.empty:
                print("\nUrgent complaints found:")
                print(complaints[['text', 'date']])
            
            # Wait for next interval
            time.sleep(interval_minutes * 60)

if __name__ == "__main__":
    # Get API key from environment variable
    api_key = os.getenv('GOOGLE_PLACES_API_KEY')
    if not api_key:
        print("Please set GOOGLE_PLACES_API_KEY in your .env file")
        exit(1)
    
    # Example place ID (replace with your business's place ID)
    place_id = "ChIJN1t_tDeuEmsRUsoyG83frY4"  # Example place ID
    
    fetcher = GoogleReviewsFetcher(api_key)
    fetcher.monitor_reviews(place_id) 
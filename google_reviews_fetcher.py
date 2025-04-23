import requests
import json
from datetime import datetime
import time
from dotenv import load_dotenv
import os
from google_places_client import GooglePlacesClient

load_dotenv()

class GoogleReviewsFetcher:
    def __init__(self, api_key=None):
        load_dotenv()
        self.api_key = api_key or os.getenv('GOOGLE_PLACES_API_KEY')
        if not self.api_key:
            raise ValueError("Google Places API key not found. Please set it in your .env file.")
        
        self.places_client = GooglePlacesClient()
        self.base_url = "https://maps.googleapis.com/maps/api/place"
    
    def search_place(self, query, location=None, radius=None):
        """Search for a place by name and optionally location"""
        params = {
            'query': query,
            'key': self.api_key
        }
        
        if location and radius:
            params['location'] = location  # Format: "latitude,longitude"
            params['radius'] = radius
        
        response = requests.get(f"{self.base_url}/findplacefromtext/json", params=params)
        data = response.json()
        
        if data['status'] == 'OK':
            return data['candidates']
        else:
            print(f"Error searching place: {data['status']}")
            return []
    
    def get_place_details(self, place_id):
        """Get detailed information about a place"""
        params = {
            'place_id': place_id,
            'key': self.api_key,
            'fields': 'name,formatted_address,rating,user_ratings_total,reviews'
        }
        
        response = requests.get(f"{self.base_url}/details/json", params=params)
        data = response.json()
        
        if data['status'] == 'OK':
            return data['result']
        else:
            print(f"Error fetching place details: {data['status']}")
            return None
    
    def get_place_reviews(self, place_name):
        """Get reviews for a place by name"""
        try:
            # Search for the place and get its ID
            place_id = self.places_client.search_place_by_name(place_name)
            
            # Get place details
            place_details = self.places_client.get_place_details(place_id)
            
            # Get reviews
            reviews = self.places_client.get_reviews(place_id)
            
            return {
                "place_id": place_id,
                "place_name": place_details.get('name', place_name),
                "rating": place_details.get('rating', 'N/A'),
                "total_ratings": place_details.get('user_ratings_total', 'N/A'),
                "reviews": reviews
            }
        except Exception as e:
            raise Exception(f"Error fetching reviews: {str(e)}")
    
    def search_places(self, query, location=None, radius=50000):
        """Search for places based on query"""
        return self.places_client.search_places(query, location, radius)
    
    def find_place_id(self, business_name, location=None):
        """Helper method to find a place_id for a business name"""
        candidates = self.search_place(business_name, location)
        if candidates:
            return candidates[0]['place_id']
        return None
    
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
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

class GooglePlacesClient:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('GOOGLE_PLACES_API_KEY')
        if not self.api_key:
            raise ValueError("Google Places API key not found in .env file. Please add your API key to the .env file.")
        
        self.base_url = "https://maps.googleapis.com/maps/api/place"
    
    def search_place_by_name(self, name, location=None):
        """Search for a place by name and return its details"""
        endpoint = f"{self.base_url}/textsearch/json"
        params = {
            'query': name,
            'key': self.api_key,
            'type': 'establishment'  # Add type to narrow down results
        }
        
        if location:
            # Ensure location is in the correct format: "latitude,longitude"
            if isinstance(location, (tuple, list)) and len(location) == 2:
                location = f"{location[0]},{location[1]}"
            params['location'] = location
            params['radius'] = 50000  # 50km radius
        
        response = requests.get(endpoint, params=params)
        if response.status_code != 200:
            raise Exception(f"API request failed with status code {response.status_code}")
        
        data = response.json()
        if data['status'] == 'REQUEST_DENIED':
            raise Exception("API request denied. Please check if your API key is valid and the Places API is enabled in your Google Cloud Console.")
        elif data['status'] == 'INVALID_REQUEST':
            raise Exception(f"Invalid request. Please check your parameters. Error details: {data.get('error_message', 'No details available')}")
        elif data['status'] != 'OK':
            raise Exception(f"API returned error: {data['status']}")
        
        if not data['results']:
            raise Exception(f"No places found matching: {name}")
        
        # Return the first result's place_id
        return data['results'][0]['place_id']
    
    def get_place_details(self, place_id):
        """Get detailed information about a place"""
        endpoint = f"{self.base_url}/details/json"
        params = {
            'place_id': place_id,
            'key': self.api_key,
            'fields': 'name,rating,reviews,user_ratings_total,formatted_address,types'  # Add more fields
        }
        
        response = requests.get(endpoint, params=params)
        if response.status_code != 200:
            raise Exception(f"API request failed with status code {response.status_code}")
        
        data = response.json()
        if data['status'] == 'REQUEST_DENIED':
            raise Exception("API request denied. Please check if your API key is valid and the Places API is enabled in your Google Cloud Console.")
        elif data['status'] == 'INVALID_REQUEST':
            raise Exception(f"Invalid request. Please check your parameters. Error details: {data.get('error_message', 'No details available')}")
        elif data['status'] == 'NOT_FOUND':
            raise Exception(f"Place with ID {place_id} not found. Please check if the place ID is valid.")
        elif data['status'] != 'OK':
            raise Exception(f"API returned error: {data['status']}")
        
        return data['result']
    
    def get_reviews(self, place_id):
        """Get all reviews for a place"""
        place_details = self.get_place_details(place_id)
        reviews = []
        
        for review in place_details.get('reviews', []):
            reviews.append({
                'text': review['text'],
                'rating': review['rating'],
                'date': review['time'],
                'author': review['author_name']
            })
        
        return reviews
    
    def search_places(self, query, location=None, radius=50000):
        """Search for places based on query and optional location"""
        endpoint = f"{self.base_url}/textsearch/json"
        params = {
            'query': query,
            'key': self.api_key
        }
        
        if location:
            params['location'] = location
            params['radius'] = radius
        
        response = requests.get(endpoint, params=params)
        if response.status_code != 200:
            raise Exception(f"API request failed with status code {response.status_code}")
        
        data = response.json()
        if data['status'] != 'OK':
            raise Exception(f"API returned error: {data['status']}")
        
        return data['results'] 
import os
from dotenv import load_dotenv
from google_reviews_fetcher import GoogleReviewsFetcher

# Load API key
load_dotenv()
api_key = os.getenv('GOOGLE_PLACES_API_KEY')

# Create fetcher
fetcher = GoogleReviewsFetcher(api_key)

# Search for a business
business_name = "Starbucks"
print(f"Searching for {business_name}...")
candidates = fetcher.search_place(business_name)

if candidates:
    place = candidates[0]
    place_id = place['place_id']
    print(f"Found place_id: {place_id}")
    
    # Get reviews
    print("Fetching reviews...")
    review_count = fetcher.get_place_reviews(place_id)
    print(f"Fetched {review_count} reviews")
else:
    print("No places found")
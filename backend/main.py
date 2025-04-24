from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from review_analyzer import ReviewAnalyzer
from review_fetcher import ReviewFetcher
import uvicorn
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from fastapi.responses import HTMLResponse
import json
import argparse
from sample_review_analyzer import analyze_reviews

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Parse command line arguments
parser = argparse.ArgumentParser(description='Review Analysis API')
parser.add_argument('--reviews-file', type=str, default='reviews.json',
                    help='Path to the JSON file containing reviews')
args = parser.parse_args()

# Initialize the review fetcher and analyzer
review_fetcher = ReviewFetcher()
analyzer = ReviewAnalyzer(reviews_file=args.reviews_file)

class ReviewRequest(BaseModel):
    text: str
    rating: int
    date: datetime

class ReviewResponse(BaseModel):
    id: int
    text: str
    sentiment: str
    score: Dict[str, float]
    keyPhrases: Dict[str, List[str]]
    categories: Optional[Dict[str, float]] = None
    createdAt: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Review Analysis API is running"}

@app.post("/add_review")
async def add_review(review: ReviewRequest):
    try:
        analyzer.add_review(
            text=review.text,
            rating=review.rating,
            date=review.date
        )
        return {"message": "Review added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/weekly_report")
async def get_weekly_report():
    try:
        report = analyzer.generate_weekly_report()
        return {"report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sentiment_trends")
async def get_sentiment_trends():
    try:
        trends = analyzer.get_sentiment_trends()
        return {"trends": trends}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/complaints")
async def get_complaints():
    try:
        complaints = analyzer.get_complaints()
        return {"complaints": complaints.to_dict('records')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/similar_reviews")
async def get_similar_reviews(text: str, n_results: int = 3):
    try:
        similar = analyzer.get_similar_reviews(text, n_results)
        return {"similar_reviews": similar}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/top_themes")
async def get_top_themes(n: int = 5):
    try:
        themes = analyzer.extract_top_themes(n)
        return {"themes": themes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/review_categories")
async def get_review_categories():
    try:
        categories = analyzer.categorize_reviews()
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/visualization", response_class=HTMLResponse)
async def get_visualization():
    try:
        # Get sentiment trends
        trends = analyzer.get_sentiment_trends()
        
        # Create a line plot
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(trends.keys()),
            y=list(trends.values()),
            mode='lines+markers',
            name='Sentiment Score'
        ))
        
        fig.update_layout(
            title='Sentiment Trends Over Time',
            xaxis_title='Date',
            yaxis_title='Average Sentiment Score',
            template='plotly_white'
        )
        
        return fig.to_html()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze-reviews")
async def analyze_reviews_endpoint(file: UploadFile = File(...)):
    """
    Endpoint to handle review file uploads from the frontend.
    Accepts CSV files and returns analysis results.
    """
    try:
        # Check if the file is a CSV or TXT
        if not (file.filename.endswith('.csv') or file.filename.endswith('.txt')):
            raise HTTPException(status_code=400, detail="Only CSV and TXT files are supported")
        
        # Read the file content
        file_data = await file.read()
        
        # Analyze the reviews
        result = analyze_reviews(file_data)
        
        # Format the response to match frontend expectations
        return {
            "status": "success",
            "data": {
                "sentiment": result["sentiment_summary"],
                "complaints": result["complaints"],
                "trends": result["sentiment_trend"],
                "report": result["report"]
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/api/reviews")
async def get_reviews():
    try:
        # Get all reviews from the CSV file
        reviews_df = review_fetcher.get_reviews()
        
        # Process each review through the analyzer
        results = []
        for idx, row in reviews_df.iterrows():
            # Add review to analyzer
            analyzer.add_review(
                text=row['text'],
                rating=row['rating'],
                date=row['date']
            )
            
            # Get the latest analysis result
            result = analyzer.reviews_df.iloc[-1]
            
            # Format the response
            review_response = ReviewResponse(
                id=idx,
                text=row['text'],
                sentiment=result['sentiment'].lower(),
                score={
                    "positive": result['sentiment_score'] if result['sentiment'] == 'POSITIVE' else 0,
                    "neutral": 0,
                    "negative": -result['sentiment_score'] if result['sentiment'] == 'NEGATIVE' else 0,
                    "compound": result['sentiment_score']
                },
                keyPhrases={
                    "positive": [],
                    "negative": []
                },
                categories={
                    "service": 0.0,
                    "food": 0.0,
                    "value": 0.0,
                    "ambiance": 0.0
                },
                createdAt=row['date'].strftime('%Y-%m-%d')
            )
            
            results.append(review_response)
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sentiment-trends")
async def get_sentiment_trends():
    try:
        trends = analyzer.get_sentiment_trends()
        return {"trends": trends}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
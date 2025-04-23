from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from review_analyzer import ReviewAnalyzer
import uvicorn
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from fastapi.responses import HTMLResponse
import json
import argparse

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Parse command line arguments
parser = argparse.ArgumentParser(description='Review Analysis API')
parser.add_argument('--reviews-file', type=str, default='reviews.json',
                    help='Path to the JSON file containing reviews')
args = parser.parse_args()

# Initialize the analyzer with reviews from file
analyzer = ReviewAnalyzer(reviews_file=args.reviews_file)

class ReviewRequest(BaseModel):
    text: str
    rating: int
    date: datetime

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
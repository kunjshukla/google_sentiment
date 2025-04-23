import pandas as pd
import chromadb
from transformers import pipeline
import spacy
from datetime import datetime, timedelta
import plotly.express as px
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import subprocess
import sys

# Load environment variables
load_dotenv()

class ReviewAnalyzer:
    def __init__(self):
        # Initialize ChromaDB
        self.chroma_client = chromadb.Client()
        self.collection = self.chroma_client.create_collection(name="reviews")
        
        # Load sentiment analysis model
        self.sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
        
        # Load spaCy for complaint detection
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("spaCy model 'en_core_web_sm' not found. Installing...")
            subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")
        
        # Load sentence transformer for semantic search
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize data storage
        self.reviews_df = pd.DataFrame(columns=['text', 'rating', 'date', 'sentiment', 'complaint'])
    
    def add_review(self, text, rating, date):
        """Add a new review to the system"""
        # Get similar reviews for context
        similar_reviews = self._get_similar_reviews(text)
        
        # Analyze sentiment with context
        sentiment_result = self._analyze_sentiment_with_context(text, similar_reviews)
        sentiment = sentiment_result['label']
        sentiment_score = sentiment_result['score']
        
        # Detect complaints with context
        is_complaint = self._detect_complaint_with_context(text, similar_reviews)
        
        # Store in DataFrame
        new_review = pd.DataFrame({
            'text': [text],
            'rating': [rating],
            'date': [date],
            'sentiment': [sentiment],
            'sentiment_score': [sentiment_score],
            'complaint': [is_complaint]
        })
        self.reviews_df = pd.concat([self.reviews_df, new_review], ignore_index=True)
        
        # Store in ChromaDB with embeddings
        embedding = self.encoder.encode([text])[0].tolist()
        
        # Convert datetime to string for ChromaDB metadata
        date_str = date.strftime("%Y-%m-%d %H:%M:%S")
        
        self.collection.add(
            documents=[text],
            embeddings=[embedding],
            metadatas=[{
                "rating": rating,
                "date": date_str,
                "sentiment": sentiment,
                "complaint": is_complaint
            }],
            ids=[f"review_{len(self.reviews_df)}"]
        )
    
    def _get_similar_reviews(self, text, n_results=3):
        """Retrieve similar reviews using semantic search"""
        query_embedding = self.encoder.encode([text])[0].tolist()
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results['documents'][0] if results['documents'] else []
    
    def _analyze_sentiment_with_context(self, text, similar_reviews):
        """Analyze sentiment using context from similar reviews"""
        if not similar_reviews:
            return self.sentiment_analyzer(text)[0]
        
        # Combine current review with similar reviews for context
        context = " ".join(similar_reviews + [text])
        return self.sentiment_analyzer(context)[0]
    
    def _detect_complaint_with_context(self, text, similar_reviews):
        """Detect complaints using context from similar reviews"""
        # Combine current review with similar reviews
        combined_text = " ".join(similar_reviews + [text])
        doc = self.nlp(combined_text)
        
        # Enhanced complaint detection with context
        complaint_keywords = ['bad', 'terrible', 'awful', 'horrible', 'disappointed', 'never again',
                            'poor', 'worst', 'unacceptable', 'avoid', 'waste', 'ripoff']
        complaint_phrases = ['not worth', 'would not recommend', 'stay away', 'never coming back']
        
        # Check for keywords
        has_keywords = any(token.text.lower() in complaint_keywords for token in doc)
        
        # Check for phrases
        has_phrases = any(phrase in combined_text.lower() for phrase in complaint_phrases)
        
        return has_keywords or has_phrases
    
    def generate_weekly_report(self):
        """Generate a weekly report with sentiment analysis and complaint summary"""
        # Get last week's data
        one_week_ago = datetime.now() - timedelta(days=7)
        weekly_data = self.reviews_df[self.reviews_df['date'] >= one_week_ago]
        
        # Create sentiment trend plot
        fig = px.line(weekly_data, x='date', y='sentiment_score', 
                     title='Sentiment Trend Over Past Week')
        fig.write_image("sentiment_trend.png")
        
        # Generate PDF report
        c = canvas.Canvas("weekly_report.pdf", pagesize=letter)
        c.drawString(100, 750, "Weekly Review Analysis Report")
        c.drawString(100, 730, f"Period: {one_week_ago.date()} to {datetime.now().date()}")
        
        # Add sentiment summary
        c.drawString(100, 700, "Sentiment Summary:")
        positive_reviews = len(weekly_data[weekly_data['sentiment'] == 'POSITIVE'])
        negative_reviews = len(weekly_data[weekly_data['sentiment'] == 'NEGATIVE'])
        c.drawString(100, 680, f"Positive Reviews: {positive_reviews}")
        c.drawString(100, 660, f"Negative Reviews: {negative_reviews}")
        
        # Add complaint summary with context
        complaints = weekly_data[weekly_data['complaint'] == True]
        c.drawString(100, 620, "Complaints Summary:")
        for i, (_, row) in enumerate(complaints.iterrows()):
            similar_reviews = self._get_similar_reviews(row['text'])
            c.drawString(100, 600 - i*40, f"Complaint: {row['text'][:50]}...")
            if similar_reviews:
                c.drawString(100, 580 - i*40, f"Similar Reviews: {len(similar_reviews)} found")
        
        # Add sentiment trend image
        c.drawImage("sentiment_trend.png", 100, 300, width=400, height=200)
        
        c.save()
        
        return "weekly_report.pdf"
    
    def get_complaints(self):
        """Get all complaints from the reviews"""
        return self.reviews_df[self.reviews_df['complaint'] == True]
    
    def get_similar_reviews(self, text, n_results=3):
        """Get similar reviews for a given text"""
        return self._get_similar_reviews(text, n_results)

# Example usage
if __name__ == "__main__":
    analyzer = ReviewAnalyzer()
    
    # Example reviews
    analyzer.add_review("Great service and friendly staff!", 5, datetime.now())
    analyzer.add_review("Terrible experience, will never come back", 1, datetime.now())
    analyzer.add_review("Average service, could be better", 3, datetime.now())
    
    # Generate report
    report_path = analyzer.generate_weekly_report()
    print(f"Report generated at: {report_path}")
    
    # Get complaints
    complaints = analyzer.get_complaints()
    print("\nComplaints found:")
    print(complaints[['text', 'date']]) 
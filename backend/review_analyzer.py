"""
ReviewAnalyzer: A comprehensive tool for analyzing customer reviews using advanced NLP techniques.
This class combines sentiment analysis, complaint detection, and semantic search capabilities
to provide deep insights into customer feedback.

Features:
- Sentiment analysis using DistilBERT
- Complaint detection using spaCy
- Semantic search using Sentence Transformers
- Review categorization and theme extraction
- Weekly report generation
- Trend analysis
"""

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
from typing import List, Dict, Any
from textblob import TextBlob
import re
import json

# Load environment variables
load_dotenv()

class ReviewAnalyzer:
    """
    A class for analyzing customer reviews using various NLP techniques.
    
    Attributes:
        chroma_client: ChromaDB client for vector storage
        collection: ChromaDB collection for storing review embeddings
        sentiment_analyzer: Transformer pipeline for sentiment analysis
        nlp: spaCy model for text processing
        encoder: Sentence transformer for semantic encoding
        reviews_df: Pandas DataFrame storing all reviews and their analysis
    """

    def __init__(self, reviews_file: str = "reviews.json"):
        """
        Initialize the ReviewAnalyzer with required models and storage.
        
        Args:
            reviews_file (str): Path to JSON file containing initial reviews
        """
        # Initialize ChromaDB for vector storage
        self.chroma_client = chromadb.Client()
        self.collection = self.chroma_client.create_collection(name="reviews")
        
        # Load sentiment analysis model
        self.sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
        
        # Load spaCy for text processing
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
        
        # Load initial reviews
        self._load_reviews_from_file(reviews_file)
    
    def _load_reviews_from_file(self, reviews_file: str):
        """
        Load reviews from a JSON file and process them.
        
        Args:
            reviews_file (str): Path to the JSON file containing reviews
        """
        try:
            with open(reviews_file, 'r') as f:
                reviews_data = json.load(f)
                
            for review in reviews_data:
                self.add_review(
                    text=review['review_text'],
                    rating=review['rating'],
                    date=datetime.fromisoformat(review['date'] + "T00:00:00")
                )
        except FileNotFoundError:
            print(f"Warning: Reviews file '{reviews_file}' not found. Starting with empty dataset.")
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in '{reviews_file}'")
        except Exception as e:
            print(f"Error loading reviews: {str(e)}")
    
    def add_review(self, text: str, rating: int, date: datetime):
        """
        Add and analyze a new review.
        
        Args:
            text (str): The review text
            rating (int): Numerical rating (typically 1-5)
            date (datetime): Date of the review
        """
        # Get similar reviews for context
        similar_reviews = self._get_similar_reviews(text)
        
        # Analyze sentiment with context
        sentiment_result = self._analyze_sentiment_with_context(text, similar_reviews)
        sentiment = sentiment_result['label']
        sentiment_score = sentiment_result['score']
        
        # Detect complaints
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

    def _get_similar_reviews(self, text: str, n_results: int = 3) -> List[str]:
        """
        Find semantically similar reviews using vector similarity.
        
        Args:
            text (str): The review text to find similar reviews for
            n_results (int): Number of similar reviews to return
        
        Returns:
            List[str]: List of similar review texts
        """
        query_embedding = self.encoder.encode([text])[0].tolist()
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results['documents'][0] if results['documents'] else []
    
    def _analyze_sentiment_with_context(self, text: str, similar_reviews: List[str]) -> Dict:
        """
        Analyze sentiment of a review considering similar reviews as context.
        
        Args:
            text (str): The review text to analyze
            similar_reviews (List[str]): List of similar reviews for context
        
        Returns:
            Dict: Sentiment analysis result with label and score
        """
        if not similar_reviews:
            result = self.sentiment_analyzer(text)[0]
        else:
            context = " ".join(similar_reviews + [text])
            result = self.sentiment_analyzer(context)[0]
        
        # Normalize the score to be between -1 and 1
        # For POSITIVE label, keep the score as is
        # For NEGATIVE label, negate the score
        normalized_score = result['score'] if result['label'] == 'POSITIVE' else -result['score']
        
        return {
            'label': result['label'],
            'score': normalized_score
        }
    
    def _detect_complaint_with_context(self, text: str, similar_reviews: List[str]) -> bool:
        """
        Detect if a review contains complaints using context.
        
        Args:
            text (str): The review text to analyze
            similar_reviews (List[str]): List of similar reviews for context
        
        Returns:
            bool: True if the review contains complaints
        """
        combined_text = " ".join(similar_reviews + [text])
        doc = self.nlp(combined_text)
        
        complaint_keywords = ['bad', 'terrible', 'awful', 'horrible', 'disappointed', 'never again',
                            'poor', 'worst', 'unacceptable', 'avoid', 'waste', 'ripoff']
        complaint_phrases = ['not worth', 'would not recommend', 'stay away', 'never coming back']
        
        has_keywords = any(token.text.lower() in complaint_keywords for token in doc)
        has_phrases = any(phrase in combined_text.lower() for phrase in complaint_phrases)
        
        return has_keywords or has_phrases
    
    def generate_weekly_report(self) -> str:
        """
        Generate a weekly sentiment analysis report.
        
        Returns:
            str: Formatted report text
        """
        last_week = datetime.now() - timedelta(days=7)
        weekly_data = self.reviews_df[self.reviews_df['date'] >= last_week]
        
        avg_sentiment = weekly_data['sentiment_score'].mean()
        total_reviews = len(weekly_data)
        positive_reviews = len(weekly_data[weekly_data['sentiment'] == 'POSITIVE'])
        negative_reviews = len(weekly_data[weekly_data['sentiment'] == 'NEGATIVE'])
        
        report = f"Weekly Review Analysis Report\n"
        report += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"Total Reviews: {total_reviews}\n"
        report += f"Average Sentiment Score: {avg_sentiment:.2f}\n"
        report += f"Positive Reviews: {positive_reviews}\n"
        report += f"Negative Reviews: {negative_reviews}\n\n"
        
        complaints = weekly_data[weekly_data['complaint'] == True]
        if not complaints.empty:
            report += "Complaints Summary:\n"
            for _, row in complaints.iterrows():
                report += f"- {row['text'][:100]}...\n"
        
        return report
    
    def get_sentiment_trends(self) -> Dict[str, float]:
        """
        Get sentiment trends over time.
        
        Returns:
            Dict[str, float]: Daily sentiment scores
        """
        df = self.reviews_df.copy()
        df['date'] = pd.to_datetime(df['date']).dt.date
        daily_sentiment = df.groupby('date')['sentiment_score'].mean()
        return daily_sentiment.to_dict()
    
    def get_complaints(self) -> pd.DataFrame:
        """
        Get all reviews marked as complaints.
        
        Returns:
            pd.DataFrame: DataFrame containing complaint reviews
        """
        return self.reviews_df[self.reviews_df['complaint'] == True]
    
    def extract_top_themes(self, n: int = 5) -> Dict[str, int]:
        """
        Extract most common themes from reviews.
        
        Args:
            n (int): Number of top themes to return
        
        Returns:
            Dict[str, int]: Theme frequencies
        """
        all_text = " ".join(self.reviews_df['text'].tolist())
        doc = self.nlp(all_text)
        
        themes = []
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) > 1:
                themes.append(chunk.text.lower())
        
        theme_counts = pd.Series(themes).value_counts()
        return theme_counts.head(n).to_dict()
    
    def categorize_reviews(self) -> Dict[str, List[str]]:
        """
        Categorize reviews into predefined categories.
        
        Returns:
            Dict[str, List[str]]: Reviews grouped by category
        """
        categories = {
            'service': [],
            'food': [],
            'ambiance': [],
            'price': [],
            'other': []
        }
        
        for _, row in self.reviews_df.iterrows():
            text = row['text'].lower()
            if any(word in text for word in ['service', 'staff', 'server', 'waiter', 'waitress']):
                categories['service'].append(row['text'])
            elif any(word in text for word in ['food', 'dish', 'meal', 'menu', 'taste']):
                categories['food'].append(row['text'])
            elif any(word in text for word in ['ambiance', 'atmosphere', 'decor', 'music', 'noise']):
                categories['ambiance'].append(row['text'])
            elif any(word in text for word in ['price', 'cost', 'expensive', 'cheap', 'value']):
                categories['price'].append(row['text'])
            else:
                categories['other'].append(row['text'])
        
        return categories

# Example usage
if __name__ == "__main__":
    analyzer = ReviewAnalyzer()
    
    # Generate report
    report = analyzer.generate_weekly_report()
    print(report)
    
    # Get complaints
    complaints = analyzer.get_complaints()
    print("\nComplaints found:")
    print(complaints[['text', 'date']]) 
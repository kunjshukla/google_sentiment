"""
ReviewFetcher: A class for fetching and managing reviews from a CSV file.
This class provides functionality to read and process reviews from a CSV file.

Features:
- CSV file reading
- Review data processing
- Basic review filtering
"""

import pandas as pd
from datetime import datetime
import os

class ReviewFetcher:
    """
    A class for fetching and managing reviews from a CSV file.
    
    Attributes:
        reviews_df (pd.DataFrame): DataFrame containing all reviews
        file_path (str): Path to the CSV file containing reviews
    """

    def __init__(self, file_path: str = "sample_reviews.csv"):
        """
        Initialize the ReviewFetcher.
        
        Args:
            file_path (str): Path to the CSV file containing reviews
        """
        self.file_path = file_path
        self.reviews_df = pd.DataFrame()
        self._load_reviews_from_file()
    
    def _load_reviews_from_file(self):
        """
        Load reviews from the CSV file.
        
        Raises:
            FileNotFoundError: If the CSV file is not found
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Reviews file '{self.file_path}' not found.")
        
        self.reviews_df = pd.read_csv(self.file_path)
        # Convert date string to datetime if needed
        if 'date' in self.reviews_df.columns:
            self.reviews_df['date'] = pd.to_datetime(self.reviews_df['date'])
    
    def get_reviews(self, limit: int = None) -> pd.DataFrame:
        """
        Get reviews from the CSV file.
        
        Args:
            limit (int, optional): Maximum number of reviews to return
        
        Returns:
            pd.DataFrame: DataFrame containing the reviews
        """
        if limit:
            return self.reviews_df.head(limit)
        return self.reviews_df
    
    def get_recent_reviews(self, days: int = 7) -> pd.DataFrame:
        """
        Get reviews from the last N days.
        
        Args:
            days (int): Number of days to look back
        
        Returns:
            pd.DataFrame: DataFrame containing recent reviews
        """
        if 'date' not in self.reviews_df.columns:
            return self.reviews_df
        
        cutoff_date = datetime.now() - pd.Timedelta(days=days)
        return self.reviews_df[self.reviews_df['date'] >= cutoff_date]
    
    def get_reviews_by_rating(self, rating: int) -> pd.DataFrame:
        """
        Get reviews with a specific rating.
        
        Args:
            rating (int): Rating value to filter by
        
        Returns:
            pd.DataFrame: DataFrame containing filtered reviews
        """
        if 'rating' not in self.reviews_df.columns:
            return self.reviews_df
        
        return self.reviews_df[self.reviews_df['rating'] == rating]
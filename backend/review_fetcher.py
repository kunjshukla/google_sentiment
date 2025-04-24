"""
ReviewFetcher: A class for fetching and managing reviews from uploaded files.
This class provides functionality to read and process reviews from uploaded files.

Features:
- File upload handling
- Review data processing
- Basic review filtering
"""

import pandas as pd
from datetime import datetime
import io

class ReviewFetcher:
    """
    A class for fetching and managing reviews from uploaded files.
    
    Attributes:
        reviews_df (pd.DataFrame): DataFrame containing all reviews
    """

    def __init__(self):
        """
        Initialize the ReviewFetcher.
        """
        self.reviews_df = pd.DataFrame()
    
    def load_reviews_from_file(self, file_data: bytes) -> None:
        """
        Load reviews from uploaded file data.
        
        Args:
            file_data (bytes): The uploaded file data in bytes format
        
        Raises:
            ValueError: If the file data is invalid or cannot be processed
        """
        try:
            # Read the file data into a DataFrame
            self.reviews_df = pd.read_csv(io.BytesIO(file_data))
            
            # Convert date string to datetime if needed
            if 'date' in self.reviews_df.columns:
                self.reviews_df['date'] = pd.to_datetime(self.reviews_df['date'])
                
            # Validate required columns
            required_columns = ['date', 'text', 'rating']
            missing_columns = [col for col in required_columns if col not in self.reviews_df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
                
        except Exception as e:
            raise ValueError(f"Error processing file: {str(e)}")
    
    def get_reviews(self, limit: int = None) -> pd.DataFrame:
        """
        Get reviews from the loaded file.
        
        Args:
            limit (int, optional): Maximum number of reviews to return
        
        Returns:
            pd.DataFrame: DataFrame containing the reviews
        """
        if self.reviews_df.empty:
            raise ValueError("No reviews loaded. Please upload a file first.")
            
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
        if self.reviews_df.empty:
            raise ValueError("No reviews loaded. Please upload a file first.")
            
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
        if self.reviews_df.empty:
            raise ValueError("No reviews loaded. Please upload a file first.")
            
        if 'rating' not in self.reviews_df.columns:
            return self.reviews_df
        
        return self.reviews_df[self.reviews_df['rating'] == rating] 
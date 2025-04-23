# Google Reviews Sentiment Analysis Tool

This tool helps businesses analyze their reviews by providing:
- Sentiment analysis of reviews
- Weekly summary reports
- Real-time complaint detection
- Sentiment trend visualization

## Features

- **Sentiment Analysis**: Uses Hugging Face's DistilBERT model for accurate sentiment classification
- **Complaint Detection**: Identifies negative reviews and complaints using keyword matching
- **Weekly Reports**: Generates PDF reports with sentiment trends and complaint summaries
- **Vector Storage**: Uses ChromaDB for efficient review storage and retrieval
- **RAG Workflow**: Implements Retrieval-Augmented Generation for better analysis

## Setup

1. Run the setup script:
```bash
python setup.py
```

This will:
- Create a virtual environment (if not exists)
- Install all required dependencies
- Download necessary models (spaCy, sentence transformers, sentiment analysis)

## Usage with Sample Data

1. Run the sample analyzer:
```bash
python sample_review_analyzer.py
```

This will:
- Process sample reviews from `sample_reviews.json`
- Generate a weekly report
- Show sentiment analysis results
- Display detected complaints
- Create visualizations

## Output

- Weekly PDF reports in `weekly_report.pdf`
- Sentiment trend visualization in `sentiment_trend.png`
- Console output with analysis results

## Customization

You can customize:
- Add more reviews to `sample_reviews.json`
- Modify complaint keywords in `review_analyzer.py`
- Adjust report format in `review_analyzer.py`

## Future Integration with Google Reviews API

When you have access to the Google Reviews API:
1. Create a `.env` file with your API key:
```
GOOGLE_PLACES_API_KEY=your_api_key_here
```
2. Update the `place_id` in `google_reviews_fetcher.py`
3. Run `python google_reviews_fetcher.py`

## Note

This tool uses free and open-source models and libraries. No paid API keys are required for the sample data version.
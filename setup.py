import subprocess
import sys
import os

def install_dependencies():
    """Install all required Python packages"""
    print("Installing Python dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def download_models():
    """Download required models"""
    print("\nDownloading spaCy model...")
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    
    print("\nDownloading sentence transformer model...")
    from sentence_transformers import SentenceTransformer
    SentenceTransformer('all-MiniLM-L6-v2')
    
    print("\nDownloading sentiment analysis model...")
    from transformers import pipeline
    pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

def main():
    """Main setup function"""
    print("Setting up the review analysis system...")
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists("venv"):
        print("\nCreating virtual environment...")
        subprocess.check_call([sys.executable, "-m", "venv", "venv"])
    
    # Install dependencies
    install_dependencies()
    
    # Download models
    download_models()
    
    print("\nSetup completed successfully!")
    print("\nTo run the analysis, use:")
    print("python sample_review_analyzer.py")

if __name__ == "__main__":
    main() 
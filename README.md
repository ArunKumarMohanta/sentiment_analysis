---

# YouTube Video Sentiment and Emotion Analysis  

This project provides an in-depth analysis of **YouTube videos** by evaluating the sentiments and emotions of both the **viewers** (via comments) and the **content creators** (via titles, descriptions, tags, and transcripts). The results are visualized in easy-to-interpret **graphs** showing the emotion distribution and overall sentiment.

## Table of Contents  
- [Features](#features)  
- [Installation](#installation)  
- [Usage](#usage)  
- [Project Structure](#project-structure)  
- [Screenshots](#screenshots)  
- [Dependencies](#dependencies)  
- [API Setup](#api-setup)  
- [License](#license)  

## Features  
- **Extract Video ID**: Automatically parses the YouTube video URL to get the video ID.  
- **Viewers' Sentiment Analysis**: Analyzes top-level comments on the video and detects the viewers' sentiment using NLP.  
- **Creator's Content Analysis**: Analyzes the video title, description, tags, and transcripts (if available).  
- **Emotion Detection**: Identifies a wide range of emotions (joy, sadness, anger, etc.) from both the creator and the viewers using a predefined emotion list.  
- **Sentiment Classification**: Uses the NLTK `SentimentIntensityAnalyzer` to determine whether the content has a positive, neutral, or negative sentiment.  
- **Graphical Visualization**: Displays the emotions and sentiment data through custom bar graphs for both the **creator** and **viewers**.

## Installation  

1. **Clone the repository**:  
   git clone https://github.com/ArunKumarMohanta/sentiment_analysis.git
   cd sentiment_analysis

2. **Set up a virtual environment (optional)**:  
   python -m venv venv  
   source venv/bin/activate  # On Linux/Mac
   .\venv\Scripts\activate   # On Windows

3. **Install dependencies**:  
   pip install -r requirements.txt  

4. **Download NLTK resources**:  
   Open a Python shell and run the following:
   import nltk
   
   nltk.download('vader_lexicon')
   
   nltk.download('punkt')
   
   nltk.download('wordnet')
   
   nltk.download('stopwords')
5. **Run the project:**
   
   yt_analysis_ver2.0.py
   

## Usage  

1. **Get YouTube Data API Key** (see [API Setup](#api-setup)).  
2. **Run the main script**:  
  yt_analysis_ver2.0.py
3. When prompted, **enter a valid YouTube video link**.  
4. The program will:  
   - Extract viewer comments and the creator’s content (title, tags, description, and transcript).
   - Analyze emotions and sentiment.
   - Generate emotion distribution graphs for both the creator and viewers.
   - Save the graphs as PNG files.

## Project Structure  
sentiment_analysis/  
│  
├── yt_analysis_ver2.0.py # Main Python script  
├── requirements.txt      # Required Python packages  
├── emotion.txt           # List of emotion words and their labels  
├── read.txt              # File storing extracted viewer comments  
├── read1.txt             # File storing extracted creator's content  
├── graph_viewers.png     # Generated graph for viewers' emotions  
├── graph_creator.png     # Generated graph for creator's emotions  
└── README.md             # Project documentation  

## Screenshots 
Viewers' Emotion:

![graph_viewers'](https://github.com/user-attachments/assets/0a54c6a8-c175-4d81-9d8f-f926e2ef1e50)


Creator's Emotions:

![image](https://github.com/user-attachments/assets/8282430d-9612-410c-ae19-a104da98ff76)



## Dependencies  
- Python 3.x  
- `google-api-python-client`: For accessing YouTube API.  
- `youtube-transcript-api`: For fetching video transcripts.  
- `nltk`: For natural language processing and sentiment analysis.  
- `matplotlib`: For plotting emotion distribution graphs.

## API Setup  

1. Go to [Google Cloud Console](https://console.cloud.google.com/).  
2. Create a project and enable **YouTube Data API v3**.  
3. Generate an **API key**.  
4. In `yt_analysis_ver2.0.py`, replace the `DEVELOPER_KEY` with your API key:
   
   DEVELOPER_KEY = "YOUR_API_KEY_HERE"
   

## License  
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

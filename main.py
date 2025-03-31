main.py:from fastapi import FastAPI, HTTPException
import tweepy
from textblob import TextBlob
import os
from pydantic import BaseModel
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Twitter API credentials (set these in your .env file)
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

if not BEARER_TOKEN:
    raise Exception("BEARER_TOKEN not found. Please set BEARER_TOKEN in your environment variables.")

# Initialize Tweepy Client for Twitter API v2
client = tweepy.Client(bearer_token=BEARER_TOKEN)

def analyze_sentiment(text: str):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity

    if polarity > 0:
        return "Positive"
    elif polarity < 0:
        return "Negative"
    else:
        return "Neutral"

def fetch_tweets(keyword: str, count: int):
    try:
        # Ensure count is within allowed range [10, 100]
        max_results = count
        if count < 10:
            max_results = 10
        elif count > 100:
            max_results = 100

        # Using Twitter API v2 to search recent tweets
        response = client.search_recent_tweets(
            query=keyword,
            max_results=max_results,
            tweet_fields=["created_at", "author_id"]
        )
        tweet_data = []
        if response.data:
            for tweet in response.data:
                text = tweet.text
                sentiment = analyze_sentiment(text)
                tweet_data.append({
                    "tweet": text, 
                    "sentiment": sentiment,
                    "created_at": tweet.created_at,
                    "author_id": tweet.author_id
                })
        return tweet_data
    except tweepy.TooManyRequests as e:
        # If Tweepy specifically throws TooManyRequests, handle it here
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please wait and try again later.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class TweetRequest(BaseModel):
    keyword: str
    count: int

@app.get("/")
def home():
    return {"message": "Sentiment Analysis API is running!"}

@app.post("/fetch_tweets/")
def get_tweets(request: TweetRequest):
    return fetch_tweets(request.keyword, request.count)

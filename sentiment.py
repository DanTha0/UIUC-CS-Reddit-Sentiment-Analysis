import pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

# Download VADER lexicon if not already
nltk.download('vader_lexicon')

sia = SentimentIntensityAnalyzer()

# --------------------------------------------
# Compute sentiment
# --------------------------------------------
def sentiment(text):
    if not text:
        return 0
    return sia.polarity_scores(text)["compound"]

# --------------------------------------------
# Load saved comments
# --------------------------------------------
df = pd.read_pickle("uiuc_course_comments.pkl")
print(f"Loaded {len(df)} posts from saved data.")

# Compute sentiment
df["sentiment_title"] = df["title"].apply(sentiment)
df["sentiment_comments"] = df["comments"].apply(
    lambda lst: sum(sentiment(c) for c in lst) / (len(lst) or 1)
)
df["sentiment_avg"] = (df["sentiment_title"] + df["sentiment_comments"]) / 2

# Save updated DataFrame if desired
df.to_pickle("uiuc_course_sentiments.pkl")
print("Saved updated DataFrame with sentiments.", df)
print("\nTop sentiment per course:\n")
print(df.groupby("course")["sentiment_avg"].mean().sort_values())

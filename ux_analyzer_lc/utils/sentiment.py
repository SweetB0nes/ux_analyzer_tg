from nltk.sentiment import SentimentIntensityAnalyzer
_analyzer = None

def get_analyzer():
    global _analyzer
    if _analyzer is None:
        _analyzer = SentimentIntensityAnalyzer()
    return _analyzer

def sentiment_score(text: str) -> float:
    s = get_analyzer().polarity_scores(text)
    return s.get('compound', 0.0)

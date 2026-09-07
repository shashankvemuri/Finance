from collections.abc import Sequence

import pandas as pd


def sentiment(texts: Sequence[str]) -> pd.DataFrame:
    """Optional VADER text scores; descriptive language sentiment, not a trading forecast."""
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

    if isinstance(texts, str) or not len(texts) or any(not isinstance(text, str) for text in texts):
        raise ValueError("provide a nonempty sequence of texts")
    analyzer = SentimentIntensityAnalyzer()
    return pd.DataFrame([{"text": text, **analyzer.polarity_scores(text)} for text in texts])

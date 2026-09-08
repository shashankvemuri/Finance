from collections.abc import Sequence

import pandas as pd


def sentiment(texts: Sequence[str]) -> pd.DataFrame:
    """Optional VADER text scores; descriptive language sentiment, not a trading forecast."""
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

    if isinstance(texts, str) or not len(texts) or any(not isinstance(text, str) for text in texts):
        raise ValueError("provide a nonempty sequence of texts")
    analyzer = SentimentIntensityAnalyzer()
    return pd.DataFrame([{"text": text, **analyzer.polarity_scores(text)} for text in texts])


def sentence_sentiment(text: str) -> pd.DataFrame:
    """Sentence-level evidence for transcript/article language scores."""
    import re

    if not isinstance(text, str) or not text.strip():
        raise ValueError("provide nonempty article text")
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n\s*\n", text) if s.strip()]
    return sentiment(sentences).assign(sentence=range(1, len(sentences) + 1))


def social_mentions(posts: pd.DataFrame, tickers: Sequence[str]) -> pd.DataFrame:
    """Count cashtags or exact uppercase symbols from an explicit universe; one mention/post."""
    import re

    if not {"text", "id"} <= set(posts) or posts.id.duplicated().any():
        raise ValueError("unique post ids and text required")
    rows = []
    for ticker in dict.fromkeys(tickers):
        pattern = re.compile(r"(?<![A-Za-z0-9])\$?" + re.escape(ticker) + r"(?![A-Za-z0-9])")
        selected = posts[posts.text.map(lambda text, pattern=pattern: bool(pattern.search(text)))]
        if len(selected):
            scores = sentiment(selected.text.tolist())
            rows.append(
                {"ticker": ticker, "posts": len(selected), "compound": scores.compound.mean()}
            )
    return pd.DataFrame(rows, columns=["ticker", "posts", "compound"]).sort_values(
        "posts", ascending=False
    )

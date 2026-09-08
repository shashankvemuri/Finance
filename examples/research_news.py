"""Headline and transcript language analysis. Add --live for public sources."""

import sys

from finance.analytics import sentence_sentiment, sentiment
from finance.data import Finviz, TradingView, article_text, transcript_index


def main():
    if "--live" in sys.argv:
        provider = Finviz()
        news = provider.news("AAPL")
        print(news[["title", "url"]].head(5).to_string(index=False))
        print(sentiment(news.title.head(20).tolist())[["compound"]].describe())
        print(TradingView().recommendations(["NASDAQ:AAPL", "NASDAQ:MSFT"]))
        transcripts = transcript_index()
        print("Transcript source:", transcripts.url.iloc[0])
        text = article_text(transcripts.url.iloc[0])
    else:
        text = "Revenue increased strongly. We face significant uncertainty and weaker demand. Cash flow remained stable."
    scores = sentence_sentiment(text)
    print(
        "Sentence counts:",
        len(scores),
        "Positive:",
        (scores.compound >= 0.05).sum(),
        "Negative:",
        (scores.compound <= -0.05).sum(),
    )
    print("Mean descriptive sentiment:", round(scores.compound.mean(), 3))


if __name__ == "__main__":
    main()

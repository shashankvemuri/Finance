from textblob import TextBlob
import requests
import numpy as np

# Retrieves earnings call transcript from API.
def get_earnings_call_transcript(api_key, company, quarter, year):
    url = f'https://financialmodelingprep.com/api/v3/earning_call_transcript/{company}?quarter={quarter}&year={year}&apikey={api_key}'
    response = requests.get(url)
    return response.json()[0]['content']

# Performs sentiment analysis on the transcript.
def analyze_sentiment(transcript):
    sentiment_call = TextBlob(transcript)
    return sentiment_call

# Counts the number of positive, negative, and neutral sentences.
def count_sentiments(sentiment_call):
    positive, negative, neutral = 0, 0, 0
    all_sentences = []

    for sentence in sentiment_call.sentences:
        polarity = sentence.sentiment.polarity
        if polarity < 0:
            negative += 1
        elif polarity > 0:
            positive += 1
        else:
            neutral += 1
        all_sentences.append(polarity)

    return positive, negative, neutral, np.array(all_sentences)

def main():
    api_key = 'your api key'
    company = 'AAPL'

    # Get transcript and perform sentiment analysis
    transcript = get_earnings_call_transcript(api_key, company, 3, 2020)
    sentiment_call = analyze_sentiment(transcript)

    # Count sentiments and calculate mean polarity
    positive, negative, neutral, all_sentences = count_sentiments(sentiment_call)
    mean_polarity = all_sentences.mean()

    # Print results
    print(f"Earnings Call Transcript for {company}:\n{transcript}\n")
    print(f"Overall Sentiment: {sentiment_call.sentiment}")
    print(f"Positive Sentences: {positive}, Negative Sentences: {negative}, Neutral Sentences: {neutral}")
    print(f"Average Sentence Polarity: {mean_polarity}")

    # Print very positive sentences
    print("\nHighly Positive Sentences:")
    for sentence in sentiment_call.sentences:
        if sentence.sentiment.polarity > 0.8:
            print(sentence)

if __name__ == "__main__":
    main()
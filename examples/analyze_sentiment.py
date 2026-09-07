from finance.analytics import sentiment


def main():
    texts = ["Revenue grew and profitability improved.", "Demand collapsed and losses increased."]
    print(sentiment(texts).to_string(index=False))


if __name__ == "__main__":
    main()

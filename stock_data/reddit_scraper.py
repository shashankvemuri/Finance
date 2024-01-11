import praw
import pandas as pd

# Import Reddit API credentials from config file
from config import get_reddit
my_client_id, my_client_secret, my_user_agent = get_reddit()

# Initialize a PRAW Reddit instance with provided credentials
reddit = praw.Reddit(client_id=my_client_id, client_secret=my_client_secret, user_agent=my_user_agent)

# Define subreddit and number of articles to scrape
subreddit_name = 'fatFIRE'
num_of_articles = 5

# Fetch posts from the specified subreddit
posts = []
subreddit = reddit.subreddit(subreddit_name)
for post in subreddit.new(limit=num_of_articles):
    # Append relevant post details to the list
    posts.append([post.title, post.score, post.id, post.subreddit, post.url, post.num_comments, post.selftext, post.created])

# Convert the list of posts into a Pandas DataFrame
# Columns: title, score, id, subreddit, url, num_comments, body (post content), created (timestamp)
posts_df = pd.DataFrame(posts, columns=['title', 'score', 'id', 'subreddit', 'url', 'num_comments', 'body', 'created'])

# Drop unnecessary columns from the DataFrame for simplicity
posts_df = posts_df.drop(columns=['score', 'id', 'subreddit', 'created', 'url'])

# Display the resulting DataFrame
print(posts_df)

# Optionally, print specific post details such as title and body of the last post
print("Title of the last post:", posts_df['title'].tolist()[-1])
print("Body of the last post:", posts_df['body'].tolist()[-1])
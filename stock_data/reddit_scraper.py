# import necessary libraries
import praw
import pandas as pd

# get client credentials and user agent from config.py file
from config import get_reddit
my_client_id, my_client_secret, my_user_agent = get_reddit()

# create a Reddit instance using praw
reddit = praw.Reddit(client_id=my_client_id, client_secret=my_client_secret, user_agent=my_user_agent)

# define subreddit and number of articles to retrieve
subreddit_name = 'fatFIRE'
num_of_articles = 5

# retrieve posts from subreddit
posts = []
subreddit = reddit.subreddit(subreddit_name)
for post in subreddit.new(limit=num_of_articles):
    posts.append([post.title, post.score, post.id, post.subreddit, post.url, post.num_comments, post.selftext, post.created])
    
# create a pandas dataframe with the post data and drop unnecessary columns
posts_df = pd.DataFrame(posts, columns=['title', 'score', 'id', 'subreddit', 'url', 'num_comments', 'body', 'created'])
posts_df = posts_df.drop(columns=['score', 'id', 'subreddit', 'created', 'url'])

# print the resulting dataframe and specific post data
print(posts_df)
print(posts_df['title'].tolist()[4])
print(posts_df['body'].tolist()[4])
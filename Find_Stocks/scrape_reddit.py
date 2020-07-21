import praw
from config import get_reddit
import pandas as pd

pd.set_option('display.max_columns', None)

my_client_id, my_client_secret, my_user_agent = get_reddit()
reddit = praw.Reddit(client_id=my_client_id, client_secret=my_client_secret, user_agent=my_user_agent)

# get 10 top posts from the fatFIRE subreddit
top_posts = reddit.subreddit('fatFIRE').top(limit=1)
for post in top_posts:
    print(post.title)
    print(post.selftext)

posts = []
subreddit = reddit.subreddit('fatFIRE')
for post in subreddit.top(limit=10):
    posts.append([post.title, post.score, post.id, post.subreddit, post.url, post.num_comments, post.selftext, post.created])
posts = pd.DataFrame(posts,columns=['title', 'score', 'id', 'subreddit', 'url', 'num_comments', 'body', 'created'])
# print(posts)
import praw
from config import get_reddit
import pandas as pd

pd.set_option('display.max_columns', None)

my_client_id, my_client_secret, my_user_agent = get_reddit()
reddit = praw.Reddit(client_id=my_client_id, client_secret=my_client_secret, user_agent=my_user_agent)

sub = 'fatFIRE'
num_of_articles = 5

# # get posts from subreddit
# wanted_posts = reddit.subreddit(sub).new(limit = num_of_articles)
# for post in wanted_posts:
#     print(post.title)
#     print(post.selftext)

posts = []
subreddit = reddit.subreddit(sub)
for post in subreddit.new(limit = num_of_articles):
    posts.append([post.title, post.score, post.id, post.subreddit, post.url, post.num_comments, post.selftext, post.created])
posts = pd.DataFrame(posts,columns=['title', 'score', 'id', 'subreddit', 'url', 'num_comments', 'body', 'created'])
posts = posts.drop(columns = ['score', 'id', 'subreddit', 'created', 'url'])
# posts = posts.set_index('title')
print(posts)

print ()
print (posts['title'].tolist()[4])
print (posts['body'].tolist()[4])
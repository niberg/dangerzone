import praw, codecs, sys

"""Use this to download posts en masse from a specific :subreddit:. Set the limit of number of posts to download with :limit:. Note that all posts will be downloaded to the current directory."""

agent = "" # User agent for PRAW. Must be set.
subreddit = "" # Must be a valid subreddit
limit = 0 # Must be an integer > 0

def main():
	validateVars()
	r = praw.Reddit(user_agent=agent)
	submissions = r.get_subreddit(subreddit).get_new(limit=limit)
	writeSubmissionsToFile(submissions)
	
def writeSubmissionsToFile(submissions):
	for post in submissions:
		f = codecs.open(subreddit + '_' + str(post.id) + '.txt', 'w', 'utf-8')
		f.write(post.title)
		f.write("\n\n")
		f.write(post.selftext)
		f.close()
	
def validateVars():
	if not subreddit:
		print 'You must specify a subreddit to download posts from. Open this script in an editor to see info on how to do so.'
		exit()
	if not agent:
		print 'You must specify a user agent name for PRAW. Open this script in an editor to see info on how to do so.'
		exit()
	if limit == 0:
		print 'You must set the number of posts to download to a positive integer. Open this script in an editor to see info on how to do so.'
		exit()
import praw
import codecs
r = praw.Reddit(user_agent='team_marina')
submissions = r.get_subreddit('rant').get_new(limit=5)
count = 0
for x in submissions:
	f = codecs.open(str(count).zfill(4) + '.txt', 'w', 'utf-8')
	f.write(x.title)
	f.write("\n\n")
	f.write(x.selftext)
	f.close()
	count += 1
	

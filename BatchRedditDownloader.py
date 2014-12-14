import praw, codecs, sys, os, getopt
from collections import defaultdict
"""Use this to download posts en masse from specific :subreddits:. Set the limit of the total number of posts to go through with :limit:. Note that all posts will be downloaded to a folder "dataset" unless another folder is set with -f."""

counts = defaultdict(int)

def main():
    agent = "rmc" # User agent for PRAW. Must be set.
    subs = ["rant", "suicidewatch", "personalfinance"] # Must be a valid list of subreddits
    limit = 1000 # Must be an integer > 0
    folder = "dataset"
    getters = "get_new get_top get_top_from_year get_top_from_month get_top_from_week get_rising get_hot get_controversial".split()

    try:
        options, remainder = getopt.getopt(sys.argv[1:], 's:f:a:l:', ["subreddits=", "folder=", "useragent=", "limit="])
    except getopt.GetoptError as err:
        print str(err)
        sys.exit(2)

    for opt, arg in options:
        if opt in ('-s', '--subreddits'):
            subs = arg.split()
        elif opt in ('-f', '--folder'):
            folder = arg
        elif opt in ('-a', '--useragent'):
            agent = arg
        elif opt in ('-l', '--limit'):
            limit = int(arg)

    r = praw.Reddit(user_agent=agent)
    
    if not os.path.exists(folder):
        os.makedirs(folder)
    for s in subs:
        submissions = r.get_subreddit(s).get_new(limit=limit)
        writeSubmissionsToFile(submissions, folder)
        submissions = r.get_subreddit(s).get_top(limit=limit)
        writeSubmissionsToFile(submissions, folder)   
        submissions = r.get_subreddit(s).get_top_from_year(limit=limit)
        writeSubmissionsToFile(submissions, folder)        
        submissions = r.get_subreddit(s).get_top_from_month(limit=limit)
        writeSubmissionsToFile(submissions, folder) 
        submissions = r.get_subreddit(s).get_top_from_week(limit=limit)
        writeSubmissionsToFile(submissions, folder)    
        submissions = r.get_subreddit(s).get_rising(limit=limit)
        writeSubmissionsToFile(submissions, folder)   
        submissions = r.get_subreddit(s).get_hot(limit=limit)
        writeSubmissionsToFile(submissions, folder)        
        submissions = r.get_subreddit(s).get_controversial(limit=limit)
        writeSubmissionsToFile(submissions, folder)                
    print_counts(counts)
    
    
def writeSubmissionsToFile(submissions, folder):
        global counts
        for post in submissions:
            filename = post.subreddit.display_name.lower() + '_' + str(post.id) + '.txt'
            joinedpath = os.path.join(os.getcwd() + "/" + folder + "/", filename)
            if not os.path.isfile(joinedpath):
                counts[post.subreddit.display_name.lower()] += 1
                f = codecs.open(joinedpath, 'w', 'utf-8')
                f.write(post.title)
                f.write("\n\n")
                f.write(post.selftext)
                f.close()

def print_counts(counts):
    for key, freq in counts.iteritems():
        print "Found", freq, "posts from", key + "."
        
        
if __name__ == "__main__":    
    main()
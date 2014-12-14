import praw, time, os, sys, codecs

r = praw.Reddit(user_agent='team_marina')

def main():
    """Must declare these two variables before referencing them later. Did not work otherwise on Python 2.7."""
    toMonitor = []
    updateInterval = 0

    try:
        updateInterval = int(sys.argv[1])
        if updateInterval < 20:
            updateInterval = 20
        sys.stdout.write('Now monitoring subreddits: ')
        for s in sys.argv[2:]:
            sys.stdout.write(s + " ")
            toMonitor.append(s)
        if not os.path.exists("suicidal"):
            os.makedirs("suicidal")
        if not os.path.exists("nonsuicidal"):
            os.makedirs("nonsuicidal")
        if not os.path.exists("unknown_submissions"):
            os.makedirs("unknown_submissions")        
        print ""
    except:
        print 'Check your arguments.'
    while True:   
        for subreddit in toMonitor:
            get_submissions(subreddit)
        time.sleep(updateInterval*60)
            
def get_submissions(subreddit, limit=5):
    global timestamp_last_post
    submissions = r.get_subreddit(subreddit).get_new(limit=limit)
    for x in submissions:
        dir = os.getcwd() + "/unknown_submissions/"
        filename = subreddit + '_' + str(x.id) + '.txt'
        file = os.path.join(dir, filename)
        #Don't write unnecessarily
        if os.path.isfile(file):
            continue
        if os.path.isfile(os.path.join("/suicidal/", filename)) or os.path.isfile(os.path.join("/nonsuicidal/", filename)):
            continue
        f = codecs.open(file, 'w', 'utf-8')
        f.write(x.title)
        f.write("\n\n")
        f.write(x.selftext)
        f.close()
        
if __name__ == "__main__":    
    main()
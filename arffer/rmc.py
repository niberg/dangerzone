import praw
import codecs
import os
import pickle
import sys
from averagedperceptron import *
import shutil

r = praw.Reddit(user_agent='team_marina')
timestamp_last_post = 0
recall = 0
precision = 0
tp = 0
tn = 0
fp = 0
fn = 0
#Prevent stupid windows cmd from crashing (hopefully)
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
def main():
    try:
        load_bot()
    except:
        pass
    p = averagedperceptron()
    p.load() 
    newsubs = get_submissions("rant")
    check_submissions(newsubs, p, "rant")
    p.save()
    save_bot()
    
def get_submissions(subreddit, limit=20):
    global timestamp_last_post
    submissions = r.get_subreddit(subreddit).get_new(limit=limit)
    new_submissions = []
    reversed = []
    for x in submissions:
        reversed.insert(0, x)
    for x in reversed:
        if x.created <= timestamp_last_post:
            continue
        new_submissions.append(x)
        timestamp_last_post = x.created
        dir = os.getcwd() + "/unknown_submissions/"
        filename = subreddit + '_' + str(x.created) + '.txt'
        file = os.path.join(dir, filename)
        #Don't write unnecessarily
        if os.path.isfile(file):
            continue
        if os.path.isfile(os.path.join("/suicidewatch_submissions/", filename)) or os.path.isfile(os.path.join("/rant_submissions/", filename)):
            continue
        f = codecs.open(file, 'w', 'utf-8')
        f.write(x.title)
        f.write("\n\n")
        f.write(x.selftext)
        f.close()
    return new_submissions
        
def check_submissions(newsubs, p, subreddit):
    global tp
    global tn
    global fp
    global fn
    global precision
    global recall
    
    if len(newsubs) < 1:
        print "No new submissions!"
        return
    print "You have", len(newsubs), "post(s) to check"   
    for x in newsubs:
        filename = subreddit + "_" + str(x.created) + ".txt"
        print "*" * 80
        print x.title
        print "\n"
        print x.selftext
        features = p.extract_post_features(x.title + "\n\n" + x.selftext)
        prediction = p.predict(features)
        print "*" * 80
        if prediction:
            print "The perceptron thinks this post contains suicidal language."
        else:
            print "The perceptron does not think this post contains suicidal language."
        input = raw_input("Does this post contain suicidal language? yes/no\n")
        while (input.lower() != "yes" and input.lower() != "no"):
            print "Please enter yes or no."
            input = raw_input("Does this post contain suicidal language? yes/no\n")
        if input.lower() == "yes" and prediction:
            print "Thank you, weights will not be adjusted."
            tp += 1
            #Move to sw folder
            move_classified(filename, "/suicidewatch_submissions/")
        elif input.lower() == "yes" and not prediction:
            print "Thank you, weights will be adjusted."
            p.update(features, False)
            fn += 1
            #Move to sw folder
            move_classified(filename, "/suicidewatch_submissions/")
        elif input.lower() == "no" and not prediction:
            print "Thank you, weights will not be adjusted."
            tn += 1
            #Move to rant folder
            move_classified(filename, "/rant_submissions/")
        elif input.lower() == "no" and prediction:
            print "Thank you, weights will be adjusted."
            p.update(features, False)
            fp += 1
            #Move to rant folder
            move_classified(filename, "/rant_submissions/")
    #Prevent divide by zero error
    if tp > 0:
        precision = float(tp)/(tp + fp)
        recall = float(tp)/(fn + tp)
        fscore = 2 * ((precision * recall)/(precision + recall))
        
        print "Precision: " + str(precision*100) + " %"
        print "Recall: " + str(recall*100) + " %"
        print "F-score: " + str(fscore*100) + " %"
 
def move_classified(filename, destination):
    shutil.move(os.path.join(os.getcwd() + "/unknown_submissions/", filename), os.path.join(os.getcwd() + destination, filename)) 
            
def save_bot():
    global timestamp_last_post
    global tp
    global tn
    global fp
    global fn
    global precision
    global recall
    with codecs.open("botsave.pickle", "wb") as file:
        pickle.dump(timestamp_last_post, file, -1)
        pickle.dump(tp, file, -1)
        pickle.dump(tn, file, -1)
        pickle.dump(fp, file, -1)
        pickle.dump(fn, file, -1)
        pickle.dump(precision, file, -1)
        pickle.dump(recall, file, -1)

def load_bot():
    global timestamp_last_post
    global tp
    global tn
    global fp
    global fn
    global precision
    global recall
    with codecs.open("botsave.pickle", "rb") as file:
        timestamp_last_post = pickle.load(file)     
        tp = pickle.load(file)
        tn = pickle.load(file)
        fp = pickle.load(file)
        fn = pickle.load(file)
        precision = pickle.load(file)
        recall = pickle.load(file)    
main()
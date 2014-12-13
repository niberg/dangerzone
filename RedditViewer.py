import codecs, os, pickle, sys, shutil, readchar, textwrap
from Perceptron import *

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
    p = Perceptron()
    p.load() 
    newsubs = read_submissions()
    check_submissions(newsubs, p)
    p.save()
    save_bot()
    
def read_submissions():
    new_submissions = []
    for file in os.listdir("unknown_submissions"):
        filename = os.path.join("unknown_submissions", file)
        f = codecs.open(filename, 'r', 'utf-8')
        post = (f.read(), file)
        new_submissions.append(post)

    return new_submissions
        
def check_submissions(newsubs, p):
    global tp
    global tn
    global fp
    global fn
    global precision
    global recall
    global timestamp_last_post
    
    if len(newsubs) < 1:
        print "No new submissions!"
        return
    print "You have", len(newsubs), "post(s) to check"   
    for x in newsubs:
        features = p.extract_post_features(x[0])
        prediction = p.predict(features)
        filename = x[1]
        print "*" * 80
        print "Filename: ", filename
        print "*" * 80
        # titleEnd = x[0].find("\n")+1
        # print x[0][:titleEnd]
        # posttext = textwrap.wrap(x[0][titleEnd:], width=80)
        # for line in posttext:
        #     print line
        posttext = x[0].split("\n")
        posttext = [x for x in posttext if x]
        for s in posttext:
            #print textwrap.wrap(s, width=80)
            for line in textwrap.wrap(s, width=80):
                print line
            print ""

        print "*" * 80
        if prediction:
            print "The perceptron thinks this post contains suicidal language."
        else:
            print "The perceptron does not think this post contains suicidal language."
        print "Does this post contain suicidal language? [y]es/[n]o/[a]bort"
        char = readchar.readchar()

        while char != 'y' and char != 'n' and char != 'a':
            print "Please press a key."
            char = readchar.readchar()
        if char == 'a':
            save_bot()
            print_statistics()
            exit()
        if char == "y" and prediction:
            print "Thank you, weights will not be adjusted."
            tp += 1
            #Move to sw folder
            move_classified(filename, "/suicidal/")
        elif char == "y" and not prediction:
            print "Thank you, weights will be adjusted."
            p.update(features, False)
            fn += 1
            #Move to sw folder
            move_classified(filename, "/suicidal/")
        elif char == "n" and not prediction:
            print "Thank you, weights will not be adjusted."
            tn += 1
            #Move to rant folder
            move_classified(filename, "/nonsuicidal/")
        elif char == "n" and prediction:
            print "Thank you, weights will be adjusted."
            p.update(features, False)
            fp += 1
            #Move to rant folder
            move_classified(filename, "/nonsuicidal/")
    print_statistics()
    
 
def move_classified(filename, destination):
    shutil.move(os.path.join(os.getcwd() + "/unknown_submissions/", filename), os.path.join(os.getcwd() + destination, filename)) 
            
def save_bot():
    global tp
    global tn
    global fp
    global fn
    global precision
    global recall
    with codecs.open("botsave.pickle", "wb") as file:
        pickle.dump(tp, file, -1)
        pickle.dump(tn, file, -1)
        pickle.dump(fp, file, -1)
        pickle.dump(fn, file, -1)
        pickle.dump(precision, file, -1)
        pickle.dump(recall, file, -1)

def load_bot():
    global tp
    global tn
    global fp
    global fn
    global precision
    global recall
    with codecs.open("botsave.pickle", "rb") as file:
        tp = pickle.load(file)
        tn = pickle.load(file)
        fp = pickle.load(file)
        fn = pickle.load(file)
        precision = pickle.load(file)
        recall = pickle.load(file)    
        
def print_statistics():
    if tp > 0:
        precision = float(tp)/(tp + fp)
        recall = float(tp)/(fn + tp)
        fscore = 2 * ((precision * recall)/(precision + recall))
        print "\nTotal combined results:"
        print "Precision: " + str(precision*100) + " %"
        print "Recall: " + str(recall*100) + " %"
        print "F-score: " + str(fscore*100) + " %"
        
if __name__ == "__main__":    
    main()
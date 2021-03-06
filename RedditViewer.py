import codecs, os, pickle, sys, shutil, readchar, textwrap, random
from Perceptron import *

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
    random.shuffle(new_submissions)
    return new_submissions
        
def check_submissions(newsubs, p):
    global tp
    global tn
    global fp
    global fn
    cur_tp = 0
    cur_tn = 0
    cur_fp = 0
    cur_fn = 0
    global timestamp_last_post
    
    if len(newsubs) < 1:
        print "No new submissions!"
        return
    print "You have", len(newsubs), "post(s) to check"   
    for i, x in enumerate(newsubs):
        features = p.extract_post_features(x[0])
        prediction = p.predict(features)
        filename = x[1]
        print "*" * 80
        print "Filename: ", filename, "\t", str(i+1) + "/" + str(len(newsubs))
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
            print "\nTotal combined results:"
            print_statistics(tp, fp, tn, fn)
            print "\nResults for this session:"
            print_statistics(cur_tp, cur_fp, cur_tn, cur_fn)
            exit()
        if char == "y" and prediction:
            save_bot()
            print "Thank you, weights will not be adjusted."
            tp += 1
            cur_tp += 1
            #Move to sw folder
            move_classified(filename, "/suicidal/")
        elif char == "y" and not prediction:
            save_bot()
            print "Thank you, weights will be adjusted."
            #Send features and correct label to perceptron
            p.update(features, True)
            p.save(silent=True)
            fn += 1
            cur_fn += 1
            #Move to sw folder
            move_classified(filename, "/suicidal/")
        elif char == "n" and not prediction:
            save_bot()
            print "Thank you, weights will not be adjusted."
            tn += 1
            cur_tn += 1
            #Move to rant folder
            move_classified(filename, "/nonsuicidal/")
        elif char == "n" and prediction:
            save_bot()
            print "Thank you, weights will be adjusted."
            #Send features and correct label to perceptron
            p.update(features, False)
            p.save(silent=True)
            fp += 1
            cur_fp += 1
            #Move to rant folder
            move_classified(filename, "/nonsuicidal/")
    print "\nTotal combined results:"
    print_statistics(tp, fp, tn, fn)
    print "\nResults for this session:"
    print_statistics(cur_tp, cur_fp, cur_tn, cur_fn)
    
 
def move_classified(filename, destination):

    if destination == "/nonsuicidal/":
        if "true_" in filename or "false_" in filename:
            newname =  "false_" + filename[filename.find("_")+1:]
            shutil.move(os.path.join(os.getcwd() + "/unknown_submissions/", filename), os.path.join(os.getcwd() + destination, newname))
        else:
            newname =  "false_" + filename
            shutil.move(os.path.join(os.getcwd() + "/unknown_submissions/", filename), os.path.join(os.getcwd() + destination, newname))
    else:
        if "true_" in filename or "false_" in filename:
            newname =  "true_" + filename[filename.find("_")+1:]
            shutil.move(os.path.join(os.getcwd() + "/unknown_submissions/", filename), os.path.join(os.getcwd() + destination, newname))
        else:
            newname =  "true_" + filename
            shutil.move(os.path.join(os.getcwd() + "/unknown_submissions/", filename), os.path.join(os.getcwd() + destination, newname))


            
def save_bot():
    global tp
    global tn
    global fp
    global fn
    with codecs.open("botsave.pickle", "wb") as file:
        pickle.dump(tp, file, -1)
        pickle.dump(tn, file, -1)
        pickle.dump(fp, file, -1)
        pickle.dump(fn, file, -1)

def load_bot():
    global tp
    global tn
    global fp
    global fn
    with codecs.open("botsave.pickle", "rb") as file:
        tp = pickle.load(file)
        tn = pickle.load(file)
        fp = pickle.load(file)
        fn = pickle.load(file)
        
def print_statistics(tp, tn, fp, fn):
    print "True positives:", tp
    print "True negatives:", tn
    print "False positives:", fp
    print "False negatives:", fn
    print ""
    if tp > 0:
        precision = float(tp)/(tp + fp)
        recall = float(tp)/(fn + tp)
        fscore = 2 * ((precision * recall)/(precision + recall))
        print "Precision: " + str(precision*100) + " %"
        print "Recall: " + str(recall*100) + " %"
        print "F-score: " + str(fscore*100) + " %"

       
        
if __name__ == "__main__":    
    main()

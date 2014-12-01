from collections import defaultdict
import getopt
import sys
import os
import codecs
import re
import random
import pickle
from nltk.tokenize import word_tokenize, sent_tokenize
from main import *
import operator

#Current weights
weights = defaultdict(int)
#Cached weights for the averaging
cached_weights = defaultdict(int)
#Last time the feature was changed, for the averaging
timestamps = defaultdict(int)
#Number of iterations to run 
iterations = 4
count = 0
bias = 0
interactive = False
train = False
test = False
file = "dataset.arff"
percentage = 100

def main():
    global iterations
    global weights
    global bias
    global interactive
    global test
    global train
    global file
    
    try:
        options, remainder = getopt.getopt(sys.argv[1:], 'd:n:b:itrf=', ['dataset=', 'iterations=', 'bias=', 'interactive', 'test=', 'train='])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        
    for opt, arg in options:
        if opt in ('-d', '--dataset'):
            file = arg
        elif opt in ('-n', '--iterations'):
            iterations = int(arg)
        elif opt in ('-b', '--bias'):
            bias = float(arg)
        elif opt in ('-i', '--interactive'):
            interactive = True
            if train or test:
                print "Only one of parameters test, train and interactive can be given."
                usage()             
        elif opt in ('-t', '--test'):
            test = True   
            if train or interactive:
                print "Only one of parameters test, train and interactive can be given."
                usage()                
        elif opt in ('-r', '--train'):
            train = True    
            if test or interactive:
                print "Only one of parameters test, train and interactive can be given."
                usage()     
                

    if interactive:
        word_features, ngram_features = get_arff_features(file)
        load()
        print "Welcome to Perceptron 2000!"
        while 1:
            input = raw_input("Please input text to classify:\n\n")
            input = unicode(input, "utf-8")
            if not input:
                sys.exit(0)
            else:
                features = extract_post_features(input, word_features, ngram_features)
                prediction = predict(features)
                if prediction:
                    print "\nThe system classified this post as containing suicidal language.\n\n"
                else:
                    print "\nThe system classified this post as a rant.\n\n"
                print "The perceptron recognized the following features: \n"
                for word, value in word_features.iteritems():
                    if value in features:
                        sys.stdout.write(word + ", ")
                print "\n\n"
    if test:       
        all_features = read_arff(file)
        bin_features = binarize(all_features)
        load()
        true_positives = 0
        false_positives = 0
        true_negatives = 0
        false_negatives = 0
       
            
        for features, pclass in bin_features[1319:]:
            prediction = predict(features)

            if prediction == pclass:
                if pclass == True:
                    true_positives += 1
                else:
                    true_negatives += 1
            else:
                if pclass == False:
                    false_positives += 1
                else:
                    false_negatives += 1

        print "True positives: " + str(true_positives)
        print "True negatives: " + str(true_negatives)
        print "False positives: " + str(false_positives)
        print "False negatives: " + str(false_negatives)
        
        precision = float(true_positives)/(true_positives + false_positives)
        recall = float(true_positives)/(false_negatives + true_positives)
        fscore = 2 * ((precision * recall)/(precision + recall))
        
        print "Precision: " + str(round(precision*100, 2)) + " %"
        print "Recall: " + str(round(recall*100, 2)) + " %"
        print "F-score: " + str(round(fscore*100, 2)) + " %"
        
    if train:
        all_features = read_arff(file)
        bin_features = binarize(all_features)
               

        for i in range(iterations):
            random.shuffle(bin_features)
            for features, pclass in bin_features[:1318]:
                learn(features, pclass)
            average()
            
        save()
        print "Successfully trained perceptron and saved weights to file."
    
    
def usage():
    print "Usage: --dataset <arff-file> [--iterations <n>] [--bias <n>] [--interactive]"
    sys.exit(0)
    
def predict(instance):
    return score(instance) >= 0
    
def score(instance):
    global weights
    return sum(weights[feature] for feature in instance)

# def update(instance, label, x=1):
    # global weights
    # global bias
    # if label is False:
        # x *= -1
    # for feature in instance:
        # weights[feature] += x + bias     
        
def update(instance, label, x=1):
    global weights
    global bias
    global count
    count += 1
    #Increment or decrement weights
    if label is False:
        x *= -1
    for feature in instance:
        weights[feature] += x + bias
        cached_weights[feature] += (count - timestamps[feature]) * weights[feature] + bias
        timestamps[feature] = count
        
def learn(instance, label):
    prediction = predict(instance)
    if label != prediction:
        update(instance, label)
        
def average():
    global weights
    global cached_weights
    global count
    for feat, weight in weights.items():
        cached = cached_weights[feat]
        cached += (count - timestamps[feat]) * weight
        averaged = round(cached / float(count), 3)
        if averaged:
            weights[feat] = averaged
            
def read_arff(file):
    all_features = []
    with codecs.open(file, 'r', 'utf-8') as file:
        lines = file.readlines()
        for line in lines:
            if "@ATTRIBUTE" in line:
                continue
            #Crude way of making sure it's a data line
            if "{" in line:
                instancefeatures = line.replace('{', '')
                instancefeatures = instancefeatures.replace('}', '')
                instancefeatures = instancefeatures.split(",")
                instancefeature = [x.strip() for x in instancefeatures]
                all_features.append(instancefeatures)
    return all_features
    
def binarize(features):
    binarized = []
    for f in features:
        feature = [x.split() for x in f]
        pclass = bool(int(feature[0][1]))
        feature = [x[0] for x in feature]
        binarized.append([feature, pclass])
    return binarized
    
def save():
    global weights
    global cached_weights
    with codecs.open("model.sav", "wb") as file:
        pickle.dump(weights, file, -1)
        pickle.dump(cached_weights, file, -1)
        
def load():
    global weights
    global cached_weights
    with codecs.open("model.sav", "rb") as file:
        weights = pickle.load(file)
        cached_weights = pickle.load(file)
        
def extract_post_features(post, word_features, ngram_features):
    #Assume post consists of one string
    post_features = [0, 0, 0, 0, {}, {}]
    sent_tokenized = sent_tokenize(post)
    sent_word_tokenized = [word_tokenize(s) for s in sent_tokenized]
    if ngram_features:
        ngrams = len(ngram_features.keys()[0])
    for sentence in sent_word_tokenized:
        post_features[1] += 1
        ngramsentence = find_ngrams(sentence, ngrams)
        for ngram in ngramsentence:
            if ngram in ngram_features.keys():
                if ngram in post_features[5]:
                    post_features[5][ngram] += 1
                else:
                    post_features[5][ngram] = 1
        for token in sentence:
            post_features[2] += 1
            post_features[3] += len(token)
            if token in word_features.keys():
                if token in post_features[4]:
                    post_features[4][token] += 1
                else:
                    post_features[4][token] = 1
                    
    post_features[3] = float(post_features[2]) / post_features[1]
    post_features[2] = float(post_features[3]) / post_features[2]
    
    modified_list = [(0, 0), (1, post_features[1]), (2, post_features[2]), (3, post_features[3])]
    for word, number in word_features.iteritems():
        if word in post_features[4].keys():
            modified_list.append((number, post_features[4][word]))
    for ngram, number in ngram_features.iteritems():
        if ngram in post_features[5].keys():
            modified_list.append((number, post_features[5][ngram]))

    
    return [x[0] for x in modified_list]
    
                
        

    

def get_arff_features(file):
    #word itself as key and attr number as value
    word_features = {}
    #ngram tuple as key and attr number as value
    ngram_features = {}
    with codecs.open(file, 'r', 'utf-8') as file:
        lines = file.readlines()
        for line in lines:
            if "@ATTRIBUTE" in line:
                if "word" in line and "%" in line:
                    #Another ugly hack, everything after percentage is supposed to be the word
                    word = line[line.find("%")+1:].strip()
                    value = line.split()[1][4:].strip()
                    word_features[word] = value
                    continue
                if "ngram" in line and "%" in line:
                    ngram = tuple(line[line.find("%")+1:].strip().split())
                    value = line.split()[1][5:]
                    ngram_features[ngram] = value
        # for word, key in word_features.iteritems():
            # print word + " : " + key
        # for ngram, key in ngram_features.iteritems():
            # print ngram , " : " + key
    return word_features, ngram_features
       
        
if __name__ == "__main__":
    main()
        
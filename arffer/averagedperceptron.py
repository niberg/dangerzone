from collections import defaultdict
import getopt
import sys
import os
import codecs
import re
import random
import pickle

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

def main():
    global iterations
    global weights
    global bias
    
    try:
        options, remainder = getopt.getopt(sys.argv[1:], 't:n:b:', ['train=', 'iterations=', 'bias='])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        
    for opt, arg in options:
        if opt in ('-t', '--t'):
            file = arg
        elif opt in ('-n', '--iterations'):
            iterations = int(arg)
        elif opt in ('-b', '--bias'):
            bias = float(arg)
            
    all_features = read_arff(file)
    bin_features = binarize(all_features)
    
    true_positives = 0
    false_positives = 0
    true_negatives = 0
    false_negatives = 0
   
    #Trains on ~66 % and tests on the rest
    for i in range(iterations):
        random.shuffle(bin_features)
        for features, pclass in bin_features[:1318]:
            learn(features, pclass)
        average()
        
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
        
    print "Accuracy: " + str(float(true_positives)/(true_positives + false_positives)*100)
    print "Recall: " + str(float(true_positives)/(false_negatives + true_positives)*100)
    
    
def usage():
    print "Usage: --train <arff-file> [--iterations <n>] [--bias <n>]"
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
        weights = pickle.load(file, -1)
        cached_weights = pickle.load(file, -1)

    
if __name__ == "__main__":
    main()
        
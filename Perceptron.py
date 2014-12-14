import sys, os, codecs, re, random, pickle, operator, getopt
from collections import defaultdict
from DatasetCreator import find_ngrams
from nltk.tokenize import word_tokenize, sent_tokenize

#Implementation of a binary averaged perceptron
def main():   
    bias = 0
    iterations = 4
    dataset = "dataset.arff"
    savefile = "model.sav"   
    train = False
    test = False
    entire = False
    testfolder = None

    try:
        options, remainder = getopt.getopt(sys.argv[1:], 'rts:b:d:i:ef:', ["train", "test", "save=", "bias=", "dataset=", "iterations=", "entire", "testfolder="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        sys.exit(2)

    for opt, arg in options:
        if opt in ('-r', '--train'):
            train = True
        elif opt in ('-t', '--test'):
            test = True
        elif opt in ('-s', '--savefile'):
            savefile = arg
        elif opt in ('-b', '--bias'):
            bias = float(arg)
        elif opt in ('-d', '--dataset'):
            dataset = arg
        elif opt in ('-i', '--iterations'):
            iterations = int(arg)
        elif opt in ('-e', '--entire'):
            train = True
            entire = True
        elif opt in ('-f', '--testfolder'):
            test = True
            testfolder = arg

    perceptron = Perceptron(iterations=iterations, bias=bias, dataset=dataset, savefile=savefile) 
    if not train and not test:
        print "Training and testing using default 66/33 % split on arff"
        perceptron.train_on_arff()
        perceptron.test_on_arff()
        
    elif train:
        perceptron.train_on_arff(entire=entire)
    elif testfolder:
        perceptron.test_on_folder(testfolder=testfolder, truelabel="suicidewatch")
    elif test:
        perceptron.test_on_arff()



class Perceptron:


    def __init__(self, iterations=4, bias=0, dataset="dataset.arff", savefile="model.sav"):
        self.iterations = iterations
        self.bias = bias
        self.count = 0
        self.weights = defaultdict(int)
        self.cached_weights = defaultdict(int)
        self.timestamps = defaultdict(int)
        self.word_features, self.ngram_features = self.get_arff_features(dataset)
        self.savefile = savefile
        self.dataset = dataset
        
    def predict(self, instance):
        return self.score(instance) >= 0
        
    def score(self, instance):
        return sum(self.weights[feature] for feature in instance)
                 
    def update(self, instance, label, x=1):
        self.count += 1
        #Increment or decrement weights
        if label is False:
            x *= -1
        for feature in instance:
            self.weights[feature] += x + self.bias
            self.cached_weights[feature] += (self.count - self.timestamps[feature]) * self.weights[feature] + self.bias
            self.timestamps[feature] = self.count
            
    def learn(self, instance, label):
        prediction = self.predict(instance)
        if label != prediction:
            self.update(instance, label)
            
    def average(self):
        for feat, weight in self.weights.items():
            cached = self.cached_weights[feat]
            cached += (self.count - self.timestamps[feat]) * weight
            averaged = round(cached / float(self.count), 3)
            if averaged:
                self.weights[feat] = averaged
                
    def read_arff(self, file=None):
        if file == None:
            file == self.dataset
        all_features = []
        with codecs.open(file, 'r', 'utf-8') as file:
            lines = file.readlines()
            for line in lines:
                if "@ATTRIBUTE" in line:
                    continue
                #Crude way of making sure it's a data line
                if "{" in line:
                    instancefeatures = line[line.find('{'):]
                    instancefeatures = instancefeatures.replace('{', '')
                    instancefeatures = instancefeatures.replace('}', '')
                    instancefeatures = instancefeatures.split(",")
                    instancefeature = [x.strip() for x in instancefeatures]
                    all_features.append(instancefeatures)
        return all_features
        
    def binarize(self, features):
        binarized = []
        for f in features:
            feature = [x.split() for x in f]
            pclass = bool(int(feature[0][1]))
            feature = [x[0] for x in feature]
            binarized.append([feature, pclass])
        return binarized
        
    def save(self, file=None, silent=False):
        if file == None:
            filename = self.savefile
        with codecs.open(filename, "wb") as file:
            pickle.dump(self.weights, file, -1)
            pickle.dump(self.cached_weights, file, -1)
            pickle.dump(self.timestamps, file, -1)
            pickle.dump(self.iterations, file, -1)
            pickle.dump(self.bias, file, -1)
            pickle.dump(self.dataset, file, -1)
        if not silent:
            print "Saved model in", filename, "\n"
            
            
    def load(self, file=None):
        if file == None:
            filename = self.savefile    
        with codecs.open(filename, "rb") as file:
            self.weights = pickle.load(file)
            self.cached_weights = pickle.load(file)
            self.timestamps = pickle.load(file)
            self.iterations = pickle.load(file)
            self.bias = pickle.load(file)
            self.dataset = pickle.load(file)
        print "Loaded model from", filename, "\n"
            
    def extract_post_features(self, post):
        #Assume post consists of one string
        post_features = [0, {}, {}]
        sent_tokenized = sent_tokenize(post)
        sent_word_tokenized = [word_tokenize(s) for s in sent_tokenized]
        if self.ngram_features:
            ngrams = len(self.ngram_features.keys()[0])
        for sentence in sent_word_tokenized:
            if self.ngram_features:
                ngramsentence = find_ngrams(sentence, ngrams)
                for ngram in ngramsentence:
                    if ngram in self.ngram_features.keys():
                        if ngram in post_features[2]:
                            post_features[2][ngram] += 1
                        else:
                            post_features[2][ngram] = 1
            for token in sentence:
                if token in self.word_features.keys():
                    if token in post_features[1]:
                        post_features[1][token] += 1
                    else:
                        post_features[1][token] = 1
        modified_list = [(0, 0)]
        for word, number in self.word_features.iteritems():
            if word in post_features[1].keys():
                modified_list.append((number, post_features[1][word]))
        for ngram, number in self.ngram_features.iteritems():
            if ngram in post_features[2].keys():
                modified_list.append((number, post_features[2][ngram]))

       # print modified_list
        return [x[0] for x in modified_list]
        
    def get_test_posts(self, dir):
        posts = []
        for file in os.listdir(dir):
            filename = os.path.join(dir, file)
            f = codecs.open(filename, 'r', 'utf-8')
            post = f.read()
            posts.append((post, file))
        return posts        

    def get_arff_features(self, file):
        #word itself as key and attr number as value
        word_features = {}
        #ngram tuple as key and attr number as value
        ngram_features = {}
        ngram_tuple_list = []
        ngram_value_list = []
        with codecs.open(file, 'r', 'utf-8') as file:
            lines = file.readlines()
            for line in lines:
                if "@ATTRIBUTE" in line:
                    if "word" in line and "%" in line:
                        #Another ugly hack, everything after percentage is supposed to be the word
                        word = line[line.find("%")+1:].strip()
                        value = line.split()[1][4:].strip()
                        value = unicode(int(value) + 1)
                        word_features[word] = value
                        continue
                    if "ngram" in line and "%" in line:
                        ngram = tuple(line[line.find("%")+1:].strip().split())
                        ngram_tuple_list.append(ngram)
                        value = line.split()[1][5:]
                        ngram_value_list.append(value)
        #In order to get the same features indices as the ones in the arff
        #we need to add 1 to word values (done above) and add [number of word features] + 1 to ngram_features          
        ngram_value_list = [unicode(int(x) + 1 + len(word_features)) for x in ngram_value_list]
        ngram_features = dict(zip(ngram_tuple_list, ngram_value_list))
        return word_features, ngram_features
           
    def test_on_arff(self, file="dataset.arff", limit=0): # Changed from 1319 -Nils
        """To do testing on entire dataset, to find training errors, set limit to 0."""
        all_features = self.read_arff(file)
        bin_features = self.binarize(all_features)
        #Load if weights are empty
        if not self.weights:
            self.load()
        true_positives = 0
        false_positives = 0
        true_negatives = 0
        false_negatives = 0
        if limit > len(bin_features):
            limit = len(bin_features) -1
                
        for features, pclass in bin_features[limit:]:
            prediction = self.predict(features)
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
        
        print "Precision: " + str(precision*100) + " %"
        print "Recall: " + str(recall*100) + " %"
        print "F-score: " + str(fscore*100) + " %"
        
    def train_on_arff(self, file="dataset.arff", limit=1998, entire=False): # Changed from 1318 -Nils
        """To do training on the entire dataset, set limit to 1998 (if used with source_data folder)."""
        all_features = self.read_arff(file)
        bin_features = self.binarize(all_features)
        if limit > len(bin_features):
            limit = len(bin_features) - 1
        if not entire:
            bin_features = bin_features
        
        for i in range(self.iterations):
            random.shuffle(bin_features)
            for features, pclass in bin_features:
                self.learn(features, pclass)
            self.average()
            
        self.save()
        

        
    def test_on_folder(self, testfolder="testfolder", file="dataset.arff", verbose=True, truelabel="sw"):
        true_positives = 0
        false_positives = 0
        true_negatives = 0
        false_negatives = 0
        simple_true_positives = 0
        simple_false_positives = 0
        simple_true_negatives = 0
        simple_false_negatives = 0
        self.load()
        posts = self.get_test_posts(testfolder)
        for post in posts:
            features = self.extract_post_features(post[0])
            prediction = self.predict(features)
            if truelabel in post[1]:
                trueclass = True
            else:
                trueclass = False
            simpleprediction = False
            if "kill myself" in post[0] or "suicide" in post[0] or "killing myself" in post[0] or "hate myself" in post[0] or "no friends" in post[0] or "to die" in post[0] or "a burden" in post[0]:
                simpleprediction = True
            if prediction == trueclass:
                if trueclass == True:
                    true_positives += 1
                else:
                    true_negatives += 1
            else:
                if trueclass == False:
                    false_positives += 1
                else:
                    false_negatives += 1
            if trueclass == simpleprediction:
                if trueclass == True:
                    simple_true_positives += 1
                else:
                    simple_true_negatives += 1
            else:
                if trueclass == False:
                    simple_false_positives += 1
                else:
                    simple_false_negatives += 1
            if verbose:
                print post[1] + " Prediction: " + str(prediction) + " Simple prediction: " + str(simpleprediction)
            # if verbose:
                # print "With features: \n"
                # for word, value in word_features.iteritems():
                    # print value
                    # if value in features:
                        # sys.stdout.write(word + ", ")
                # if ngrams:
                    # for ngram, value in ngram_features.iteritems():
                        # if value in features:
                            # sys.stdout.write(", (")
                            # for x in ngram:
                                # sys.stdout.write(x + ", ")
                            # sys.stdout.write(")", )
                        
                # print "\n\n"
                
        precision = float(true_positives)/(true_positives + false_positives)
        recall = float(true_positives)/(false_negatives + true_positives)
        fscore = 2 * ((precision * recall)/(precision + recall))
        simple_precision = float(simple_true_positives)/(simple_true_positives + simple_false_positives)
        simple_recall = float(simple_true_positives)/(simple_false_negatives + simple_true_positives)
        simple_fscore = 2 * ((simple_precision * simple_recall)/(simple_precision + simple_recall))        
        
        print "\n\n"
        print "True positives: " + str(true_positives)
        print "True negatives: " + str(true_negatives)
        print "False positives: " + str(false_positives)
        print "False negatives: " + str(false_negatives)      
        print "Precision: " + str(precision*100) + " %"
        print "Recall: " + str(recall*100) + " %"
        print "F-score: " + str(fscore*100) + " %"    
        print "\n\n"
        print "Simple true positives: " + str(simple_true_positives)
        print "Simple true negatives: " + str(simple_true_negatives)
        print "Simple false positives: " + str(simple_false_positives)
        print "Simple false negatives: " + str(simple_false_negatives)      
        print "Simple precision: " + str(simple_precision*100) + " %"
        print "Simple recall: " + str(simple_recall*100) + " %"
        print "Simple f-score: " + str(simple_fscore*100) + " %"    
            

if __name__ == "__main__":    
    main()            

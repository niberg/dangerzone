import sys
import os
import codecs
import operator
import math
import getopt
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords as stp
from collections import defaultdict
import random

top_n = 500
threshold = 20
diffmeasure = "advanced"
dataset = "dataset"
alpha = 100
ngrams = 0
top_n_ngrams = 100
words = False
stopwords = False
customfeatures = False


def main():
    global top_n
    global threshold
    global diffmeasure
    global dataset
    global alpha
    global ngrams
    global top_n_ngrams
    global words
    global stopwords
    global customfeatures

    try:
        options, remainder = getopt.getopt(sys.argv[1:], 'n:t:i:d:ha:gx:wsc', ['top_n=', 'threshold=', 'input=', 'diffmeasure=', 'help', 'alpha=', 'ngrams=', 'top_n_ngrams=', 'words', 'stopwords', 'customfeatures'])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    for opt, arg in options:
        if opt in ('-n', '--top_n'):
            top_n = int(arg)
        elif opt in ('-t', '--threshold'):
            threshold = int(arg)
        elif opt in ('-i', '--input'):
            dataset = arg
        elif opt in ('-d', '--diffmeasure'):
            diffmeasure = arg
        elif opt in ('-h', '--help'):
            usage()
        elif opt in ('-a', '--alpha'):
            alpha = int(arg)
        elif opt in ('-g', '--ngrams'):
            ngrams = int(arg)
        elif opt in ('-x', '--top_n_ngrams'):
            top_n_ngrams = int(arg)
        elif opt in ('-w', '--words'):
            words = True
        elif opt in ('-s', '--stopwords'):
            stopwords = True
        elif opt in ('-c', '--customfeatures'):
            customfeatures = True
        
  
    if ngrams == 0 and words == False:
        print "You need to specify either --ngrams <n> or --words or both."
        usage()
    posts = read_posts(dataset)
    if ngrams > 0:
        post_features, word_freqs, ngram_freqs = get_features(posts)
    else:
        post_features, word_freqs = get_features(posts)
    if customfeatures:
        top_words = get_top_words(word_freqs, False, get_custom_features())
    else:
        top_words = get_top_words(word_freqs, False)
    if ngrams > 0:
        top_ngrams = get_top_words(ngram_freqs, True)
    if ngrams > 0:
        write_arff(post_features, top_words, top_ngrams)
    else:
        write_arff(post_features, top_words)
    
def read_posts(dir):
    posts = []
    
    for filename in os.listdir(dir):
        pclass = 0
        if filename.startswith("sw"):
            pclass = 1
            
        filename = os.path.join(dir, filename)
        with codecs.open(filename, 'r', 'utf-8') as post:
            posts.append([post.read(), pclass])
    return posts
    
def get_features(posts):
    #We need to loop through all posts and count wordfreqs
    #in order to calculate top 100 words or whatever we choose to use
    
    #List containing the features for each post
    all_post_features = []
    #Global word frequencies
    word_freqs = {}
    if ngrams > 0:
        ngram_freqs = {}
    
    
    for post in posts:
        #Every post needs to keep track of this information
        #Class, sentence count, word count, total token length, words in sentence
        #Add dictionary of ngrams if needed
        if ngrams > 0:
            post_features = [0, 0, 0, 0, {}, {}]
        else:
            post_features = [0, 0, 0, 0, {}]
        sent_tokenized = sent_tokenize(post[0])
        sent_word_tokenized = [word_tokenize(s) for s in sent_tokenized]
        #Get if sw or rant
        post_features[0] = post[1]
        
        
        for sentence in sent_word_tokenized:
            if ngrams > 0:
                ngramsentence = find_ngrams(sentence, ngrams)
                for ngram in ngramsentence:
                    if ngram not in ngram_freqs:
                        if post[1] == 0:
                            ngram_freqs[ngram] = [1, 0, 1]
                        #Token belongs to sw
                        else:
                            ngram_freqs[ngram] = [0, 1, 1]
                    else:
                        #Add ngrams to global freq list
                        ngram_freqs[ngram][post[1]] += 1
                        #Keep count of how many emails an ngram is in
                        if ngram not in post_features[5]:
                            ngram_freqs[ngram][2] += 1
                    if ngram not in post_features[5]:
                        post_features[5][ngram] = 1
                    else:
                        post_features[5][ngram] += 1
                        
            #Increase sentence count for post
            post_features[1] += 1
            for token in sentence:
                #Increase word count for post
                post_features[2] += 1
                #Increase total token length for post
                post_features[3] += len(token)
                if words:
                    #Add word to global list
                    if token not in word_freqs:
                        #Token belongs to rant
                        if post[1] == 0:
                            word_freqs[token] = [1, 0, 1]
                        #Token belongs to sw
                        else:
                            word_freqs[token] = [0, 1, 1]
                    #If the token already exits in wordlist
                    #we can just increment using class variable
                    else:
                            word_freqs[token][post[1]] += 1
                            # Word exists in wordfreqs but hasn't been added for this post
                            if token not in post_features[4]:
                                word_freqs[token][2] += 1
                    #Add word to posts list of words
                    if token not in post_features[4]:
                        post_features[4][token] = 1
                    else:
                        post_features[4][token] += 1

                    
        #Add the post's features to global list
        all_post_features.append(post_features)
    if ngrams > 0:
        return all_post_features, word_freqs, ngram_freqs
    return all_post_features, word_freqs
    

def write_arff(post_features, top_words, top_ngrams=None):
    
    #We need to write all the attributes before we write the actual data
    f = codecs.open('dataset.arff', 'w', 'utf-8')
    #Static write
    f.write('@RELATION suicidal\n\n@ATTRIBUTE class {1, 0}\n@ATTRIBUTE sentence_count NUMERIC\n@ATTRIBUTE average_word_length NUMERIC\n@ATTRIBUTE average_sentence_length NUMERIC\n')
    #Write attributes for all the top words

    for word in top_words:
        f.write('@ATTRIBUTE ' + 'word' + str(top_words.index(word)) + ' NUMERIC     %' + word + '\n')
    
    #Write ngram attributes
    if ngrams > 0:
        for ngram in top_ngrams:
            f.write('@ATTRIBUTE ' + 'ngram' + str(top_ngrams.index(ngram)) + ' NUMERIC     %')
            for x in ngram:
                f.write(x + ' ')
            f.write('\n')
    

    f.write('\n@DATA\n')
    
    #Now we write the data
    #Use sparse data format
    random.shuffle(post_features)
    for x in post_features:
        average_word_length = float(x[3]) / x[2]
        average_sentence_length = float(x[2]) / x[1]
        #Static write
        f.write('{0 ' + str(x[0]) + ', 1 ' + str(x[1]) + ', 2 ' + str(average_word_length) + ', 3 ' + str(average_sentence_length))
        #Iterate through words in post, see if any are in top words, if so write word and frequency
        #Need to keep track of which attribute word belongs to
        for top_word in top_words:
            for post_word, freq in x[4].iteritems():
                if post_word == top_word:
                   #There are 4 attributes before the words (with zero-based index) so first word is 4
                    f.write(', ' + str(top_words.index(post_word)+4) + ' ' + str(freq))
                    
        if ngrams > 0:
            for top_ngram in top_ngrams:
                for post_ngram, freq in x[5].iteritems():
                    if post_ngram == top_ngram:
                       #There are top_n + 4 attributes before the words (with zero-based index)
                       #If there are no words to write, we don't want to add the top_n variable
                        if top_words:
                            f.write(', ' + str(top_ngrams.index(post_ngram)+4+top_n) + ' ' + str(freq))
                        else:
                            f.write(', ' + str(top_ngrams.index(post_ngram)+4) + ' ' + str(freq))
        #Close curly braces and newline
        f.write('}\n')
            
    f.close()
        
        
def get_top_words(word_freqs, ngram, customwords=[]):
    global stopwords
    global customfeatures
    global top_n
    differences = {}
    if stopwords:
        #Gets stopwords from nltk
        stop = stp.words('english')
    
    #Iterate through word frequencies
    if diffmeasure == "relative":
        for word, freqs in word_freqs.iteritems(): 
            if freqs[2] >= threshold:
                sw = freqs[1]
                rant = freqs[0]
                #There's probably a more elegant way to prevent divide by zero errors
                if sw == 0:
                    sw = 0.001
                if rant == 0:
                    rant = 0.001
                #Get the relative difference between frequency for rant and frequency for sw
                diff = (sw - rant)/float(sw)
                if customfeatures and word in customwords or ngram:
                    differences[word] = diff
                elif not customfeatures:
                    differences[word] = diff
    elif diffmeasure == "absolute":
        for word, freqs in word_freqs.iteritems(): 
            if freqs[2] >= threshold:
                sw = freqs[1]
                rant = freqs[0]
                #Get the absolute difference between frequency for rant and frequency for sw
                diff = abs(sw - rant)
                if customfeatures and word in customwords or ngram:
                    differences[word] = diff
                elif not customfeatures:
                    differences[word] = diff
    else:
        for word, freqs in word_freqs.iteritems(): 
            if freqs[2] >= threshold:
                sw = freqs[1]
                rant = freqs[0]
                #There's probably a more elegant way to prevent divide by zero errors
                if sw == 0:
                    sw = 0.001
                if rant == 0:
                    rant = 0.001
                #Get the adjusted relative difference between frequency for rant and frequency for sw
                #I found this on the INTERNET!
                diff = 100 * ((sw - rant)/float(sw)) * (1 - math.exp(-(sw - rant)/alpha))
                if customfeatures and word in customwords or ngram:
                    differences[word] = diff
                elif not customfeatures:
                    differences[word] = diff
                
     
    
    #Sort in descending order    
    sorted_differences = sorted(differences.items(), key=operator.itemgetter(1), reverse=True)
    #Get top x words
    top_words = [x[0] for x in sorted_differences]
    #It's an ngram list if it's a tuple
    if stopwords and type(top_words[0]) is not tuple:
        #Rebuild list without stopwords
        top_words = [x for x in top_words if x not in stop]
    elif stopwords and type(top_words[0]) is tuple:
        ##Create temp holding list
        temp = []
        ##Iterate through tuples
        for x in top_words:
            stoptuple = False
            counter = 0
            for z in x:
                if z in stop:
                    counter += 1
            #If the entire tuple is composed of stopwords, we don't want it
            if counter == len(top_words[0]):
                stoptuple = True
            #add all other tuples to the list
            if not stoptuple:
                temp.append(x)
        #Replace top_words with filtered list
        top_words = temp
    if customfeatures and len(customwords) < top_n:
        top_n = len(customwords)
    if ngram:
        top_words = top_words[:top_n_ngrams]
    else:
        top_words = top_words[:top_n]
    
    return top_words
    
def get_custom_features():
    featureslist = []
    with codecs.open('customfeatures.txt', 'r', 'utf-8') as f:
        featureslist = f.readlines()
        featureslist = [x.strip() for x in featureslist]
    return featureslist
        
    
#Not really needed
def get_dataset_features(posts):
    features = [[0, 0], [0, 0], [0, 0], [0, 0], {}]
            # features[0][0] = number_rant_posts
            # features[0][1] = number_sw_posts
            # features[1][0] = rant_number_sentences
            # features[1][1] = sw_number_sentences
            # features[2][0] = rant_total_sentence_lengths
            # features[2][1] = sw_total_sentence_lengths
            # features[3][0] = rant_total_number_tokens
            # features[3][1] = sw_total_number_tokens
            # features[4][0] = rant_total_token_lengths
            # features[4][1] = sw_total_token_lengths
            # features[5] = word_freqs


    for post in posts:
        localsentences = sent_tokenize(post[0])
        sentences = [word_tokenize(s) for s in localsentences]
        #Get if sw or rant
        pclass = post[1]
        #Number of posts
        features[0][pclass] += 1

        for sentence in sentences:
            #Number of sentences
            features[1][pclass] += 1
            for token in sentence:
                    #Total sentence lengths
                    features[2][pclass] += 1
                    #Total number of tokens
                    features[3][pclass] += 1
                    #Total token lengths
                    features[4][pclass] += len(token)
    
                    if token not in features[5]:
                    #Token belongs to rant
                        if pclass == 0:
                            features[5][token] = [1, 0]
                        #Token belongs to sw
                        else:
                            features[5][token] = [0, 1]
                #If the token already exits in wordlist
                #we can just increment using class variable
                    else:
                        features[5][token][pclass] += 1
    return features
    
def usage():
    print "Usage: python main.py [--input <dir>] [--top_n <n>] [--treshold <n>]"
    print "[--diffmeasure <relative|absolute|advanced>] [--alpha <n>] (affects advanced diffmeasure only) [--ngrams <n>] [--top_n_ngrams <n>] [--words]"
    sys.exit(0)
    
def find_ngrams(input_list, n):
    return zip(*[input_list[i:] for i in range(n)])
    
    

    

    

if __name__ == "__main__":
    main()

import sys
import os
import codecs
import operator
import math
import getopt
from nltk.tokenize import word_tokenize, sent_tokenize

top_n = 500
threshold = 20
diffmeasure = "advanced"
dataset = "dataset"
alpha = 100




def main():
    global top_n
    global threshold
    global diffmeasure
    global dataset
    global alpha

    try:
        options, remainder = getopt.getopt(sys.argv[1:], 'n:t:i:d:ha:', ['top_n=', 'threshold=', 'input=', 'diffmeasure=', 'help', 'alpha='])
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
  
    posts = read_posts(dataset)
    post_features, word_freqs = get_features(posts)
    top_words = get_top_words(word_freqs)
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
    
    for post in posts:
        #Every post needs to keep track of this information
        #Class, sentence count, word count, total token length, words in sentence 
        post_features = [0, 0, 0, 0, {}]
        sent_tokenized = sent_tokenize(post[0])
        sent_word_tokenized = [word_tokenize(s) for s in sent_tokenized]
        #Get if sw or rant
        post_features[0] = post[1]
        
        
        for sentence in sent_word_tokenized:
            #Increase sentence count for post
            post_features[1] += 1
            for token in sentence:
                #Increase word count for post
                post_features[2] += 1
                #Increase total token length for post
                post_features[3] += len(token)
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
        
    return all_post_features, word_freqs
    

def write_arff(post_features, top_words):
    #We need to write all the attributes before we write the actual data
    f = codecs.open('dataset.arff', 'w', 'utf-8')
    #Static write
    f.write('@RELATION suicidal\n\n@ATTRIBUTE class {1, 0}\n@ATTRIBUTE sentence_count NUMERIC\n@ATTRIBUTE average_word_length NUMERIC\n@ATTRIBUTE average_sentence_length NUMERIC\n')
    #Write attributes for all the top words

    for word in top_words:
        f.write('@ATTRIBUTE ' + 'word' + str(top_words.index(word)) + ' NUMERIC     %' + word + '\n')

    f.write('\n@DATA\n')
    
    #Now we write the data
    #Use sparse data format
 
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
        #Close curly braces and newline
        f.write('}\n')
            
    f.close()
        
        
def get_top_words(word_freqs):
    differences = {}
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
                differences[word] = diff
    elif diffmeasure == "absolute":
        for word, freqs in word_freqs.iteritems(): 
            if freqs[2] >= threshold:
                sw = freqs[1]
                rant = freqs[0]
                #Get the absolute difference between frequency for rant and frequency for sw
                diff = abs(sw - rant)
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
                differences[word] = diff
                
     
    
    #Sort in descending order    
    sorted_differences = sorted(differences.items(), key=operator.itemgetter(1), reverse=True)
    #Get top x words
    top_words = [x[0] for x in sorted_differences]
    top_words = top_words[:top_n]
    
    return top_words
    
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
    print "Usage: python main.py [--input <dir>] [--top_n <n>] [--treshold <n>] [--diffmeasure <relative|absolute|advanced>] [--alpha <n>] (affects advanced diffmeasure only)"
    sys.exit(0)
    

if __name__ == "__main__":
    main()

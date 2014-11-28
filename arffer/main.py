import sys
import os
import codecs
import operator
from nltk.tokenize import word_tokenize, sent_tokenize




def main():
    if len(sys.argv) < 3:
        print "Argument one need to be a directory and argument two an integer"
        sys.exit(0)
    global top_x
    top_x = int(sys.argv[2])
    posts = read_posts(sys.argv[1])
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
                #Add word to posts list of words
                if token not in post_features[4]:
                    post_features[4][token] = 1
                else:
                    post_features[4][token] += 1
                #Add word to global list
                if token not in word_freqs:
                    #Token belongs to rant
                    if post[1] == 0:
                        word_freqs[token] = [1, 0]
                    #Token belongs to sw
                    else:
                        word_freqs[token] = [0, 1]
                #If the token already exits in wordlist
                #we can just increment using class variable
                else:
                        word_freqs[token][post[1]] += 1
                    
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
    for word, freqs in word_freqs.iteritems():
        #Get the absolute difference between frequency for rant and frequency for sw
        #Abs prevents negative numbers
        diff = abs(freqs[0] - freqs[1])
        differences[word] = diff
    #Sort in descending order    
    sorted_differences = sorted(differences.items(), key=operator.itemgetter(1), reverse=True)
    #Get top x words
    top_words = [x[0] for x in sorted_differences]
    top_words = top_words[:top_x]
    
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
        
main()

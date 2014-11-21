import sys
import os
import codecs
#~ from nltk.tokenize.stanford import StanfordTokenizer
from nltk.tokenize import wordpunct_tokenize, sent_tokenize
from decimal import *
#java_path = "/home/stp13/niberg/jdk1.8.0_25/bin/java"
#os.environ['JAVAHOME'] = java_path

#threshold = sys.argv[1]
sw = []
rant = []
# sw_tok = []
# rant_tok = []
n_sw = 0
n_rant = 0
markers = dict()
word_freqs = {}
rant_number_sentences = 0
sw_number_sentences = 0
rant_total_sentence_lengths = 0
sw_total_sentence_lengths = 0
rant_number_tokens = 0
sw_number_tokens = 0
rant_total_token_lengths = 0
sw_total_token_lengths = 0

# Set decimal precision
getcontext().prec = 10

# Read SW posts
for fn in os.listdir('suicidewatch'):
	n_sw += 1
	fn = os.path.join('suicidewatch', fn)
	with codecs.open(fn, 'r', 'utf-8') as f:
		sw.append(f.read())

# Read rant posts
for fn in os.listdir('rant'):
	n_rant += 1
	fn = os.path.join('rant', fn)
	with codecs.open(fn, 'r', 'utf-8') as f:
		rant.append(f.read())

# Create list of unique words
# (Uses very simple tokenization)
for post in rant:
	localsentences = sent_tokenize(post)
	rant_number_sentences += len(localsentences)
	rant_total_sentence_lengths += sum(len(sentence) for sentence in localsentences)
	localwords = [wordpunct_tokenize(s) for s in localsentences]
	#Flatten list
	localwords = [t for s in localwords for t in s]
	#Unused
	#rant_tok.append(localwords)
	for token in localwords:
		rant_number_tokens += 1
		rant_total_token_lengths += len(token)
		if token not in word_freqs:
			word_freqs[token] = [1, 0]
		else:
			word_freqs[token][0] += 1

for post in sw:
	localsentences = sent_tokenize(post)
	sw_number_sentences += len(localsentences)
	sw_total_sentence_lengths += sum(len(sentence) for sentence in localsentences)
	localwords = [wordpunct_tokenize(s) for s in localsentences]
	#Flatten list
	localwords = [t for s in localwords for t in s]
	#Unused
	#sw_tok.append(localwords)
	for token in localwords:
		sw_number_tokens += 1
		sw_total_token_lengths += len(token)
		if token not in word_freqs:
			word_freqs[token] = [0, 1]
		else:
			word_freqs[token][1] += 1

# Calculate occurrence probability
for word in word_freqs:
	rant_prob = float(word_freqs[word][0]) / n_rant
	sw_prob = float(word_freqs[word][1]) / n_sw
	pdiff = float(sw_prob) - rant_prob
	#if pdiff > float(threshold):
	markers[word] = pdiff
	
# Write lexicon
f = codecs.open('freqs.txt', 'w', 'utf-8')
for word in word_freqs:
	f.write(word + ' ' + str(word_freqs[word][0]) + ' ' + str(word_freqs[word][1]))
	f.write('\n')
f.close()
#Write lengths
f = codecs.open('lengths.txt', 'w', 'utf-8')
f.write('Average sentence length for rant: ' + str(float(rant_total_sentence_lengths) / rant_number_sentences) + '\n')
f.write('Average sentence length for suicidewatch: ' + str(float(sw_total_sentence_lengths) / sw_number_sentences) + '\n')
f.write('Average word length for suicidewatch: ' + str(float(sw_total_token_lengths) / sw_number_tokens) + '\n')
f.write('Average word length for rant: ' + str(float(rant_total_token_lengths) / rant_number_tokens) + '\n')
print sw_total_sentence_lengths
print sw_total_token_lengths

print rant_total_sentence_lengths
print rant_total_token_lengths

f.close()

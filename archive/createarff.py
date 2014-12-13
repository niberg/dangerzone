import sys
import os
import codecs
from nltk.tokenize import word_tokenize, sent_tokenize



# format = [is_sw, sentence_count, average_word_length, word_I, word_!]



f = codecs.open('dataset.arff', 'w', 'utf-8')
f.write('@RELATION suicidal\n@ATTRIBUTE class {1, 0}\n@ATTRIBUTE sentence_count NUMERIC\n@ATTRIBUTE average_word_length NUMERIC\n@ATTRIBUTE word_I  NUMERIC\n@ATTRIBUTE word_! NUMERIC\n@ATTRIBUTE average_sentence_length NUMERIC\n\n@DATA')
f.close()
	
for fn in os.listdir('dataset'):
	# Declare feature variables
	is_sw = 0
	sentence_count = 0
	average_word_length = 0
	average_sentence_length = 0
	word_I = 0
	word_excl = 0
	word_freqs = {}
	
	# Assign is_sw
	if fn.startswith('sw'):
		is_sw = 1
		
	# Read post
	fn = os.path.join('dataset', fn)
	f = codecs.open(fn, 'r', 'utf-8')
	post = f.read()
				
	# Collect feature values
	localsentences = sent_tokenize(post)
	sentences = [word_tokenize(s) for s in localsentences]

	total_sentence_lengths = 0
	total_number_tokens = 0
	total_token_lengths = 0

	for sentence in sentences:
		sentence_count += 1
		for token in sentence:
			total_number_tokens += 1
			total_token_lengths += len(token)
			if token not in word_freqs:
				word_freqs[token] = 1
			else:
				word_freqs[token] += 1
	
	# Assign feature values
	if 'I' in word_freqs:
		word_I = word_freqs['I']
	else:
		word_I = 0
	
	if '!' in word_freqs:
		word_excl = word_freqs['!']
	else:
		word_excl = 0
	
	average_word_length = total_token_lengths / float(total_number_tokens)
	average_sentence_length = float(total_number_tokens) / sentence_count
	f.close()
	
	# Weight features (maybe)
	
	f = codecs.open('dataset.arff', 'a', 'utf-8')
	f.write(str(is_sw) + ',' + str(sentence_count) + ',' + str(average_word_length) + ',' + str(word_I) + ',' + str(word_excl) + ',' + str(average_sentence_length))
	f.write('\n')
	f.close()

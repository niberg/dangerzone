import sys
import os
import codecs
from nltk.tokenize import word_tokenize, sent_tokenize

class main:
	
	def main:
		posts = read_posts(sys.argv[1])
		features = get_features(posts)
		write_arff(posts, features)
		
	def read_posts(dir):
		posts = []
		
		for filename in os.listdir(dir):
			class = 0
			if filename.startswith("sw"):
				class = 1
				
			filename = os.path.join(dir, filename)
			with codecs.open(filename, 'r', 'utf-8') as post:
				posts.append(post.read(), class)
		return posts
	
	def get_features(posts):
		features = []
		number_sw_posts = 0
		number_rant_posts = 0
		word_freqs = {}
		rant_number_sentences = 0
		rant_total_sentence_lengths = 0
		rant_total_number_tokens = 0
		rant_total_token_lengths = 0
		sw_number_sentences = 0
		sw_total_sentence_lengths = 0
		sw_total_number_tokens = 0
		sw_total_token_lengths = 0

		for post in posts:
			localsentences = sent_tokenize(post[0])
			sentences = [word_tokenize(s) for s in localsentences]
			if post[1] == 1:
				number_sw_posts += 1
			else:
				number_rant_posts += 1

			for sentence in sentences:
				if post[1] == 1:
					sw_number_sentences += 1
				else:
					rant_number_sentences += 1
				for token in sentence:
					if post[1] == 1:
						sw_total_sentence_lengths += 1
						sw_total_number_tokens += 1
						sw_total_token_lengths += len(token)
					else:
						rant_total_sentence_lengths += 1
						rant_total_number_tokens += 1
						rant_total_token_lengths += len(token)
					if token not in word_freqs:
						word_freqs[token] = [1, 0]
					else:
						word_freqs[token][0] += 1
		features[0] = 
				
		


	def write_arff(posts, features):
		for post in posts:
			_get_statistics(post)
			
	def _get_statistics(post):
		rant_number_sentences = 0
		rant_total_sentence_lengths = 0
		rant_total_number_tokens = 0
		rant_total_token_lengths = 0
		rant_avg_post_length = 0
		
		sw_number_sentences = 0
		sw_total_sentence_lengths = 0
		sw_total_number_tokens = 0
		sw_total_token_lengths = 0
		sw_avg_post_length = 0

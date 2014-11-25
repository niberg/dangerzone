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
	
	def get_dataset_features(posts):
		features = [[0, 0], [0, 0], [0, 0], [0, 0], {}]
		word_freqs = {}
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
                # features[5][0] = word_freqs


		for post in posts:
			localsentences = sent_tokenize(post[0])
			sentences = [word_tokenize(s) for s in localsentences]
			class = post[1]
			features[0][class] += 1

			for sentence in sentences:
				features[1][class] += 1
				for token in sentence:
                                        	features[2][class] += 1
						features[3][class] += 1
						features[4][class] += len(token)

					if token not in features[5]:
                                            if class == 0:
						features[5][token] = [1, 0]
					    else:
                                                features[5][token] = [0, 1]
                                        else:
						features[5][token][class] += 1
		return features


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

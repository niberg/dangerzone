import os
import sys
import codecs

global_words = dict()

path = sys.argv[1]
for fn in os.listdir(path):
	fn = os.path.join(path, fn)
	with open(fn) as f:
		local = set(f.read().replace('\n', '').split())
		for s in local:
			if s in global_words:
				global_words[s] += 1
			else: 
				global_words[s] = 1
	f.close()
	
topwords = []
for s in global_words:
	if global_words[s] >= 20:
		topwords.append(s)
topwords.sort()

f = codecs.open('20words.txt', 'w', 'utf-8')
for s in topwords:
	f.write(s + '\n')
f.close()

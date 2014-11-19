import sys

from practnlptools.tools import Annotator
annotator=Annotator()
message = sys.argv[1]

import nltk.data
import codecs

sbd = nltk.data.load('english.pickle')

with open(message) as f:
	lines = f.readlines()[2:]
	#f = codecs.open(str(count).zfill(4) + '.txt', 'w', 'utf-8')
	for line in lines:
		sentences = sbd.tokenize(line.strip())
		for sentence in sentences:
			#print annotator.getAnnotations(sentence,dep_parse=True)['dep_parse']
			print annotator.getAnnotations(sentence)['srl']
			#print(sentence)
	#f = codecs.open('test.txt', 'w', 'utf-8')
	#annotatedlist = annotator.getBatchAnnotations(list,dep_parse=True)['dep_parse']
	#annotator.getBatchAnnotations(list,dep_parse=True)['dep_parse']
	#for s in annotatedlist:
	#	f.write(s)
	#	f.write('\n')	
			#if not s:
		#	print("Yo")
		#else:
		#f.write(annotator.getAnnotations(,dep_parse=True)['dep_parse'])
		#for r in roles:
		#	f.write(r)
		#f.write('\n')
	#f.write('\n\n'.join(sbd.tokenize(message_string.strip())))
f.close()

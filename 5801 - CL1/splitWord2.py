# Read a text in and print every word (space-delimited) on a new line
# Keep track of the number of tokens, and of the number of words (types)

import sys

inputFile = open(sys.argv[1], 'r')
freqW = sys.argv[2]
nbWords = 0

dictW = {}

def stripPunc(word):
	puncList = [".",";",":","!","?","/","\\",",","#","@","$","&",")","(","\""]
	cleanWord = ""
	for char in word:
		if not char in puncList:
			cleanWord = cleanWord + char
	return cleanWord
	
words = inputFile.read().split()
    #ANALYSIS
    #doing the same thing as splitword.
    #picking each word and looping all the words.
    #complexity is order of n square. where n is the number of words
    #END ANALYSIS
for token in words:
	count = 0
	nbWords = nbWords + 1
	token = stripPunc(token)
	print(token)
	for word in words:
		if token == stripPunc(word):
			count = count + 1
	# add frequency of the token in the dictionary
	dictW[token] = count
	
		
print("Total number of tokens:", nbWords)
print("Total number of tokens:", sum(dictW.values()))
print("Total number of types:", len(dictW.keys()))

if freqW in dictW :
	print("Frequency of", freqW, "in", sys.argv[1], ":", dictW[freqW])
else:
	print("Frequency of the word", freqW, "in", sys.argv[1], ": 0")

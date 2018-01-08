# Read a text in and print every word (space-delimited) on a new line
# Keep track of the number of tokens, and of the number of words (types)
import sys
import math
#inputFile = open(sys.argv[1], 'r')
#freqW = sys.argv[2]
inputFile = open(r'C:\Sem1\5801\nyt_200811.txt', 'r')
nbWords = 0

dictW = {}

def stripPunc(word):
	puncList = [".",";",":","!","?","/","\\",",","#","@","$","&",")","(","\""]
	cleanWord = ""
	for char in word:
		if not char in puncList:
			cleanWord = cleanWord + char
	return cleanWord

def ProcessToken(token):
	puncList = [".",";","!","?","/","\\",",","#","@","$","&",")","(","\"",":","'","=","_"]
	wordList=[]
	word=''
	for i in range(len(token)):
		#remove punctuations
		if not token[i] in puncList:
			word = word + token[i]
		#handle can't
		if token[i] == "'":
			if word[:-1] and word[-1] == 'n' and i < len(token) - 1 and token[i+1] and token[i+1] == 't':
				if word == 'can':
					wordList.append(word)
				else:
					wordList.append(word[:-1])
				wordList.append('not')
				word=''
	if word:
		wordList.append(word)
	return wordList
		
#ANALYSIS
#this is order of n. number of chars in a word is small compared to number of words.where n is the number of words
#End ANALYSIS
for line in inputFile.readlines():
	line = line.split()
	for token in line:
		words = ProcessToken(token.lower())
		for word in words:
			if not word in dictW:
				dictW[word] = 1
			else:
				dictW[word] = dictW[word] + 1

a1_sorted_keys = sorted(dictW, key=dictW.get, reverse=True)
column1, column2 = [], []
for rank,key in enumerate(a1_sorted_keys,1):
    column1.append(math.log(rank))
    column2.append(math.log(dictW[key]))

import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.scatter(column1, column2)
print(column1[0])
print(column2[0])



for i, txt in enumerate(a1_sorted_keys,1):
   ax.annotate(txt, (column1[i-1],column2[i-1]))
plt.scatter(column1, column2)
plt.ylabel('Log(Frequency)')
plt.xlabel('Log(Rank)')

plt.show()

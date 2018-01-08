'''
LING 5801 - Fall 2017
This is a script to calculate overall entropy for the given piece of text 
'''

import math

puncList = [".",";","!","?","/","\\",",","#","@","$","&",")","(","\"",":","'","=","_",'-',"’"]
text = 'Like a leaf or a feather,In the windy, windy weather,We’ll whirl about, and twirl about And all sink down together.'
count=0
scoreDict = {}
for i in range(0, len(text)):
	if text[i] != ' ' and text[i] not in puncList:
		scoreDict[text[i].lower()]  = scoreDict.get(text[i].lower(),0)
		scoreDict[text[i].lower()] += 1
		count+=1

#relative frequencies
psum = 0
#appending category for each item based on the average scores
for key in scoreDict:
	scoreDict[key] = scoreDict[key]/count
	psum +=scoreDict[key] 


perLetterEntropy = 0
#appending entropy of each item
for key in scoreDict:
	entropy = -(float(scoreDict[key])*math.log((scoreDict[key]), 2))
	if entropy == -0.0:
		entropy = 0.0
	perLetterEntropy += entropy
	scoreDict[key] = (entropy)

#for final results
maxEntropy = 0.0
minEntropy = 5.0
for key in scoreDict:
	if scoreDict[key] < minEntropy:
		minEntropy = scoreDict[key]
	if scoreDict[key] > maxEntropy:
		maxEntropy = scoreDict[key]

print( '*********************** RESULTS *************************')
print('Entropy: ' + str(round(perLetterEntropy,3)) + ' bits per character')
print( 'Minimum Entropy\t\tMaximum Entropy')
print( str(round(minEntropy,3)) + '\t\t        ' + str(round(maxEntropy,3)))
print('----------------------------------------------------------')

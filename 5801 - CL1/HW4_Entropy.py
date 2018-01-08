'''
LING 5801 - Fall 2017
This is a script to calculate entropy based on the scores assigned by 
mechanical turks
This script takes 1 input - the answers csv file.
The answers csv is expected to have a header :
    key,worker_id,agreement
It will output the maximum and the minimum entropy along with the 
agreement/disagreement/neutral with max/min entropy
'''
import pandas as pd
import math
import sys

inputFileName = sys.argv[1]
df=pd.read_csv(inputFileName,sep=',')
scoreDict = {}
for i in range(0, len(df)):
	if df.loc[i]['key'] in scoreDict:
		scoreDict[df.loc[i]['key']].append(df.loc[i]['agreement'])
	else:
		scoreDict[df.loc[i]['key']] = [df.loc[i]['agreement']]	

#appending category for each item based on the average scores
for key in scoreDict:
	sum = 0
	totalNum = 0
	for val in scoreDict[key]:
		sum += val
		totalNum += 1
	average = float(sum/totalNum)
	if average>=1 and average <= 5:
		scoreDict[key].append('agreement')
	elif average < 1 and average >= -1:
		scoreDict[key].append('neutral')
	elif average >= -5 and average < -1:
		scoreDict[key].append('disagreement')

#calculation for per item agreement/disagreement/neutral scorees
#appending entropy of each item
for key in scoreDict:
	item_AgreementCount = 0
	item_DisagreementCount = 0
	item_NeutralCount = 0
	item_TotalNumOfScores = 0
    
	agreementEntropy = 0
	disagreementEntropy = 0
	neutralEntropy = 0
	for val in scoreDict[key][:-1]:
		if val>=1 and val<=5:
			item_AgreementCount += 1
		elif val<-1 and val>=-5:
			item_DisagreementCount += 1
		else:
			item_NeutralCount += 1
		item_TotalNumOfScores +=1

	if item_AgreementCount > 0:
		agreementEntropy = (float(item_AgreementCount/item_TotalNumOfScores)*math.log((item_AgreementCount/item_TotalNumOfScores), 2))
	if item_DisagreementCount > 0:
		disagreementEntropy = (float(item_DisagreementCount/item_TotalNumOfScores)*math.log((item_DisagreementCount/item_TotalNumOfScores), 2))
	if item_NeutralCount > 0:
		neutralEntropy = (float(item_NeutralCount/item_TotalNumOfScores)*math.log((item_NeutralCount/item_TotalNumOfScores), 2))
	entropy = -(agreementEntropy + disagreementEntropy + neutralEntropy)
	if entropy == -0.0:
		entropy = 0.0
	scoreDict[key].append(entropy)

#for final results
maxEntropy = 0.0
minEntropy = 0.0
for key in scoreDict:
	if scoreDict[key][-1] < minEntropy:
		minEntropy = scoreDict[key][-1]
	if scoreDict[key][-1] > maxEntropy:
		maxEntropy = scoreDict[key][-1]

print( '******************************** RESULTS *******************************')
print( 'Minimum Entropy\t\tMaximum Entropy')
print( str(round(minEntropy,3)) + '\t\t        ' + str(round(maxEntropy,3)))
print('-------------------------------------------------------------------------')

numItemsWithMinEntropy = 0
numItemsWithMaxEntropy = 0
agreement_MinEntropy = 0
disagreement_MinEntropy = 0
neutral_MinEntropy = 0
agreement_MaxEntropy = 0
disagreement_MaxEntropy = 0
neutral_MaxEntropy = 0

for key in scoreDict:
	if scoreDict[key][-1] == minEntropy:
		numItemsWithMinEntropy += 1
		if scoreDict[key][-2] == 'agreement':
			agreement_MinEntropy += 1
		elif scoreDict[key][-2] == 'neutral':
			neutral_MinEntropy += 1
		elif scoreDict[key][-2] == 'disagreement':
			disagreement_MinEntropy += 1
	elif scoreDict[key][-1] == maxEntropy:
		numItemsWithMaxEntropy += 1
		if scoreDict[key][-2] == 'agreement':
			agreement_MaxEntropy += 1
		elif scoreDict[key][-2] == 'neutral':
			neutral_MaxEntropy += 1
		elif scoreDict[key][-2] == 'disagreement':
			disagreement_MaxEntropy += 1

print( 'Number of items with Minimum Entropy = ' + str(numItemsWithMinEntropy))
print( 'Number of items with Maximum Entropy = ' + str(numItemsWithMaxEntropy))
print( '-------------------------------------------------------------------------')
print( 'Entropy\t| Agreement  |  Disagreement  |  Neutral  |')
print( 'Minimum\t|    ' + str(agreement_MinEntropy) + '\t     |     ' + str(disagreement_MinEntropy) + '\t      |    ' + str(neutral_MinEntropy) + '      |')
print( 'Maximum\t|     ' + str(agreement_MaxEntropy) + '      |\t    ' + str(disagreement_MaxEntropy) + '         |   ' + str(neutral_MaxEntropy) + '      |')
print( '--------------------------------------------------------------------------')
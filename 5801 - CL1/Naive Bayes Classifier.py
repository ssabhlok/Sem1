'''
LING 5801 - Fall 2017
This is a Naive Bayes Classifier
This script takes 2 inputs - the training csv and the test csv files.
The training and test csv are expected to have a header :
    key,agreement,quote,response
It will output the accuracy of the classifier along with the precision and recall
for each catergory.
Naming convention followed = positive implies agreement
                           = negative implies disagreement
'''
import pandas as pd
import sys

positive = {}
negative = {}
countPositive = 0
countNegative = 0
totalWordsInPositive = 0
totalWordsInNegative=0
totalCorpus = 0
positivePrior = 0.0
negativePrior = 0.0

def ProcessToken(token):
	puncList = [".",";","!","?","/","\\",",","#","@","$","&",")","(","\"",":","'","=","_",'-']
	wordList=[]
	stopWord = ['a','and','the','an']
	word=''
	for i in range(len(token)):
		#remove punctuations
		if not token[i] in puncList:
			word = word + token[i]
	if word and word not in stopWord:
		wordList.append(word)
	return wordList

#P(c|x)  = P(c)*P(x|c)
def Classify(wordList):
    #probability for positive
    pPositive=1.0
    pNegative = 1.0
    for word in wordList:
        pPositive *= (positive.get(word,0)+1)/(totalWordsInPositive+totalCorpus)
        pNegative *= (negative.get(word,0)+1)/(totalWordsInNegative+totalCorpus)
    pPositive = pPositive*positivePrior
    pNegative = pNegative*negativePrior
    if pPositive > pNegative:
        return 'positive'
    else:
        return 'negative'

trainFileName = sys.argv[1]
########################################## TRAINING ######################################
df=pd.read_csv(trainFileName,sep=',') #opening the desired csv file 
#read the training file in a pandas dataframe

for i in range(len(df)):
    count = 0
    agreement = df.loc[i]['agreement']
    for token in df.loc[i]['response'].split():
        words = ProcessToken(token.lower())
        for word in words:
                  if count > 3:
                      break
                  if len(word) >= 3:
                      if agreement <= 5.0 and agreement >=1:
                          countPositive+=1
                          positive[word] = positive.get(word,0) + 1
                      elif agreement < -1 and agreement >= -5:
                          countNegative+=1
                          negative[word] = negative.get(word,0) + 1
                  count+=1
for val in positive.values():
    totalWordsInPositive+=val
for val in negative.values():
    totalWordsInNegative+=val
corpus = set(positive.keys())
corpus.update(negative.keys())
totalCorpus = len(corpus) 
positivePrior = (countPositive)/(countPositive+countNegative)  
negativePrior = (countNegative)/(countPositive+countNegative)
                    
################################### EVLUATION #########################################
testFileName = sys.argv[2]           
test_df=pd.read_csv(testFileName,sep=',')
test_ActualPositiveClassifyPositive = 0
test_ActualPositiveClassifyNegative = 0
test_ActualNegativeClassifyNegative = 0
test_ActualNegativeClassifyPositive =0
test_ActualPositive = 0
test_ActualNegative =0
actualClass = ''
for i in range(len(test_df)):
    count = 0
    wordList = []
    agreement = test_df.loc[i]['agreement']
    if agreement <= 5.0 and agreement >=1:
        test_ActualPositive+=1
        actualClass = 'positive'
    elif agreement < -1 and agreement >= -5:
        test_ActualNegative+=1
        actualClass = 'negative'
    else:
        continue
    for token in test_df.loc[i]['response'].split():
        words = ProcessToken(token.lower())
        for word in words:
                  if count > 3:
                      break
                  if len(word) >= 3:
                      wordList.append(word)
                      count+=1
    result = Classify(wordList)
    if result == 'positive' and actualClass == 'positive':
        test_ActualPositiveClassifyPositive+=1
    elif result == 'positive' and actualClass == 'negative':
        test_ActualNegativeClassifyPositive+=1
    elif result == 'negative' and actualClass == 'negative':
        test_ActualNegativeClassifyNegative+=1
    elif result == 'negative' and actualClass == 'positive':
        test_ActualPositiveClassifyNegative+=1
   

print( '******************************* CONFUSION MATRIX **************************')
print( '|Predicted Class ->           \tAgree       Disagree                          ')
print( '|    Actual Class |  Agree    \t' + str(test_ActualPositiveClassifyPositive) + ' \t     ' + str(test_ActualPositiveClassifyNegative) + '      ')
print( '|                   Disagree     ' + str(test_ActualNegativeClassifyPositive) + ' \t    ' + str(test_ActualNegativeClassifyNegative) + '     ')
print( '***************************************************************************')
accuracy = round((float(test_ActualPositiveClassifyPositive+test_ActualNegativeClassifyNegative)/(test_ActualPositiveClassifyPositive + test_ActualNegativeClassifyNegative + test_ActualPositiveClassifyNegative + test_ActualNegativeClassifyPositive))*100,3)
print( 'Accuracy(percentage) is - ' + str(accuracy) + '%')
recallForAgreement = round((float(test_ActualPositiveClassifyPositive)/(test_ActualPositiveClassifyPositive + test_ActualPositiveClassifyNegative))*100,3)
print( 'Recall(percentage) for Agreement category - ' + str(recallForAgreement) + '%')
precisionForAgreement = round((float(test_ActualPositiveClassifyPositive)/(test_ActualPositiveClassifyPositive + test_ActualNegativeClassifyPositive))*100,3)
print( 'Precision(percentage) for Agreement category - ' + str(precisionForAgreement)+ '%')
                        
recallForDisagreement = round((float(test_ActualNegativeClassifyNegative)/(test_ActualNegativeClassifyNegative + test_ActualNegativeClassifyPositive))*100,3)
print( 'Recall(percentage) for Disagreement category - ' + str(recallForDisagreement)+ '%')
precisionForDisagreement = round((float(test_ActualNegativeClassifyNegative)/(test_ActualNegativeClassifyNegative + test_ActualPositiveClassifyNegative))*100,3)
print( 'Precision(percentage) for Disagreement category - ' + str(precisionForDisagreement)+ '%')                      
                        

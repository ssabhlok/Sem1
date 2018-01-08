import numpy as np
import csv
import math
import matplotlib.pyplot as plt
import sys

def ReadCSVFile(inputFile):
    with open(inputFile) as csvfile:
        next(csvfile)  # skip header row
        data = (csv.reader(csvfile, delimiter=',', quotechar='|'))
        column1, column2 = [], []
        for row in data:
            column1.append(row[0])
            column2.append(row[1])
    rank = np.array(column1)
    rank = rank.astype(int)
    rank = np.log(rank)
    freq = np.array(column2)
    freq = freq.astype(int)
    freq = np.log(freq)
    return (rank,freq)
a1_sorted_keys = []            
def ReadTextFile(fileName):
    dictW = {}
    inputFile = open(fileName, 'r')
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
    AnnotatedPlot(column1,column2,a1_sorted_keys)
    return (column1,column2)
    
    
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

def Plot(X,Y):
    fig, ax = plt.subplots()
    ax.scatter(X, Y)
    plt.ylabel('Log(Frequency)')
    plt.xlabel('Log(Rank)')
    plt.show()

def AnnotatedPlot(X,Y,sortedDict):
    fig, ax = plt.subplots()
    ax.scatter(X, Y)
    plt.ylabel('Log(Frequency)')
    plt.xlabel('Log(Rank)')
    plt.show()
    for i, txt in enumerate(sortedDict,1):
        ax.annotate(txt, (X[i-1],Y[i-1]))
        
def Main():
    fileName = sys.argv[1];
    #fileName = r'C:\Sem1\5801\nyt_200811.txt'
    idx = fileName.index('.')
    extension = fileName[idx+1:]
    if extension == "csv":
        logRank,logFreq = ReadCSVFile(fileName)
    elif extension == 'txt':
        logRank,logFreq = ReadTextFile(fileName)
    Plot(logRank,logFreq)
        
if __name__ == '__main__':
    Main()

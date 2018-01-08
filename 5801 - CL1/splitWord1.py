# Read a text in and print every word (space-delimited) on a new line
# Keep track of the number of tokens

import sys

inputFile = open(sys.argv[1], 'r')
nbWords = 0


for line in inputFile.readlines():
	line = line.split()
	for word in line:
		nbWords = nbWords + 1
		print(word)

print("Total number of tokens:", nbWords)





	
	

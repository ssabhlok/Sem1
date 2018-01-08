# Read in a text file that contains a tweet on each line
# Remove urls from tweets, and print every cleaned tweet on a newline
# The script takes one argument at the command line: the file that you want to process
# If you are in a directory where the code as well as the tweets_buckeyes.txt file is, you can run the code as follows:
# python cleanTweets tweets_buckeyes.txt


import re

#os.chdir(r"C:\Sem1\5801")
inputFile = open(r"C:\Sem1\5801\Code\TEST.txt", 'r')
outputFile = open(r"C:\Sem1\5801\Code\o_TEST.txt", 'a')
outputFile_2 = open(r"C:\Sem1\5801\Code\omitWord_TEST.txt", 'a')
#reading number of lines in the file
print(len(inputFile.readlines()))
inputFile.seek(0)
for line in inputFile.readlines():
    #donot print the line if it contais http
    if re.search(r"[H]t{2}ps?(?=:)",line,re.I) == None:
        outputFile.write(line)
    else:
        #replacing all URLs with space
        print(re.sub(r"(?i)[H]t{2}ps?(?=:\\)",'',line))
        line_up = re.sub(r"(?i)[H]t{2}ps?(?=:)",'',line)
        outputFile_2.write(line_up)
    line = line.split()
    
    # what does the variable "line" contain now?
    for word in line:
        #print(word)
        if re.search(r"[H]t{2}ps?(?=:)",word,re.I) == None:
            outputFile_2.write(word + " ")
    outputFile_2.write('\n')      
# add here your code for going through each element in "line" and check whether it starts with "http" (see https://www.tutorialspoint.com/python/string_startswith.htm for the startswith method)
outputFile.close()
outputFile_2.close()
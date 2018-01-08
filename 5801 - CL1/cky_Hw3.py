sentence = ['people','with','fish' ,'fish', 'fish', 'with','rods']
n = len(sentence)

# initialize the chart
#initialize the backtracking table too
chart = []
back = []
for i in range(0,n):
  row1 = []
  row2 = []
  for j in range(0,n):
    row1.append({})
    row2.append({})
  chart.append(row1)
  back.append(row2)

# build grammar
binaries = [
  [0.9, 'S', 'NP', 'VP'],
  [0.5, 'VP', 'V', 'NP'],
  [0.3, 'VP', 'V', '@VP_V'],
  [0.1, 'VP', 'V', 'PP'],
  [1.0, '@VP_V', 'NP', 'PP'],
  [0.1, 'NP', 'NP', 'NP'],
  [0.2, 'NP', 'NP', 'PP'],
  [1.0, 'PP', 'P', 'NP']
]
unaries = [
  [0.1, 'S', 'VP'],
  [0.7, 'NP', 'N'],
  [0.1, 'VP', 'V']
]

lexicon = [
  [0.5, 'N', 'people'],
  [0.2, 'N', 'fish'],
  [0.2, 'N', 'tanks'],
  [0.1, 'N', 'rods'],
  [0.1, 'V', 'people'],
  [0.6, 'V', 'fish'],
  [0.3, 'V', 'tanks'],
  [1.0, 'P', 'with']
]

def handleUnaries(i,j):
  modified = False
  for (p, A, B) in unaries:
    if chart[i][j].get(B,0)*p > chart[i][j].get(A, 0):
      chart[i][j][A] = chart[i][j].get(B)*p
      #
      # store information necessary to backtrack
      back[i][j][A] = (i,j,B)
      #
      modified = True
  if modified:
    handleUnaries(i,j)
      
# lexicon
for (i, word) in enumerate(sentence):
  for (p, preterm, term) in lexicon:
    if word == term:
      chart[i][i][preterm] = p
      #
      # store information necessary to backtrack - left and right coordinates for the key
      back[i][i][preterm] = (word,)
      #
  handleUnaries(i,i)

# process all sets of span words  
for span in range(2,n+1):
  # print ('span', span)
  for begin in range(0, n-span+1):
    # print ('begin', begin)
    end = begin + span
    for split in range(begin+1,end):
      # print('split', split)
      # check all binary rules A -> B C
      for (p, A, B, C) in binaries:
        if chart[begin][split-1].get(B) and chart[split][end-1].get(C):
          prob = chart[begin][split-1].get(B)*chart[split][end-1].get(C)*p
          if prob > chart[begin][end-1].get(A,0):
            chart[begin][end-1][A] = prob
            #
            # store information necessary to backtrack
            back[begin][end-1][A]= (begin,split-1,B,split,end-1,C)
            #
    handleUnaries(begin,end-1)  
visited = {}
def tree2string(i, j, nonterm):
  # return string representation of tree with root <nonterm> in chart[i][j]
  # with the following format:
  # (<nonterm> <left-subtree> <right-subtree>)
  #    or
  # (<nonterm> <left-subtree> )
  #    or
  # (<nonterm> <term>)
  print('(%s' %nonterm,end=' ')
  root = back[i][j][nonterm]
  #print(root)
  if len(root) == 6:
      if visited.get((root[0],root[1],root[2]),0) == 0:
          visited[(root[0],root[1],root[2])]=1
          tree2string(root[0],root[1],root[2])
          print(')',end='')
      if visited.get((root[3],root[4],root[5]),0) == 0:
          tree2string(root[3],root[4],root[5])
          visited[(root[3],root[4],root[5])]=1
          print(')',end='')
  elif len(root) ==3:
      elem = (back[i][j][nonterm])
      for a,b in back[i][j].items():
          if a == elem[2]:
              print('(',end='')
              print(a,end ='')
              print('(',end='')
              print(b[0],end='')
              print(')',end='')
              print(')',end='')
  elif len(root) == 1:
      print('(',end='')
      print(root[0],end='')
      print(')',end='')
  
    
#print(chart[0][n-1])

tree2string(0,n-1,'S')
print(')')

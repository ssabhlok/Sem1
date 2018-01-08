import sys

modelFile = sys.argv[1]
input = sys.argv[2]

S = set()
F = set()
M = {}

# build FSA based on model description in modelFile
for line in open(modelFile, 'r').readlines():
  line = line.split()
  type = line[0]
  if type is 'S':
    S.add(line[1])
  if type is 'F':
    F.add(line[1])
  if type is 'M':
    start = line[1]
    obs = line[2]
    end = line[3]
    if not start in M:
      M[start] = {}
    if not obs in M[start]:
      M[start][obs] = set()
    M[start][obs].add(end)
  
current = S
for (idx, obs) in enumerate(input):
  next = set()
  for s in current:
    if s in M and obs in M[s]:
      next = next.union(M[s][obs])
  current = next

if current.intersection(F):
  print(True, current.intersection(F))
else:
  print(False)

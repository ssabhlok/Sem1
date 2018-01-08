# FSA to recognize strings over the alphabet {a,b} that have an even number of b's

import sys

Q = {"q0","q1"}		
S = {"q0"}
F = {"q0"}
X = {"a","b"}

M = {	"q0": 	{ 	"a": {"q0"},
					"b": {"q1"} 	},
		"q1":	{	"a": {"q1"},
					"b": {"q0"}	}
	}

#input = ["a","b","a"]
input = sys.argv[1]

T = [S] #initial set of states

# build the sequence of acceptable set of states
for (idx,obs) in enumerate(input):
	T.append(set())
	for s in T[idx]:
		if s in M and obs in M[s]:
			T[idx+1] = T[idx+1].union(M[s][obs])

endStates = T[len(input)]
if endStates.intersection(F):
	print(True,endStates.intersection(F))
else:
	print(False)

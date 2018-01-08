import os
import sys
import csv
import random
import itertools
from operator import itemgetter
from collections import defaultdict
import numpy as np
import scipy
import scipy.spatial.distance
from numpy.linalg import svd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import time

vsmdata_home = "vsmdata"
def build(src_filename, delimiter=',', header=True, quoting=csv.QUOTE_MINIMAL):
    """
    Returns
    -------
    (np.array, list of str, list of str)
       The first member is a dense 2d Numpy array, and the second 
       and third are lists of strings (row names and column names, 
       respectively). The third (column names) is None if the 
       input file has no header. The row names are assumed always 
       to be present in the leftmost column.    
    """
    reader = csv.reader(open(src_filename), delimiter=delimiter, quoting=quoting)
    colnames = None
    if header:
        colnames = next(reader)
        colnames = colnames[1: ]
    mat = []    
    rownames = []
    for line in reader:        
        rownames.append(line[0])            
        mat.append(np.array(list(map(float, line[1: ]))))
    return (np.array(mat), rownames, colnames)

ww = build(os.path.join(vsmdata_home, 'imdb-wordword.csv'))
wd = build(os.path.join(vsmdata_home, 'imdb-worddoc.csv'))

def euclidean(u, v):    
	"""Eculidean distance between 1d np.arrays `u` and `v`, which must 
	have the same dimensionality. Returns a float."""
	# Use scipy's method:
	return scipy.spatial.distance.euclidean(u, v)
	# Or define it yourself:
	# return vector_length(u - v)

def vector_length(u):
	"""Length (L2) of the 1d np.array `u`. Returns a new np.array with the 
	same dimensions as `u`."""
	return np.sqrt(np.dot(u, u))

def length_norm(u):
	"""L2 norm of the 1d np.array `u`. Returns a float."""
	return u / vector_length(u)

def cosine(u, v):        
	"""Cosine distance between 1d np.arrays `u` and `v`, which must have 
	the same dimensionality. Returns a float."""
	# Use scipy's method:
	return scipy.spatial.distance.cosine(u, v)
	# Or define it yourself:
	# return 1.0 - (np.dot(u, v) / (vector_length(u) * vector_length(v)))

def matching(u, v):    
	"""Matching coefficient between the 1d np.array vectors `u` and `v`, 
	which must have the same dimensionality. Returns a float."""
	# The scipy implementation is for binary vectors only. 
	# This version is more general.
	return np.sum(np.minimum(u, v))

def jaccard(u, v):    
	"""Jaccard distance between the 1d np.arrays `u` and `v`, which must 
	have the same dimensionality. Returns a float."""
	# The scipy implementation is for binary vectors only. 
	# This version is more general.
	return 1.0 - (matching(u, v) / np.sum(np.maximum(u, v)))

def neighbors(word, mat, rownames, distfunc=cosine):    
	"""Tool for finding the nearest neighbors of `word` in `mat` according 
	to `distfunc`. The comparisons are between row vectors.
	
	Parameters
	----------
	word : str
		The anchor word. Assumed to be in `rownames`.
		
	mat : np.array
		The vector-space model.
		
	rownames : list of str
		The rownames of mat.
		
	distfunc : function mapping vector pairs to floats (default: `cosine`)
		The measure of distance between vectors. Can also be `euclidean`, 
		`matching`, `jaccard`, as well as any other distance measure  
		between 1d vectors.
		
	Raises
	------
	ValueError
		If word is not in rownames.
	
	Returns
	-------    
	list of tuples
		The list is ordered by closeness to `word`. Each member is a pair 
		(word, distance) where word is a str and distance is a float.
	
	"""
	if word not in rownames:
		raise ValueError('%s is not in this VSM' % word)
	w = mat[rownames.index(word)]
	dists = [(rownames[i], distfunc(w, mat[i])) for i in range(len(mat))]
	return sorted(dists, key=itemgetter(1), reverse=False)

def prob_norm(u):
	"""Normalize 1d np.array `u` into a probability distribution. Assumes 
	that all the members of `u` are positive. Returns a 1d np.array of 
	the same dimensionality as `u`."""
	return u / np.sum(u)

def pmi(mat, rownames=None, positive=True):
	"""Pointwise Mutual Information with Positive on by default.
	
	Parameters
	----------
	mat : 2d np.array
		The matrix to operate on.
		
	rownameS : list of str or None
		Not used; it's an argument only for consistency with other methods 
		defined here.
		
	positive : bool (default: True)
		Implements Positive PMI.
		
	Returns
	-------    
	(np.array, list of str)
		The first member is the PMI-transformed version of `mat`, and the 
		second member is `rownames` (unchanged).
	
	"""    
	# Joint probability table:
	p = mat / np.sum(mat, axis=None)
	# Pre-compute column sums:
	colprobs = np.sum(p, axis=0)
	# Vectorize this function so that it can be applied rowwise:
	np_pmi_log = np.vectorize((lambda x : _pmi_log(x, positive=positive)))
	p = np.array([np_pmi_log(row / (np.sum(row)*colprobs)) for row in p])   
	return (p, rownames)

def _pmi_log(x, positive=True):
	"""With `positive=False`, return log(x) if possible, else 0.
	With `positive=True`, log(x) is mapped to 0 where negative."""
	val = 0.0
	if x > 0.0:
		val = np.log(x)
	if positive:
		val = max([val,0.0])
	return val

def tfidf(mat, rownames=None):
	"""TF-IDF 
	
	Parameters
	----------
	mat : 2d np.array
		The matrix to operate on.
		
	rownames : list of str or None
		Not used; it's an argument only for consistency with other methods 
		defined here.
		
	Returns
	-------
	(np.array, list of str)    
		The first member is the TF-IDF-transformed version of `mat`, and 
		The second member is `rownames` (unchanged).
	
	"""
	colsums = np.sum(mat, axis=0)
	doccount = mat.shape[1]
	w = np.array([_tfidf_row_func(row, colsums, doccount) for row in mat])
	return (w, rownames)

def _tfidf_row_func(row, colsums, doccount):
	df = float(len([x for x in row if x > 0]))
	idf = 0.0
	# This ensures a defined IDF value >= 0.0:
	if df > 0.0 and df != doccount:
		idf = np.log(doccount / df)
	tfs = row/colsums
	return tfs * idf

def lsa(mat=None, rownames=None, k=100):
	"""Latent Semantic Analysis using pure scipy.
	
	Parameters
	----------
	mat : 2d np.array
		The matrix to operate on.
		
	rownames : list of str or None
		Not used; it's an argument only for consistency with other methods 
		defined here.
		
	k : int (default: 100)
		Number of dimensions to truncate to.
		
	Returns
	-------    
	(np.array, list of str)
		The first member is the SVD-reduced version of `mat` with 
		dimension (m x k), where m is the rowcount of mat and `k` is 
		either the user-supplied k or the column count of `mat`, whichever 
		is smaller. The second member is `rownames` (unchanged).

	"""    
	rowmat, singvals, colmat = svd(mat, full_matrices=False)
	singvals = np.diag(singvals)
	trunc = np.dot(rowmat[:, 0:k], singvals[0:k, 0:k])
	return (trunc, rownames)

def wordsim_dataset_reader(src_filename, header=False, delimiter=','):    
	"""Basic reader that works for all four files, since they all have the 
	format word1,word2,score, differing only in whether or not they include 
	a header line and what delimiter they use.
	
	Parameters
	----------
	src_filename : str
		Full path to the source file.
		
	header : bool (default: False)
		Whether `src_filename` has a header.
		
	delimiter : str (default: ',')
		Field delimiter in `src_filename`.
	
	Yields
	------    
	(str, str, float)
		(w1, w2, score) where `score` is the negative of the similarity 
		score in the file so that we are intuitively aligned with our 
		distance-based code.
	
	"""
	reader = csv.reader(open(src_filename), delimiter=delimiter)
	if header:
		next(reader)
	for row in reader:
		w1, w2, score = row
		# Negative of scores to align intuitively with distance functions:
		score = -float(score)
		yield (w1, w2, score)

def wordsim353_reader():
	"""WordSim-353: http://www.cs.technion.ac.il/~gabr/resources/data/wordsim353/"""
	src_filename = os.path.join(vsmdata_home, 'wordsim', 'wordsim353.csv')
	return wordsim_dataset_reader(src_filename, header=True)

def mturk287_reader():
	"""MTurk-287: http://tx.technion.ac.il/~kirar/Datasets.html"""
	src_filename = os.path.join(vsmdata_home, 'wordsim', 'MTurk-287.csv')
	return wordsim_dataset_reader(src_filename, header=False)

def mturk771_reader():
	"""MTURK-771: http://www2.mta.ac.il/~gideon/mturk771.html"""
	src_filename = os.path.join(vsmdata_home, 'wordsim', 'MTURK-771.csv')
	return wordsim_dataset_reader(src_filename, header=False)

def men_reader():
	"""MEN: http://clic.cimec.unitn.it/~elia.bruni/MEN"""
	src_filename = os.path.join(vsmdata_home, 'wordsim', 'MEN_dataset_natural_form_full')
	return wordsim_dataset_reader(src_filename, header=False, delimiter=' ')

def word_similarity_evaluation(reader, mat, rownames, distfunc=cosine):
	"""Word-similarity evalution framework.
	
	Parameters
	----------
	reader : iterator
		A reader for a word-similarity dataset. Just has to yield
		tuples (word1, word2, score).
	
	mat : 2d np.array
		The VSM being evaluated.
		
	rownames : list of str
		The names of the rows in mat.
		
	distfunc : function mapping vector pairs to floats (default: `cosine`)
		The measure of distance between vectors. Can also be `euclidean`, 
		`matching`, `jaccard`, as well as any other distance measure 
		between 1d vectors.  
	
	Prints
	------
	To standard output
		Size of the vocabulary overlap between the evaluation set and
		rownames. We limit the evalation to the overlap, paying no price
		for missing words (which is not fair, but it's reasonable given
		that we're working with very small VSMs in this notebook).
	
	Returns
	-------
	float
		The Spearman rank correlation coefficient between the dataset
		scores and the similarity values obtained from `mat` using 
		`distfunc`. This evaluation is sensitive only to rankings, not
		to absolute values.
	
	"""
	
	sims = defaultdict(list)
	vocab = set([])
	for w1, w2, score in reader():
		if w1 in rownames and w2 in rownames:
			sims[w1].append((w2, score))
			sims[w2].append((w1, score))
			vocab.add(w1)
			vocab.add(w2)
	print("Evaluation vocabulary size: %s" % len(vocab))
	# Evaluate the matrix by creating a vector of all_scores for data
	# and all_dists for mat's distances. 
	all_scores = []
	all_dists = []
	for word in vocab:
		vec = mat[rownames.index(word)]
		vals = sims[word]
		cmps, scores = zip(*vals)
		all_scores += scores
		all_dists += [distfunc(vec, mat[rownames.index(w)]) for w in cmps]
	# Return just the rank correlation coefficient (index [1] would be the p-value):
	return scipy.stats.spearmanr(all_scores, all_dists)[0]

def full_word_similarity_evaluation(mat, rownames):
	"""Evaluate the (mat, rownames) VSM against all four datasets."""
	for reader in (wordsim353_reader, mturk287_reader, mturk771_reader, men_reader):
		print("="*40)
		print(reader.__name__)
		print('Spearman r: %0.03f' % word_similarity_evaluation(reader, mat, rownames))

start_time = time.time()

ww = build(os.path.join(vsmdata_home, 'imdb-wordword.csv'))
wd = build(os.path.join(vsmdata_home, 'imdb-worddoc.csv'))

ww_ppmi = pmi(mat=ww[0], rownames=ww[1], positive=True)
ww_pmi= pmi(mat=ww[0],rownames=ww[1],positive=False)
ww_tfidf = tfidf(mat=ww[0],rownames=ww[1])

ww_pmi_lsa = lsa(mat=ww_pmi[0],rownames=ww_pmi[1])
ww_ppmi_lsa = lsa(mat=ww_ppmi[0],rownames=ww_ppmi[1])
ww_tfidf_lsa = lsa(mat=ww_tfidf[0],rownames=ww_tfidf[1])

print()
print("Bare Matrix")
full_word_similarity_evaluation(ww[0],ww[1])
print()
print("PMI Matrix")
full_word_similarity_evaluation(ww_pmi[0],ww_pmi[1])
print()
print("Positive PMI Matrix")
full_word_similarity_evaluation(ww_ppmi[0],ww_ppmi[1])
print()
print("TF-IDF Matrix")
full_word_similarity_evaluation(ww_tfidf[0],ww_tfidf[1])
print()
print("PMI LSA Matrix")
full_word_similarity_evaluation(ww_pmi_lsa[0],ww_pmi_lsa[1])
print()
print("PPMI LSA Matrix")
full_word_similarity_evaluation(ww_ppmi_lsa[0],ww_ppmi_lsa[1])
print()
print("TF-IDF LSA Matrix")
full_word_similarity_evaluation(ww_tfidf_lsa[0],ww_tfidf_lsa[1])
print()
print("Runtime (s): ", int(time.time()-start_time))

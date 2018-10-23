# -*- coding: utf-8 -*-
"""
Created on Fri Oct 10 14:34:39 2018

@author: Christian Rekdal
"""

from leseTxt import opprett_testset
from leseTxt import hent_ut_beretning


a = opprett_testset()

def rette_tekstfil_test():
    fihaf = []
    testfil_1,testfil_2,testfil_3 = hent_ut_beretning()
    for items in testfil_3:
        word = items.split(' ')
        fihaf.append(word)
    return fihaf
        

def P(word, N=sum(a.values())): 
    "Probability of `word`."
    return a[word] / N

def correction(word): 
    "Most probable spelling correction for word."
    return max(candidates(word), key=P)

def candidates(word): 
    "Generate possible spelling corrections for word."
    return (known([word]) or known(edits1(word)) or known(edits2(word)) or [word])

def known(words): 
    "The subset of `words` that appear in the dictionary of WORDS."
    return set(w for w in words if w in a)

def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = 'abcdefghijklmnopqrstuvwxyzæøå'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def edits2(word): 
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))

    
    
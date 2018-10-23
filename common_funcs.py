# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 16:00:45 2017

@author: Eirik.Sandvik
"""

#%% Importing libraries
from nltk.corpus import stopwords
from re import sub
from nltk.tokenize import word_tokenize
import math

#%% Vasker avsnitt
def vasking_av_ord(tekst, ikke_fjern):# Funksjon som Vasker avsnitt
# "ikke_fjern" en int som bestemmer hvilke stoppord som IKKE skal vaskes bort. 1 = alle stoppord skal fjernes, 2 = behold ikke/ikkje
    if ikke_fjern==1:
        ikke_fjern_list=[]
    elif ikke_fjern==2:
        ikke_fjern_list=['ikke', 'ikkje']
    stop_ord=set(stopwords.words("norwegian"))
    bare_bokstaver = sub("[^a-zA-Z]", " ", tekst)
    små_bokstaver_avsnitt=bare_bokstaver.lower()
    words=word_tokenize(små_bokstaver_avsnitt)
    filtrert_setning=[]

    for w in words:
        if w not in stop_ord or w in ikke_fjern_list:
            filtrert_setning.append(w)     
    return(" ".join(filtrert_setning))

#%% Levenstein Distance
def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def lev_vector(setning,dokument):
    len_s = len(setning)
    jump_factor = 0.37
    cut_lim = math.ceil(len_s / 6)
#    print("Cut limit: "+str(cut_lim))
    len_d = len(dokument)
    lev_vec = []
    min_idx = []
    nexti = 0
    for i in range(len_d-len_s):
        if nexti == i:
            L = levenshtein(setning,dokument[i:i+len_s])
            nexti = i+1+math.ceil(L*jump_factor)
            if L <= cut_lim:
                lev_vec.append(L)
                min_idx.append(i)
                nexti = i+len_s
    Lout = []
    Iout = []
    
    #If we have any results:
    if len(min_idx)>0:
        Imin = min_idx[0]
        Lmin = lev_vec[0]
        for i in range(len(min_idx)-1):
            #If this is in the a major jump, use the previous best
            if min_idx[i+1]-min_idx[i] > len_s:
                Lout.append(Lmin)
                Iout.append(Imin)
                Lmin = lev_vec[i+1]
                Imin = min_idx[i+1]
            elif lev_vec[i+1]<Lmin:
                Lmin = lev_vec[i+1]
                Imin = min_idx[i+1]
        Lout.append(Lmin)
        Iout.append(Imin)
    return Lout, Iout

def find_paragraph(i,dokument):
    char = '\n'
    # find iStart
    iStart = i
    cPrev = ''
    cCurr = dokument[iStart]
    while True:
        if iStart == 0:
            break
        if cPrev == char and cCurr == char:
            break
        cPrev = cCurr
        iStart -= 1
        cCurr = dokument[iStart]
    
    # find iEnd
    iEnd = i
    cNext = ''
    cCurr = dokument[iEnd]
    dokEnd = len(dokument)-1
    while True:
        if iEnd == dokEnd:
            break
        if cNext == char and cCurr == char:
            break
        cNext = cCurr
        iEnd += 1
        cCurr = dokument[iEnd]
    return dokument[iStart:iEnd].strip()
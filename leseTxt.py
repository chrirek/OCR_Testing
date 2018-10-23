# -*- coding: utf-8 -*-
"""
Created on Fri Oct 10 14:34:39 2018

@author: Christian Rekdal
"""
import os
import pandas as pd
from nltk import ngrams
import re
from collections import Counter
from testscript import prediker_ett_dokument

'root_dir = --------------- filbane til mappen du vil kjøre -----------------------

'leser alle undermapper og legger filnavn og filbaner i lister'
def get_files_in_dir():
    
    if not isinstance(root_dir, str):
        print('input argument is not a string')
        return

    #Filbaner
    full_file_list = []
    #Filnavn
    file_names = []

    for roots, dirs, files in os.walk(root_dir):
        for file in files:
            full_file_list.append(os.path.join(roots, file))
            file_names.append(file)

    'sorter listen basert på file extension'
    full_file_list.sort(key=lambda f: os.path.splitext(f)[1])
    file_names.sort(key=lambda f: os.path.splitext(f)[1])

    return file_names, full_file_list

'Filtrer hvilke txt filer som er aktuelle'
def find_files_to_process():
    
    list_working_files, full_file_list = get_files_in_dir()
    new_file_list = []

    if not isinstance(list_working_files, list):
        print('input argument is not a list')
        return

    'finn filene jeg er intressert i, alle ".txt" (uten "txt-noter.txt")'
    for file, full_path in (zip(list_working_files, full_file_list)):
        
        if "txt-noter" not in file and file.endswith('.txt'):
            new_file_list.append(full_path)

    'returner "vasket" liste med akutelle filbaner'
    return new_file_list


'leser gjennom en liste med txt filer og henter ut revisors beretning fra ''testscript'', returnerer 3 forskjellige lister'
def hent_ut_beretning() :
    
    beretning = find_files_to_process()
    a,b,c = [],[],[]
    
    for bi in beretning:
      t1,t2,t3 = prediker_ett_dokument(bi)
      
      a.extend(t1)
      b.extend(t2)
      c.extend(t3)
      
    return a,b,c


'BURDE HA NOE SOM RETURNERER TEKSTFILER'
'Går igjennom lister med tekst og legger til i en dict og teller antall forkomster av hvert ord'
def count_words_in_beretning():
    
    liste_bare_txt, b, c = hent_ut_beretning()
    temp = {}
    WORDS = {}
    i = 0
    
    for listItem in c:
        
        if i == 0 :
            WORDS = Counter(words(listItem))
            i+=1
        else:
            temp = Counter(words(listItem))
            for key in temp.keys():
                if key in WORDS.keys():
                    WORDS[key] = WORDS[key] + temp[key]
                else:
                    WORDS[key] = temp[key]
    
    return WORDS


def skriv_til_excel(dictonary):
    
    df = pd.DataFrame(data=[dictonary.keys(),dictonary.values()])
    df = df.transpose()
    df.columns = ['Ord','Count']
    df = df.sort_values(['Count'], ascending=False)
    
    writer = pd.ExcelWriter('antall_unike_ord_i_beretning.xlsx', engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1')
    
    writer.save()

    return df
        
        
    #df.dropna(inplace=True)

'Kryssjekker alle ord i revisors beretning med norsk ordliste for å lage et testset'
def opprett_testset():
    #DICT - Norsk ordliste
    fullFormsListe = read_files('fullformsliste.txt')
    
    #DICT - Revisors beretning ordliste
    beretningsOrd = count_words_in_beretning()
    
    temp = {}
    
    for key in beretningsOrd.keys():

        if key in fullFormsListe.keys():
            temp[key] = beretningsOrd[key]
    
    temp = Counter(temp)
    return temp
                
          
'Tell antall forekomster av hvert ord'      
def words(text): 
    return re.findall(r'\b[^\d\W]+\b(?:-\w+)*', text.lower())
    

'Les en teksfil og returer som dict'
def read_files(file):
    
    ordliste = Counter(words(open(file).read()))

    return ordliste
    

'funksjon som gir antall unike n-gram. Tar n-gram som input'
'Output er et Datasett 2*n kolonner. Kolonne 1: 1, gram, kolonne2: 1-gram count'
"""
def count_n_grams(n, liste):
    
    di = dict()
    liste_grams = []
    counter = 1
    
    while counter <= n:
        
        di = {}
        for i in liste:
            
            n_grams = ngrams(i.split(), counter)
            for grams in n_grams:
               if grams in di:
                   di[grams] = di[grams]+1
               else:
                   di[grams] = 1
                   
        liste_grams.append(di)
        
        counter = counter + 1
    
    # Looper liste med dictonary og legger til i df og appender alle til df2
    df2 = pd.DataFrame()
    
    for index, value in enumerate(liste_grams):
        
        df = pd.DataFrame(data=[value.keys(),value.values()])
        df = df.transpose()
        df.columns = [str(index+1)+'grams',str(index+1)+'gram-count']
        df = df.sort_values([str(index+1)+'gram-count'], ascending=True)
        
        
        # Legger inn df i df2, slik at alle n-grams fra 1 og oppover kommer med
        df2 = df2.append(df)
        df2[str(index+1)+'gram-count']=df2[str(index+1)+'gram-count'].values[:: -1]
        df2[str(index+1)+'grams']=df2[str(index+1)+'grams'].values[::-1]
        
        
        
    df2.dropna(inplace=True)

    
    return df2"""

"""'Les alle file i den nye listen'
def read_files():
    
    liste_bare_txt = find_files_to_process()
    file_content_list = []
    
    for listItem in liste_bare_txt:
        
        with open(listItem,"r") as f:
            content = f.readlines()
            file_content_list.append(''.join(content))
            f.close()
            
    return file_content_list"""

'Leser alle filer og teller antall forekomster av ord i fil'
"""def count_words_in_file():
    
    liste_bare_txt, b, c = hent_ut_beretning(find_files_to_process())
    temp = {}
    WORDS = {}
    i = 0
    
    for listItem in liste_bare_txt:
        
        if i == 0 :
            WORDS = Counter(words(open(listItem,encoding='iso8859_10').read()))
            i+=1
        else:
            temp = Counter(words(open(listItem,encoding='iso8859_10').read()))
            for key in temp.keys():
                if key in WORDS.keys():
                    WORDS[key] = WORDS[key] + temp[key]
                else:
                    WORDS[key] = temp[key]
    
    return WORDS"""

# coding: utf-8

# %% Importing libraries
from sys import argv
import logging
import re
from pandas import DataFrame
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer
from numpy import argmax, where, count_nonzero
from common_funcs import vasking_av_ord, lev_vector, find_paragraph
from os.path import basename, dirname, realpath, join, isfile


# %%
def hent_modell(kat):
    classifier_filename = dirname(realpath(__file__)) + ('\\trente_modeller\\') + kat + ('_svm_classifier.pk1')
    vectorizer_filename = dirname(realpath(__file__)) + ('\\trente_modeller\\') + kat + ('_vectorizer_vocabulary.pkl')
    classifier = joblib.load(classifier_filename)
    vocab, ngramr, modell_ant_features, _, ikke_fjern = joblib.load(vectorizer_filename)
    vectorizer = CountVectorizer(ngram_range=ngramr, analyzer='word', vocabulary=vocab, tokenizer=None,
                                 preprocessor=None, stop_words=None, max_features=modell_ant_features)
    kat_index = where(classifier.classes_ == kat)[0][0]

    return classifier, vectorizer, kat_index, ikke_fjern


# %%
def split_avsnitt(tekst):
    return tekst.split('\n\n')  # Returnerer "list" av avsnitt


# %%
def split_sider(tekst):
    return tekst.split('----NY SIDE:')  # Returnerer "list" av sider


# Her henter vi opp alle modellene per side

def prediker_ett_dokument(path):
    with open(path, encoding='iso8859_10', newline=None) as f:
        global rev_modell
        global eng_modell
        global stdsetn_modell

        # Lag tom versjon av output
        fileRow = {}
        fileRow['journalnr'] = basename(path).split('.')[0]
        tekst_fil = f.read()

        # Splitt dokument på sider og vask sidene
        alle_sider_raa = split_sider(tekst_fil)
        alle_sider_vasket = []
        for side_raa in alle_sider_raa:
            alle_sider_vasket.append(vasking_av_ord(side_raa, 1))

        # Kjør modell for å skille revisors beretning fra resten
        kat_features = rev_modell['vectorizer'].transform(alle_sider_vasket).toarray()
        pred_kat_rev = rev_modell['classifier'].predict(kat_features)
        pred_prob_rev = rev_modell['classifier'].predict_proba(kat_features)[:, rev_modell['kat_index']]

        # Kjør modell for å finne engelsek sider
        kat_features = eng_modell['vectorizer'].transform(alle_sider_vasket).toarray()
        pred_kat_eng = eng_modell['classifier'].predict(kat_features)
        #        pred_prob_eng = eng_modell['classifier'].predict_proba(kat_features)[:,eng_modell['kat_index']]

        # teller resultater fra rev og eng- modeller
        number_of_pages = len(pred_kat_rev)
        number_of_rev = count_nonzero(pred_kat_rev == 'rev')
        number_of_eng = count_nonzero(pred_kat_eng == 'eng')

        # Regelsett for hva vi regner som engelsk. Her kan/bør det gjøres justeringer.
        if number_of_pages >= 5:
            is_eng = True if (number_of_eng / (number_of_pages - 3)) > 0.5 else False
        else:
            is_eng = True if number_of_eng > 0 else False

        fileRow['regnskap_ikke_norsk'] = 1 if is_eng else 0

        if number_of_rev == 0:
            alle_avsnitt_vasket1 = []
            alle_avsnitt_vasket2 = []
            alle_avsnitt_raa = []
        else:
            alle_avsnitt_vasket1 = []
            alle_avsnitt_vasket2 = []
            alle_avsnitt_raa = []

            # Loop alle sider, forbered avsnitt for å kjøre modell for de sidene som er revisors beretning
            forrige_side_rev = False
            for i, kat in enumerate(pred_kat_rev):
                if kat == 'rev' or (forrige_side_rev and pred_prob_rev[i] > 0.3):
                    for avsnitt_raa in split_avsnitt(alle_sider_raa[i]):
                        alle_avsnitt_vasket1.append(vasking_av_ord(avsnitt_raa, 1))
                        alle_avsnitt_vasket2.append(vasking_av_ord(avsnitt_raa, 2))
                        alle_avsnitt_raa.append(avsnitt_raa)
                    forrige_side_rev = True
                else:
                    forrige_side_rev = False

            # Modell som predikerer hvilke avsnitt som er standarsetninger og ikke
            kat_features = stdsetn_modell['vectorizer'].transform(alle_avsnitt_vasket1).toarray()
            pred_kat_stdsetn = stdsetn_modell['classifier'].predict(kat_features)
            pred_prob_stdsetn = stdsetn_modell['classifier'].predict_proba(kat_features)[:, stdsetn_modell['kat_index']]

            # Loop baklengs og slett avsnitt som er standarsetninger
            for i, v in enumerate(range(len(pred_kat_stdsetn) - 1, -1, -1)):
                if pred_prob_stdsetn[v] > 0.9:
                    del alle_avsnitt_vasket1[v]
                    del alle_avsnitt_vasket2[v]
                    del alle_avsnitt_raa[v]


    return alle_avsnitt_vasket1, alle_avsnitt_vasket2, alle_avsnitt_raa

global rev_modell
global eng_modell
global stdsetn_modell
global not_modell

rev_modell = {}
rev_modell['kat'] = 'rev'
rev_modell['classifier'], rev_modell['vectorizer'], rev_modell['kat_index'], rev_modell['ikke_fjern'] = hent_modell(
    'rev')

eng_modell = {}
eng_modell['kat'] = 'eng'
eng_modell['classifier'], eng_modell['vectorizer'], eng_modell['kat_index'], eng_modell['ikke_fjern'] = hent_modell(
    'eng')

stdsetn_modell = {}
stdsetn_modell['kat'] = 'stdsetn'
stdsetn_modell['classifier'], stdsetn_modell['vectorizer'], stdsetn_modell['kat_index'], stdsetn_modell[
    'ikke_fjern'] = hent_modell('stdsetn')

#path = 'C:\\Users\\ChristianRekdal\\Desktop\\Python ting\\Arkiv\\INBOUND\\TETML\\220\\550.txt'

#liste1, liste2, listeRaa = prediker_ett_dokument(path)

#print(listeRaa)
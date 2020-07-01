#!/usr/bin/env python
# coding: utf-8

import os
import json
from docx import Document
from io import StringIO, BytesIO
import re
import time
import datetime

import pandas as pd
import json
import spacy
from nltk.corpus import stopwords

from gensim.models import LdaModel
from gensim.models.wrappers import LdaMallet
import gensim.corpora as corpora
from gensim.corpora import Dictionary
from gensim import matutils, models
from gensim.models import CoherenceModel, TfidfModel, HdpModel
from gensim.models.phrases import Phrases, Phraser
import pyLDAvis.gensim

from sklearn.cluster import KMeans
from scipy.sparse import csc_matrix
from gensim.matutils import corpus2csc
from matplotlib.ticker import MaxNLocator
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import cosine_similarity

from docx import Document
from io import StringIO, BytesIO
import matplotlib.pyplot as plt

nlp = spacy.load("en_core_web_sm")
# Adopted from 
nltk_stopwords = {'hers', 'each', 're', 'into', 'been', 'out', 'has', "hasn't", 'did', 'them', 'until', 's', 'your', 'its', 'is', 'were', 'have', 'because', "couldn't", 'up', "won't", 'i', 'if', 'mustn', 'you', "you'd", 'down', 'while', 'for', 'does', 'this', 'when', 'which', 'are', 'mightn', 'what', 'such', "you're", 've', 'off', 'now', 'that', 'hasn', "you've", "needn't", "that'll", 'wasn', 'couldn', 'these', 'with', "shouldn't", "she's", 'of', 'had', 'they', 'most', 'here', 'o', 'ma', 'was', 'm', 'all', 'nor', 'our', "you'll", 'myself', 'both', 'needn', 'her', 'yourselves', 'again', 'having', 'y', 'the', 'under', 'an', 'how', 'only', 'so', 'above', 'just', 'about', 'wouldn', 'from', 'over', 'can', "should've", 'isn', 'doesn', "hadn't", 'll', 'but', 'no', 'more', 'yourself', "shan't", 'theirs', 'don', 'those', 'against', 'same', 'd', 'ours', 'hadn', 'who', 'by', "weren't", 'we', "isn't", 'doing', 'why', 'too', 'won', 'between', 'then', 'shouldn', 'do', "it's", 'own', 'will', 'being', 'at', 'she', 'themselves', 'than', 'he', "haven't", 'him', 'other', 'himself', 'to', 'some', 't', "didn't", 'any', 'didn', 'during', 'weren', 'haven', 'after', 'not', 'there', 'be', 'as', "wouldn't", 'aren', 'my', 'his', 'through', 'on', 'few', 'it', 'or', 'where', "doesn't", 'before', 'me', 'am', 'below', "don't", 'herself', 'should', 'whom', 'very', 'shan', "mightn't", 'their', "mustn't", 'a', 'further', 'in', 'ain', 'once', 'yours', 'ourselves', 'itself', "wasn't", "aren't", 'and'}

def preprocess(strlist,
               min_token_len = 2,
               allowed_pos = ['ADV', 'ADJ', 'VERB', 'NOUN', 'PART', 'NUM', 'PROPN']): 
    removal = ['-', r'i\.e\.']
    res = list()
    not_stopword = {'call'}
    for string in strlist:
        text = re.sub(r"|".join(removal), ' ', string.lower())
        doc = nlp(text)
        res += [token.lemma_ for token in doc                if token.pos_ in allowed_pos                # Spacy considers 'call' as a stop word, which is not suitable for our case
               and (token.text in not_stopword or not token.is_stop) \
#                and token.text not in stop_words \              
#                and token.is_alpha \
               and len(token.lemma_) > min_token_len
               ]
    
    return ' '.join(res)


def get_dct_dtmatrix(sops):
    corpus = [sop.split() for sop in map(preprocess, sops)]
#     phrases = Phrases(corpus, min_count = 1, threshold = 1)
#     bigram = Phraser(phrases)
#     corpus = bigram(corpus)
    dictionary = corpora.Dictionary(corpus)
    doc_term_matrix = [dictionary.doc2bow(doc) for doc in corpus]
    return doc_term_matrix, corpus, dictionary


def bow2tfidf(doc_term_bow, corpus_tfidf):
    doc_term_tfidf = corpus_tfidf[doc_term_bow]
    scipy_tfidf = corpus2csc(doc_term_tfidf, num_terms = len(corpus_tfidf.idfs))
    tfidf_mtx = csc_matrix(scipy_tfidf).T.toarray()
#     print(f'The dimensions of tfidf matrix = {tfidf_mtx.shape}')
    return tfidf_mtx


def show_result(query_mtx, corpus_mtx, df_clusters, N = 20):
    """
    Apply tfidf conversion

    params
    ----
    doc_term_bow: array of (int, int) for term frequency
    corpus_tfidf: tfidf model fitted with doc_term_bow above

    returns
    ----
    dataframe with up t0 20 most likely match 

    """
    sim = cosine_similarity(query_mtx, corpus_mtx)[0]
    cluster_sorted = zip(sim.argsort()[::-1], sorted(sim)[::-1])
    idx = list()
    for cnt, (i, prob) in enumerate(cluster_sorted):
        if prob < 0.1 or cnt >= N:
            break
        idx.append(i)
    return df_clusters.iloc[idx].copy()


def query_situation(query, corpus_tfidf, corpus_dct, corpus_mtx, df_clusters, N = 20):
    """
    Apply tfidf conversion

    params
    ----
    doc_term_bow: array of (int, int) for term frequency
    corpus_tfidf: tfidf model fitted with doc_term_bow above

    returns
    ----
    dataframe with up t0 20 most likely match 

    """
    query_corpus = [preprocess([query]).split()]
    query_bow = [corpus_dct.doc2bow(doc) for doc in query_corpus]
    query_tfidf_mtx = bow2tfidf(query_bow, corpus_tfidf)
    return show_result(query_tfidf_mtx, corpus_mtx, df_clusters, N = N)

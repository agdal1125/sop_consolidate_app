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


def preprocess(nlp, 
               strlist,
               min_token_len = 2,
               allowed_pos = ['ADV', 'ADJ', 'VERB', 'NOUN', 'PART', 'NUM', 'PROPN']): 
    """
    Pre-process texts and return lemmatized words

    params
    ----
    nlp: Spacy en_core_web_sm model
    strlist : list of strings
    min_token_len: minimum length of lammetized tokens
    allowed_pos: allowable part-of-speech

    returns
    ----
    string of lammetized tokens

    """
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


def get_dct_dtmatrix(nlp, sops):
    """
    Convert texts into Gensim dictionary and doc term matrix

    params
    ----
    nlp: Spacy en_core_web_sm model
    sops: list of strings

    returns
    ----
    doc_term_matrix: array of (int, int) for term frequency
    corpus: string of tokens
    dictionary: Gensim word2vec dictionary

    """
    corpus = [sop.split() for sop in map(lambda x: preprocess(nlp, x), sops)]
#     phrases = Phrases(corpus, min_count = 1, threshold = 1)
#     bigram = Phraser(phrases)
#     corpus = bigram(corpus)
    dictionary = corpora.Dictionary(corpus)
    doc_term_matrix = [dictionary.doc2bow(doc) for doc in corpus]
    return doc_term_matrix, corpus, dictionary


def bow2tfidf(doc_term_bow, corpus_tfidf):
    """
    Apply tfidf conversion

    params
    ----
    doc_term_bow: array of (int, int) for term frequency
    corpus_tfidf: tfidf model fitted with doc_term_bow above

    returns
    ----
    tfidf_mtx: array of (int, float) 

    """
    doc_term_tfidf = corpus_tfidf[doc_term_bow]
    scipy_tfidf = corpus2csc(doc_term_tfidf, num_terms = len(corpus_tfidf.idfs))
    tfidf_mtx = csc_matrix(scipy_tfidf).T.toarray()
#     print(f'The dimensions of tfidf matrix = {tfidf_mtx.shape}')
    return tfidf_mtx


def main():
    """
    Executes all the functions defined above
    """
    nlp = spacy.load("en_core_web_sm")

    notebook_dir = os.getcwd()
    situ_df = pd.read_csv('data/interim/calltaker_situation.csv', 
                        keep_default_na = False, 
                        converters = {'sop': eval})
    doc_term_bow, corpus, dictionary = get_dct_dtmatrix(nlp, situ_df['sop'])
    tfidf_situ = TfidfModel(doc_term_bow)
    tfidf_mtx = bow2tfidf(doc_term_bow, tfidf_situ)
    km_190 = KMeans(n_clusters = 190, random_state = 2020).fit(tfidf_mtx)

    situ_topics_kmeans_tfidf = situ_df.copy()
    situ_topics_kmeans_tfidf['cluster'] = km_190.labels_
    situ_topics_kmeans_tfidf = situ_topics_kmeans_tfidf.sort_values(by = ['cluster', 'type', 'juri'], ignore_index = True)
    situ_topics_kmeans_tfidf['situ_lst'] = situ_topics_kmeans_tfidf['situation'].apply(lambda x: [x])
    situ_topics_kmeans_tfidf.to_csv('data/interim/situ_topics_kmeans_tfidf.csv', index = False)


if __name__ == "__main__":
    main()

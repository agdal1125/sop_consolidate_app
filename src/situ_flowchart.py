import pandas as pd
import pydot
import numpy as np
from gensim.models import TfidfModel
import situ_helper as situ
from sklearn.metrics.pairwise import cosine_similarity

from sklearn.feature_extraction.text import TfidfVectorizer

def main():
    df = pd.read_csv(
        'data/interim/situ_topics_kmeans_tfidf.csv',
        converters = {'sop': eval, 'situ_lst': eval}
    )
    df['sop_graph'] = df['sop'].apply(lambda x: '\n'.join(x))
    df = df[['type', 'juri', 'role', 'filename', 'situation', 'sop_graph', 'cluster', 'situ_lst', 'sop']]
    df2 = df.drop(columns = ['role', 'filename', 'juri'])

    for i, df in df2.groupby('cluster'):
        df3 = df.copy().reset_index(drop = True)
        cluster = int(df3.iloc[0]['cluster'])

        # convert situation texts to tf-idf vectors
        situ_tfidf = TfidfVectorizer().fit(df3['situ_lst'].apply(situ.preprocess))
        situ_tfidf_mtx = situ_tfidf.transform(df3['situation'])

        # convert SOP texts to tf-idf vectors
        sop_tfidf =  TfidfVectorizer().fit(df3['sop'].apply(situ.preprocess))
        sop_tfidf_mtx = sop_tfidf.transform(df3['sop_graph'])

        # obtain similarity matrix
        situ_similarity = cosine_similarity(situ_tfidf_mtx)
        sop_similarity = cosine_similarity(sop_tfidf_mtx)

        # add a place holder column for similar nodes
        df3['situ_group'] = df3['situation']
        df3['sop_group'] = df3['sop_graph']

        # The threshold for cosine similarity
        similarity_threshold = 0.45

        situ_grouped = set()
        for i in range(situ_similarity.shape[0]):
            if i in situ_grouped:
                continue
            same_group = np.where(situ_similarity[i] >= similarity_threshold)[0]
            situ_grouped = situ_grouped | set(same_group)
            for j in same_group:
                df3.at[j, 'situ_group'] = df3.iloc[i]['situation']

        sop_grouped = set()
        for i in range(sop_similarity.shape[0]):
            if i in sop_grouped:
                continue
            same_group = np.where(sop_similarity[i] >= similarity_threshold)[0]
            sop_grouped = sop_grouped | set(same_group)
            for j in same_group:
                df3.at[j, 'sop_group'] = df3.iloc[i]['sop_graph']

        graph = pydot.Dot(graph_type='graph', concentrate=True, rankdir='LR')
        df3 = df3[['type', 'situ_group', 'sop_group']]
        nrows, _ = df3.shape
        for i in range(nrows):
            row = df3.iloc[i]
            for p, c in zip(row[:-1], row[1:]):
                edge = pydot.Edge(p, c)
                graph.add_edge(edge)
        graph.write_png(f"img/flowcharts/situ_cluster_{cluster}.png")
        
if __name__ == "__main__":
    main()

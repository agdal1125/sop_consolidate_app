
import pandas as pd
import pydot
import numpy as np
from gensim.models import TfidfModel
import situ_helper as situ
from sklearn.metrics.pairwise import cosine_similarity

from sklearn.feature_extraction.text import TfidfVectorizer

def main():
    type_df = pd.read_csv(
        'data/interim/type_topics_kmeans_tfidf.csv',
        converters = {'sop': eval}
    )
    type_df = type_df.drop(columns = 'sop')

    situ_df = pd.read_csv(
        'data/interim/all_situation.csv',
        converters = {'sop': eval},
        keep_default_na = False
    )
    situ_df['situation'] = situ_df['situation'].apply(lambda x: x if len(x) > 0 else 'situation NA')
    call_situ = situ_df[situ_df['role'] == 'call taker'] \
                    .drop(columns = ['role', 'filename']) \
                    .copy() \
                    .reset_index(drop = True)
    del situ_df

    for _, df in type_df.groupby('cluster'):
        type_i = df.copy().reset_index(drop = True)
        cluster = int(type_i.iloc[0]['cluster'])
        df3 = pd.DataFrame()
        for i in range(type_i.shape[0]):
            row = type_i.iloc[i]
            doc_type = row['type']
            juri = row['juri']
            df_match = call_situ[ (call_situ['type'] == doc_type) & (call_situ['juri'] == juri) ]
            df3 = df3.append(df_match)
        df3 = df3.reset_index(drop = True)
        df3['sop_str'] = df3['sop'].apply(lambda x: '\n'.join(x))
        df3['situ_lst'] = df3['situation'].apply(lambda x: [x])
        df3 = df3[['type', 'juri', 'situation', 'sop_str', 'situ_lst', 'sop']]

        try:
            situ_tfidf = TfidfVectorizer().fit(df3['situ_lst'].apply(situ.preprocess))
            situ_tfidf_mtx = situ_tfidf.transform(df3['situation'])
            sop_tfidf =  TfidfVectorizer().fit(df3['sop'].apply(situ.preprocess))
            sop_tfidf_mtx = sop_tfidf.transform(df3['sop_str'])
            situ_similarity = cosine_similarity(situ_tfidf_mtx)
            sop_similarity = cosine_similarity(sop_tfidf_mtx)
        except:
            print(f'Exception at cluster {cluster}')
            print(f'')
            print(df3['situ_lst'])

        df3['situ_group'] = df3['situation']
        df3['sop_group'] = df3['sop_str']

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
                df3.at[j, 'sop_group'] = df3.iloc[i]['sop_str']

        graph = pydot.Dot(graph_type='graph', concentrate=True, rankdir='LR')
        df3 = df3[['type', 'situ_group', 'sop_group']]
        nrows, _ = df3.shape
        for i in range(nrows):
            row = df3.iloc[i]
            for p, c in zip(row[:-1], row[1:]):
                edge = pydot.Edge(p, c)
                graph.add_edge(edge)
        graph.write_png(f"img/flowcharts/type_cluster_{cluster}.png")

if __name__ == "__main__":
    main()
        
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.manifold import TSNE
from sklearn.metrics.pairwise import cosine_similarity


def preprocess(word_freq_df):
    # Delete columns which have frequency > 5 for more than 90% of the rows
    # Delete columns which have frequency > 5 for only one row
    freq_sat = word_freq_df > 5
    freq_sat_total = freq_sat.sum(axis=0)
    selected = (freq_sat_total > 1) & (freq_sat_total < len(word_freq_df) * 0.9)
    delete_list = []
    for inx in selected.index:
        if not selected[inx]:
            delete_list.append(inx)
    word_freq_df = word_freq_df.drop(delete_list, axis=1)

    # Perform min-max scaling on the dataframe
    min_max_scaler = MinMaxScaler()
    transformed = min_max_scaler.fit_transform(word_freq_df)
    word_freq_df = pd.DataFrame(transformed, columns=word_freq_df.columns, index=list(word_freq_df.index.values))

    return word_freq_df


def tsne(word_freq_df, p, m='cosine'):
    # Perform t-SNE with perplexity p
    z = TSNE(
        n_components=2,
        perplexity=p,
        metric=m
    ).fit_transform(word_freq_df)
    embedding_df = pd.DataFrame(data=z, columns=['t-SNE 1', 't-SNE 2'])
    return embedding_df


def new_node_embedding(original_embedding, word_counts):
    # Where last column is the frequency of the new node
    nn_emb = {'t-SNE 1': 0.0, 't-SNE 2': 0.0}

    # Union words
    word_union = []
    for word_count in word_counts:
        for key in word_count:
            if key not in word_union:
                word_union.append(key)

    # Make frequency matrix
    frequency_matrix = np.zeros((len(word_counts), len(word_union)))
    for i in range(len(word_counts)):
        for j in range(len(word_union)):
            if word_union[j] not in word_counts[i]:
                frequency_matrix[i][j] = 0
            else:
                frequency_matrix[i][j] = word_counts[i].get(word_union[j])

    # Compute cosine similarities to the last row
    cos_sim = cosine_similarity(frequency_matrix[:-1], frequency_matrix[-1].reshape(1, -1))
    func_cos_sim = over_quantile(cos_sim.reshape(1, -1), 0.9)
    nn_emb['t-SNE 1'] = np.sum(original_embedding['t-SNE 1'].tolist() * func_cos_sim) / np.sum(func_cos_sim)
    nn_emb['t-SNE 2'] = np.sum(original_embedding['t-SNE 2'].tolist() * func_cos_sim) / np.sum(func_cos_sim)

    return nn_emb


def over_quantile(x, q):
    quantile = np.quantile(x, q)
    return (x > quantile) * x

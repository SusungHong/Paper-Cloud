import nltk
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.tag import pos_tag
from nltk import Text
from libbmc.citations.pdf import cermine
from tika import parser


def make_union_df(word_counts):
    # Union all words
    # and make them into a dataframe

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

    # Change the matrix into a dataframe
    df = pd.DataFrame(data=frequency_matrix, columns=word_union)
    return df


def count_word(full_text):
    # Count each word in the full text
    # Filter unnecessary words

    counts = dict()
    # Load nltk stop words
    stop_words = set(stopwords.words('english'))    # lookupErr
    # Tokenize the text with a RegexpTokenizer
    word_tokens = RegexpTokenizer(r'[A-Z][A-Z]\w?|[a-zA-Z][a-zA-Z]\w+').tokenize(full_text.replace('-\n', ''))
    # Count
    for word in word_tokens:
        if word.lower() in counts:
            counts[word.lower()] += 1
        elif (word.lower() not in stop_words) & (word.lower() not in ['the', 'on', 'of', 'merely', 'www', 'com', 'every', 'follows', 'without']):
            counts[word.lower()] = 1
    return counts


def extract_text(pdf_path):
    # Extract text from the pdf using tika parser
    extracted = parser.from_file(pdf_path)
    return extracted['content']


def extract_metadata(pdf_path):
    # Extract title, author and abstract from the pdf
    print('Extracting...')
    metadata = {'Title': "", 'Author': "", 'Abstract': ""}
    extracted = cermine(pdf_path, override_local='jars/cermine-impl-1.13-jar-with-dependencies.jar')
    root = ET.fromstring(extracted)
    if root is None:
        return metadata
    for article_meta in root.iter('article-meta'):

        title_group = article_meta.find('title-group')
        if title_group is None:
            metadata['Title'] = pdf_path.split('/')[-1].split('.')[0]
        else:
            metadata['Title'] = title_group.find('article-title').text

        author_list = []
        contrib_group = article_meta.find('contrib-group')
        if contrib_group is not None:
            for contrib in contrib_group.findall('contrib'):
                contrib_type = contrib.get('contrib-type')
                if contrib_type == 'author':
                    string_name = contrib.find('string-name')
                    author_list.append(string_name.text)
        metadata['Author'] = ', '.join(author_list)

        abstract = article_meta.find('abstract')
        if abstract is not None:
            metadata['Abstract'] = abstract.find('p').text
    return metadata

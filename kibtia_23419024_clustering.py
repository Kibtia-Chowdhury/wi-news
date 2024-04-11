# -*- coding: utf-8 -*-
"""Kibtia-23419024_clustering.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1PL7cJhI0m7RLJK3t0v6TsZ5vw42RTK_C

**Install packages**
"""

#install nltk package
!pip install pandas nltk
!python -m spacy download en_core_web_md

#remove annoying warnings from sklearn
def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn

# import all packages
import pandas as pd
import numpy as np
from glob import glob
import string
import re
import nltk
import json
import spacy
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
#from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import StandardScaler, Normalizer
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib.pyplot as plt
#import wikipedia as wiki
from scipy.spatial.distance import cosine

nltk.download('punkt') # downloads the NLTK data for tokenization
nltk.download('stopwords') # downloads the NLTK data for stopwords
nltk.download('wordnet') # downloads the NLTK data for WordNet lemmatizer

"""**Load and Preprocess the Dataset**"""

def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()

    # Remove punctuation
    text = re.sub(r'\d+', '', text)  # Remove numbers
    text = text.translate(str.maketrans('', '', string.punctuation)) # removes punctuation from the text using the translate method

    # Tokenize
    tokens = word_tokenize(text) # tokenizes the text into individual words

    # Remove stopwords
    stop_words = set(stopwords.words('english')) # creates a set of stopwords for English language
    tokens = [w for w in tokens if not w in stop_words] # removes stopwords from the list of tokens

    # Lemmatize
    lemmatizer = WordNetLemmatizer() # creates an instance of the WordNetLemmatizer
    tokens = [lemmatizer.lemmatize(token) for token in tokens] # applies lemmatization to each token in the list
    return ' '.join(tokens)
    #return tokens

# Load the dataset
dataset = pd.read_json('/content/News_Category_Dataset_v3.json', lines=True)

df = pd.DataFrame(dataset)
print(df)
print("\n")
# Preprocess the news headline & short description
df['processed_text'] = df.apply(lambda row: preprocess_text(row['headline'] + " " + row['short_description']), axis=1)
print(df['processed_text'])

import matplotlib.pyplot as plt

# Count the frequency of each category
category_counts = df['category'].value_counts()

# Plot the category distribution
plt.figure(figsize=(12, 6))
plt.bar(category_counts.index, category_counts.values)
plt.xlabel('Category')
plt.ylabel('Count')
plt.title('Distribution of Categories')
plt.xticks(rotation=90)
plt.show()

total_categories = category_counts.nunique()
print("Total number of categories:", total_categories)
category_counts = df['category'].value_counts()
print(category_counts)

"""**Vectorization**"""

import json
from sklearn.feature_extraction.text import CountVectorizer
from gensim.models import Word2Vec

processed_text = df['processed_text'].tolist()

# Word2Vec Vectorization
tokenized_articles = [text.split() for text in processed_text]
word2vec_model = Word2Vec(tokenized_articles, vector_size=100, window=5, min_count=1, workers=4)

document_vector = []
for article in tokenized_articles:
    for word in article:
        if word in word2vec_model.wv.key_to_index:
            document_vector.append(word2vec_model.wv[word])

# Print the word vectors in batches
batch_size = 32
for i in range(0, len(document_vector), batch_size):
    batch_vectors = document_vector[i:i+batch_size]
    print(batch_vectors)

# Alternatively, you can print a subset of word vectors
subset_size = 100
print(document_vector[:subset_size])

"""**Dimensionality Reduction**"""

#Dimensionality Reduction
import numpy as np
from sklearn.decomposition import PCA

document_array = np.array(document_vector)
pca = PCA(n_components=2)
document_pca = pca.fit_transform(document_array)
print(document_pca)

"""**Clustering Algorithm**"""

import numpy as np
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.mixture import GaussianMixture
from sklearn.datasets import make_blobs
from sklearn.preprocessing import StandardScaler
import warnings

# Generate sample data
X, _ = make_blobs(n_samples=100, centers=23, random_state=42)

# Preprocess the data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Check the number of distinct samples in the dataset
unique_samples = np.unique(X_scaled, axis=0)
n_samples = unique_samples.shape[0]

# Check if the number of clusters is valid
n_clusters = 42
if n_clusters > n_samples:
    n_clusters = n_samples

# Disable ConvergenceWarnings for demonstration purposes
warnings.filterwarnings("ignore", category=UserWarning)

# K-means clustering
kmeans = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
kmeans_labels = kmeans.fit_predict(unique_samples)

# Agglomerative clustering
agglomerative = AgglomerativeClustering(n_clusters=n_clusters)
agglomerative_labels = agglomerative.fit_predict(unique_samples)

# GMM clustering
gmm = GaussianMixture(n_components=n_clusters, random_state=42)
gmm.fit(unique_samples)
gmm_labels = gmm.predict(unique_samples)

# Enable ConvergenceWarnings
warnings.filterwarnings("default", category=UserWarning)

# Print the labels assigned by each clustering algorithm
print("K-means labels:", kmeans_labels)
print("Agglomerative labels:", agglomerative_labels)
print("GMM labels:", gmm_labels)

"""**Evaluation of Clustering & Comparison**"""

from sklearn.metrics import calinski_harabasz_score

import matplotlib.pyplot as plt

# Calculate Calinski-Harabasz scores
kmeans_ch_score = calinski_harabasz_score(X_scaled, kmeans_labels)
agglomerative_ch_score = calinski_harabasz_score(X_scaled, agglomerative_labels)
gmm_ch_score = calinski_harabasz_score(X_scaled, gmm_labels)

# Print the Calinski-Harabasz scores
print("K-means Calinski-Harabasz Index:", kmeans_ch_score)
print("Agglomerative Calinski-Harabasz Index:", agglomerative_ch_score)
print("GMM Calinski-Harabasz Index:", gmm_ch_score)

# Plot the clustering results
plt.figure(figsize=(12, 4))

# K-means clustering
plt.subplot(1, 3, 1)
plt.scatter(X_scaled[:, 0], X_scaled[:, 1], c=kmeans_labels)
plt.title("K-means Clustering")

# Agglomerative clustering
plt.subplot(1, 3, 2)
plt.scatter(X_scaled[:, 0], X_scaled[:, 1], c=agglomerative_labels)
plt.title("Agglomerative Clustering")

# GMM clustering
plt.subplot(1, 3, 3)
plt.scatter(X_scaled[:, 0], X_scaled[:, 1], c=gmm_labels)
plt.title("GMM Clustering")

plt.tight_layout()
plt.show()

# Determine the best clustering algorithm based on the Calinski-Harabasz index
best_ch_score = max(kmeans_ch_score, agglomerative_ch_score, gmm_ch_score)
best_algorithm = None

if best_ch_score == kmeans_ch_score:
    best_algorithm = "K-means"
elif best_ch_score == agglomerative_ch_score:
    best_algorithm = "Agglomerative"
else:
    best_algorithm = "GMM"

print("Best Clustering Algorithm based on Calinski-Harabasz Index:", best_algorithm)


from pathlib import Path
import index
import nltk
import json
import math
from queue import PriorityQueue

def search():
    file_path = Path('./index.json')
    documents = index.get_doc_paths()   
    if not Path.is_file(file_path):
        index.build_index(documents)
        index.tfidf(len(documents))
    with open('index.json') as file:
        index = json.load(file)
    query = input()
    #queries = []
    stemmer = nltk.PorterStemmer
    postings = []
    for q in query.split():
        #queries.append(stemmer.stem(q))
        postings.append(index[stemmer.stem(q)])
    ids = PriorityQueue()

    
    

    # figure out what to do with index

def tfidf(N, p, v_len): # not sure if correct
    tf = 1 + math.log(p['y'], 10)
    idf = math.log((N/v_len))
    w = tf * idf
    # p['y'] = w # put here temporarily will prob rename/create new attribute and rebuild index later
    return w

def intersection(l1, l2, N):
    intersection = []
    len1 = len(l1)
    len2 = len(l2)
    l1 = iter(sorted(sorted(l1, key=lambda x: x['id'])))
    l2 = iter(sorted(sorted(l2, key=lambda x: x['id'])))
    p1 = next(l1)
    p2 = next(l2)
    while(True):
        try:
            if p1['id'] < p2['id']:
                p1 = next(l1)
            elif p2['id'] < p1['id']:
                p2 = next(l2)
            elif p1['id'] == p2['id']:
                tfidf = tfidf(N, p1, len1) + tfidf(N, p2, len2)
                intersection.append((p1['id'], tfidf))
        except StopIteration:
            break
    return intersection


from pathlib import Path
import index
import nltk
import json
import math
from queue import PriorityQueue

def search(k):
    file_path = Path('./index.json')
    documents = index.get_doc_paths()   
    if not Path.is_file(file_path):
        index.build_index(documents)
        #index.tfidf(len(documents)) might calculate it for all tokens beforehand instead of during query handling
    with open('index.json') as file:
        index = json.load(file)
    query = input()
    #queries = []
    stemmer = nltk.PorterStemmer
    postings = PriorityQueue()
    for q in query.split():
        #queries.append(stemmer.stem(q))
        # assuming the stem exists will deal with it not existing later
        postings.put(len(index[stemmer.stem(q)]), index[stemmer.stem(q)])
    tfidf = True
    if postings.qsize == 1:
        p = postings.get()
        for i in p:
            w = tfidf(i)
            i['y'] = w
        postings.put(len(p), p)
    while(postings.qsize() > 1):
        l1 = postings.get()
        l2 = postings.get()
        intersection = intersection(l1, l2, tfidf)
        postings.put(len(intersection), intersection)
        tfidf = False
    # assuming there are interesections will deal with there not having any later
    ids = PriorityQueue()
    final = postings.get()
    for id, y in final:
        ids.put(-y, id)
    # get top k results
    results = []
    for _ in range(k):
        id = ids.get()
        results.append(get_doc_url(id))
        if ids.empty():
            break
    for url in results:
        print(url)


def tfidf(N, p, v_len): # not sure if correct
    tf = 1 + math.log(p['y'], 10)
    idf = math.log((N/v_len), 10)
    w = tf * idf
    # p['y'] = w # put here temporarily will prob rename/create new attribute and rebuild index later
    return w

def intersection(l1, l2, N, tfidf=False):
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
                val = dict()
                if tfidf:
                    score = tfidf(N, p1, len1) + tfidf(N, p2, len2)
                else:
                    score = p1['y'] + tfidf(N, p2, len2)
                # score = p1['y'] + p2['y'] if tfidf is calculated beforehand
                val['id'] = p1['id']
                val['y'] = score
                intersection.append(val)
        except StopIteration:
            break
    return intersection

def get_doc_url(documents, id):
    i = id - 1 # because id starts at 1
    doc = documents[i]
    with open(doc, 'r', encoding='utf-8', errors='ignore') as f:
        content = json.load(f)
        if 'url' in content:
            return content['url']
    return ''


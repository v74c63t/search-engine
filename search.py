
from pathlib import Path
import nltk
import json
import math
from queue import PriorityQueue
from index import build_index, sort_and_tfidf, get_doc_paths
from urllib.parse import urldefrag

def input_query():
    queries = input("Please enter your search terms \n >> ")
    words = nltk.tokenize.word_tokenize(queries.lower()) # parse terms into separate queries
    # remove words if not alnum
    return queries, set(word for word in words if word.isalnum()) # decide what do with queries that contain duplicate words later

def load_index(path):
    file_path = Path('./index.json')
    documents = get_doc_paths(path)  
    N = len(documents) 
    if not Path.is_file(file_path):
        build_index(documents)
        #index.tfidf(len(documents)) might calculate it for all tokens beforehand instead of during query handling
        sort_and_tfidf(N)
    with open('index.json') as file:
        index = json.load(file)
    return index, N, documents

def search(documents, index, N, k):
    # file_path = Path('./index.json')
    # documents = get_doc_paths(path)  
    # N = len(documents) 
    # if not Path.is_file(file_path):
    #     build_index(documents)
    #     #index.tfidf(len(documents)) might calculate it for all tokens beforehand instead of during query handling
    #     sort_and_tfidf(N)
    # with open('index.json') as file:
    #     index = json.load(file)
    queries, query = input_query()
    #queries = []
    stemmer = nltk.PorterStemmer()
    postings = PriorityQueue()
    for q in query:
        # print(q)
        #queries.append(stemmer.stem(q))
        # assuming the stem exists will deal with it not existing later
        postings.put((len(index[stemmer.stem(q)]), index[stemmer.stem(q)]))
        #print(len(index[stemmer.stem(q)]))
    # tfidf = True
    # if postings.qsize == 1:
    #     p = postings.get()
    #     for i in p:
    #         w = tfidf(N, i, len(p))
    #         i['y'] = w
    #     postings.put(len(p), p)
    while(postings.qsize() > 1):
        l1 = postings.get()[1]
        # print(l1)
        l2 = postings.get()[1]
        # intersection = intersection(l1, l2, N, tfidf)
        intersection = compute_intersection(l1, l2)
        postings.put((len(intersection), intersection))
        # tfidf = False
    # assuming there are interesections will deal with there not having any later
    ids = PriorityQueue()
    final = postings.get()[1]
    #print(final)
    for d in final:
        ids.put((-d['y'], d['id']))
    # get top k results
    total_results = ids.qsize()
    results = []
    for _ in range(k):
        id = ids.get()[1]
        while(True):
            url = get_doc_url(documents, id)
            if urldefrag(url)[1] != "":
                url = urldefrag(url)[0]
                if url in results:
                    if ids.empty():
                        break
                    id = ids.get()[1]
                else:
                    results.append(url)
                    break
            else:
                if url in results:
                    if ids.empty():
                        break
                    id = ids.get()[1]
                else:
                    results.append(url)
                    break
        # results.append(get_doc_url(documents, id))
        if ids.empty():
            break
    print()
    print(f'Found {total_results} results for {queries}\nReturning top {len(results)} results')
    for url in results:
        print(url)


# def tfidf(N, p, v_len): # not sure if correct
#     tf = 1 + math.log(p['y'], 10)
#     idf = math.log((N/v_len), 10)
#     w = tf * idf
#     # p['y'] = w # put here temporarily will prob rename/create new attribute and rebuild index later
#     return w

# def intersection(l1, l2, N, tfidf=False):
def compute_intersection(l1, l2):
    '''
    finds the intersection between the two lists of postings
    essentially finds documents that belong on both lists and returns postings 
    of those with updated tfidf score
    '''
    intersection = []
    # len1 = len(l1)
    # len2 = len(l2)
    # l1 = iter(sorted(l1, key=lambda x: x['id'])) # might sort after index is built instead of during query handling
    # l2 = iter(sorted(l2, key=lambda x: x['id']))
    i1 = iter(l1)
    i2 = iter(l2)
    p1 = next(i1)
    p2 = next(i2)
    while(True):
        try:
            if p1['id'] < p2['id']:
                p1 = next(i1)
            elif p2['id'] < p1['id']:
                p2 = next(i2)
            elif p1['id'] == p2['id']:
                val = dict()
                # if tfidf:
                #     score = tfidf(N, p1, len1) + tfidf(N, p2, len2)
                # else:
                #     score = p1['y'] + tfidf(N, p2, len2)
                score = p1['y'] + p2['y'] #if tfidf is calculated beforehand
                val['id'] = p1['id']
                val['y'] = score
                intersection.append(val)
                p1 = next(i1)
                p2 = next(i2)
        except StopIteration:
            break
    return intersection

def get_doc_url(documents, id):
    '''
    gets the doc url from a list of document paths given a document id
    '''
    i = id - 1 # because id starts at 1
    doc = documents[i]
    with open(doc, 'r', encoding='utf-8', errors='ignore') as f:
        content = json.load(f)
        if 'url' in content:
            return content['url']
    return ''

def main():
    index, N, documents = load_index("./DEV")
    user_input = ''
    while(True):
        user_input = input("Press the enter key to continue or input quit to exit: ")
        if user_input == 'quit': break
        print()
        search(documents, index, N, 5)
        # print(input_query())
        # # user_input = input("Press Enter to continue or input quit() to exit")
        # print(user_input)


if __name__ == "__main__":
    main()
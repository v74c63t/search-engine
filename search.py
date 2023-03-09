
from pathlib import Path
import nltk
import json
import math
from queue import PriorityQueue
from index import build_index, sort_and_tfidf, get_doc_paths
from urllib.parse import urldefrag
import time
from nltk.corpus import stopwords

def input_query():
    queries = input("Please enter your search query \n  >> ")
    start = time.time()
    words = nltk.tokenize.word_tokenize(queries.lower()) # parse terms into separate queries
    stemmer = nltk.PorterStemmer()
    stops = set(stopwords.words('english'))
    non_parsed = []
    parsed = []
    for word in words:
        if word.isalnum():
            if word in stops:
                non_parsed.append(stemmer.stem(word))
            else:
                parsed.append(stemmer.stem(word))
                non_parsed.append(parsed[-1])
    if non_parsed != []:
        if len(parsed)/len(non_parsed) < 0.5:
            return queries, non_parsed, start
        else:
            return queries, parsed, start
    else:
        return queries, non_parsed, start
    # remove words if not alnum
    # stemmer = nltk.PorterStemmer()
    # return queries, [stemmer.stem(word) for word in words if word.isalnum()], start

def load_index():
    # file_path = Path('./index.json')
    with open('doc_url.json', 'r') as file:
        documents = json.load(file) 
    N = len(documents.keys()) 
    # if not Path.is_file(file_path):
    #     build_index(documents)
    #     #index.tfidf(len(documents)) might calculate it for all tokens beforehand instead of during query handling
    #     sort_and_tfidf(N)
    # with open('index.json') as file:
    #     index = json.load(file)
    with open('index_pos.json') as file:
        index_pos = json.load(file)
    return index_pos, N, documents

def get_query_tfidf(query, N, df_dict):
    query_tfidf = dict()
    # stemmer = nltk.PorterStemmer()
    # # query_len = len(query)
    # query = [stemmer.stem(q) for q in query]
    parsed = set(query)
    for p in parsed:
        freq = 0
        for q in query:
            if p == q:
                freq+=1
        tf = 1 + math.log(freq, 10)
        idf = math.log(N/df_dict[p])
        score = tf*idf
        query_tfidf[p] = score
    return query_tfidf

def search(documents, index_pos, N, k):
    # file_path = Path('./index.json')
    # documents = get_doc_paths(path)  
    # N = len(documents) 
    # if not Path.is_file(file_path):
    #     build_index(documents)
    #     #index.tfidf(len(documents)) might calculate it for all tokens beforehand instead of during query handling
    #     sort_and_tfidf(N)
    # with open('index.json') as file:
    #     index = json.load(file)
    queries, query, start = input_query()
    if len(query) == 0:
        print()
        print(f'Found 0 results for {queries}.')
        print((time.time()-start)* 10**3, 'ms')
        print() 
        return
    # original = query
    query = set(query)
    #queries = []
    # stemmer = nltk.PorterStemmer()
    postings = PriorityQueue()
    try:
        # df=dict()
        # i = 0
        with open('index.json') as file:
            for q in query:
                pos = index_pos[q]
                file.seek(pos)
                index = file.readline()
                index = index[:-3]
                if index[-1] != ']':
                    index += '}]}'
                else:
                    index += '}'
                if index[0] != '{':
                    index = '{' + index
                index = json.loads(index)
                p = index[q]
                q_len = len(p)
                postings.put((q_len, p))
                index.clear()
        # for q in query:
        # while i < len(query):
        #     q = query[i]
        #     #queries.append(stemmer.stem(q))
        #     # put posting list and length into priority queue so smaller lists will be checked first
        #     pos, lines = index_pos[q[0]]
        #     with open('index.json') as file:
        #         file.seek(pos)
        #         index = ""
        #         for _ in range(lines):
        #             index += file.readline()
        #         index = index[:-3]
        #         if index[-1] != ']':
        #             index += '}]}'
        #         else:
        #             index += '}'
        #         if index[0] != '{':
        #             index = '{' + index
        #     index = json.loads(index)
        #     while True:    
        #         p = index[q]
        #         q_len = len(p)
        #         postings.put((q_len, p))
        #         # df[q] = q_len
        #         i += 1
        #         if i < len(query):
        #             if query[i][0] != query[i-1][0]:
        #                 break
        #         else:
        #             break
        #     index.clear()
        # query_tfidf = get_query_tfidf(original, N, df)
        # df.clear()
            #print(len(index[stemmer.stem(q)]))
        # tfidf = True
        # if postings.qsize == 1:
        #     p = postings.get()
        #     for i in p:
        #         w = tfidf(N, i, len(p))
        #         i['y'] = w
        #     postings.put(len(p), p)
        #more  than one word in query
        while(postings.qsize() > 1):
            l1 = postings.get()[1]
            # print(l1)
            l2 = postings.get()[1]
            # intersection = intersection(l1, l2, N, tfidf)
            # get intersection of all words in query (the documents that contain all the words in query)
            intersection = compute_intersection(l1, l2)
            postings.put((len(intersection), intersection))
            # tfidf = False
        # assuming there are interesections will deal with there not having any later
        ids = PriorityQueue()
        final = postings.get()
        size = final[0]
        if size == 0:
            # no interesection/no document that contains all words
            print()
            print(f'Found 0 results for {queries}.')
            print((time.time()-start)* 10**3, 'ms')
            print()
            return
        final = final[1]
        #print(final)
        for d in final:
            # put into priority queue with score 
            # have to use -score so the highest score will be popped first
            ids.put((-d['y'], d['id']))
        # get top k results
        total_results = ids.qsize()
        results = []
        for _ in range(k):
            id = ids.get()[1]
            # while(True):
            #     # make sure no fragements/duplicates
            #     # url = get_doc_url(documents, id)
            #     url = documents[str(id)]
            #     if urldefrag(url)[1] != "":
            #         url = urldefrag(url)[0]
            #         if url in results:
            #             if ids.empty():
            #                 break
            #             id = ids.get()[1]
            #         else:
            #             results.append(url)
            #             break
            #     else:
            #         if url in results:
            #             if ids.empty():
            #                 break
            #             id = ids.get()[1]
            #         else:
            #             results.append(url)
            #             break
            results.append(documents[str(id)])
            # results.append(get_doc_url(documents, id))
            if ids.empty():
                break
        print()
        print(f'Found {total_results} results for {queries}. Returning top {len(results)} results...')
        for url in results:
            print(url)
        print((time.time()-start)* 10**3, 'ms')
        print()
    except(KeyError):
        print()
        print(f'Found 0 results for {queries}.')
        print((time.time()-start)* 10**3, 'ms')
        print()


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

def cosine(q, d):
    return

# def get_doc_url(documents, id):
#     '''
#     gets the doc url from a list of document paths given a document id
#     '''
#     i = id - 1 # because id starts at 1
#     doc = documents[i]
#     with open(doc, 'r', encoding='utf-8', errors='ignore') as f:
#         content = json.load(f)
#         if 'url' in content:
#             return content['url']
#     return ''

def main():
    index_pos, N, documents = load_index()
    while(True):
        user_input = input("Press the enter key to continue or input quit to exit: ")
        if user_input == 'quit': break
        print()
        search(documents, index_pos, N, 5)
        # print(input_query())
        # # user_input = input("Press Enter to continue or input quit() to exit")
        # print(user_input)
    documents.clear()
    index_pos.clear()


if __name__ == "__main__":
    main()
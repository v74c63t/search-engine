
from pathlib import Path
import nltk
import json
from queue import PriorityQueue
import time
from nltk.corpus import stopwords
import unicodedata
from collections import defaultdict

def input_query(HTMLq):
    # if HTMLq == None:
    #     queries = input("Please enter your search query \n  >> ")
    queries = HTMLq
    start = time.time()
    words = nltk.tokenize.word_tokenize(queries.lower()) # parse terms into separate queries
    stemmer = nltk.PorterStemmer()
    stops = set(stopwords.words('english'))
    stop = set()
    non_parsed = set()
    parsed = set()
    for word in words:
        if word.isalnum():
            stem = stemmer.stem(unicodedata.normalize('NFKD', word).encode('ascii', errors='ignore').decode())
            if word in stops:
                non_parsed.add(stem)
                stop.add(stem)
            else:
                parsed.add(stem)
                non_parsed.add(stem)
    # ideas if more than a certain amt of stop words jus remove them sort by len then remove?
    if non_parsed != set():
        if len(parsed)/len(non_parsed) < 0.3:
            if len(stop) > 5:
                print()
                stop = sorted(stop, key=lambda x: len(x), reverse=True)
                parsed.update(stop[0:5])
                return queries, parsed, start
            else:
                return queries, non_parsed, start
        else:
            if len(stop) > 5:
                print()
                stop = sorted(stop, key=lambda x: len(x), reverse=True)
                parsed.update(stop[:5])
            return queries, parsed, start
    else:
        return queries, non_parsed, start
    # remove words if not alnum
    # stemmer = nltk.PorterStemmer()
    # return queries, [stemmer.stem(word) for word in words if word.isalnum()], start

def load_index():
    with open('doc_url.json', 'r') as file:
        documents = json.load(file) 
    N = len(documents.keys()) 
    with open('index_pos.json') as file:
        index_pos = json.load(file)
    return index_pos, N, documents

# def term_at_time_retr(documents, index_pos, k, query):
def search(documents, index_pos, k, HTMLq):
    queries, query, start = input_query(HTMLq)
    if len(query) == 0:
    # print()
    # print(f'Found 0 results for {queries}.')
    # print((time.time()-start)* 10**3, 'ms')
    # print() 
        ntime = (time.time()-start)* 10**3
        print()
        return [], ntime
    query = sorted(query)
    # print(query)
    score = defaultdict(int)
    posting_lists = []
    rank = PriorityQueue()
    try:
        # if p == None:
        with open('index.json') as file:
            for q in query:
                try:
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
                    # posting = index[q]
                    # q_len = len(posting)
                    # postings.put((q_len, posting))
                    posting_lists.append(index[q])
                    index.clear()
                except(KeyError):
                    continue
        # else:
        #     for posting in p:
        #         postings.put((len(posting),p))
        if len(posting_lists) == 0:
            # print()
            # print(f'Found 0 results for {queries}.')
            # print((time.time()-start)* 10**3, 'ms')
            # print() 
            ntime = (time.time()-start)* 10**3
            print()
            return [], ntime
        for posting_list in posting_lists:
            for posting in posting_list:
                score[posting['id']] += posting['y']
        for id, y in score.items():
            rank.put((-y, id))
        results = []
        for _ in range(k):
            id = rank.get()[1]
            results.append(documents[str(id)])
            if rank.empty():
                break
        ntime = (time.time()-start)* 10**3
        print()
        return results, ntime
        # return results
    except(KeyError):
        # print()
        # print(f'Found 0 results for {queries}.')
        # print((time.time()-start)* 10**3, 'ms')
        # print()
        ntime = (time.time()-start)* 10**3
        print()
        return [], ntime

# def search(documents, index_pos, N, k):
# def search(documents, index_pos, k, p=None, query=None):
# def old_search(documents, index_pos, k, query):
#     # queries, query, start = input_query()
#     # if query != None:
#     if len(query) == 0:
#         # print()
#         # print(f'Found 0 results for {queries}.')
#         # print((time.time()-start)* 10**3, 'ms')
#         # print() 
#         return []
#     query = set(query)
#     postings = PriorityQueue()
#     try:
#         # if p == None:
#         with open('index.json') as file:
#             for q in query:
#                 try:
#                     pos = index_pos[q]
#                     file.seek(pos)
#                     index = file.readline()
#                     index = index[:-3]
#                     if index[-1] != ']':
#                         index += '}]}'
#                     else:
#                         index += '}'
#                     if index[0] != '{':
#                         index = '{' + index
#                     index = json.loads(index)
#                     posting = index[q]
#                     q_len = len(posting)
#                     postings.put((q_len, posting))
#                     index.clear()
#                 except(KeyError):
#                     continue
#         # else:
#         #     for posting in p:
#         #         postings.put((len(posting),p))
#         if postings.qsize() == 0:
#             # print()
#             # print(f'Found 0 results for {queries}.')
#             # print((time.time()-start)* 10**3, 'ms')
#             # print() 
#             return []
#         #more  than one word in query
#         while(postings.qsize() > 1):
#             l1 = postings.get()[1]
#             l2 = postings.get()[1]
#             # intersection = intersection(l1, l2, N, tfidf)
#             # get intersection of all words in query (the documents that contain all the words in query)
#             intersection = compute_intersection(l1, l2)
#             postings.put((len(intersection), intersection))
#             # tfidf = False
#         # assuming there are interesections will deal with there not having any later
#         ids = PriorityQueue()
#         final = postings.get()
#         size = final[0]
#         if size == 0:
#             # no interesection/no document that contains all words
#             # print()
#             # print(f'Found 0 results for {queries}.')
#             # print((time.time()-start)* 10**3, 'ms')
#             # print()
#             return []
#         final = final[1]
#         #print(final)
#         for d in final:
#             # put into priority queue with score 
#             # have to use -score so the highest score will be popped first
#             ids.put((-d['y'], d['id']))
#         # get top k results
#         # total_results = ids.qsize()
#         results = []
#         for _ in range(k):
#             id = ids.get()[1]
#             results.append(documents[str(id)])
#             if ids.empty():
#                 break
#         # print()
#         # print(f'Found {total_results} results for {queries}. Returning top {len(results)} results...')
#         # for url in results:
#         #     print(url)
#         # print((time.time()-start)* 10**3, 'ms')
#         # print()
#         return results
#     except(KeyError):
#         # print()
#         # print(f'Found 0 results for {queries}.')
#         # print((time.time()-start)* 10**3, 'ms')
#         # print()
#         return []

# def get_results(documents, index_pos, k):
#     # queries, query, start = input_query()
#     # results = old_search(documents, index_pos, k, query)
#     results = search(documents, index_pos, k)
#     # i = len(query)-1
#     # # sort = []
#     # if len(results) < k:   
#     #     p_len = dict()
#     #     with open('index.json') as file:
#     #         for q in query:
#     #             try:
#     #                 pos = index_pos[q]
#     #                 file.seek(pos)
#     #                 index = file.readline()
#     #                 index = index[:-3]
#     #                 if index[-1] != ']':
#     #                     index += '}]}'
#     #                 else:
#     #                     index += '}'
#     #                 if index[0] != '{':
#     #                     index = '{' + index
#     #                 index = json.loads(index)
#     #                 p_len[q] = len(index[q])
#     #                 # print(type(index[q]), len(index[q]))
#     #                 # postings.append(index[q])
#     #                 # print(len(postings))
#     #                 index.clear()
#     #             except(KeyError):
#     #                 continue
#     #     sort = sorted(query, key=lambda x: p_len[x], reverse=True)
#     #     # print(len(sort))
#     #     while len(results) < k or i >= 0:
#     #         parse = sort[:i]
#     #         if i < len(sort)-1:
#     #             parse += sort[i+1:]
#     #         results += search(documents, index_pos, k-len(results), parse)
#     #         i -= 1
#     print()
#     print(f'For query: {queries} returning top {len(results)} results...')
#     end = (time.time() - start) * 10**3
#     for url in results:
#         print(url)
#     print((time.time()-start)* 10**3, 'ms')
#     print(end, 'ms')
#     print()


# def tfidf(N, p, v_len): # not sure if correct
#     tf = 1 + math.log(p['y'], 10)
#     idf = math.log((N/v_len), 10)
#     w = tf * idf
#     # p['y'] = w # put here temporarily will prob rename/create new attribute and rebuild index later
#     return w

# def intersection(l1, l2, N, tfidf=False):
# def compute_intersection(l1, l2):
#     '''
#     finds the intersection between the two lists of postings
#     essentially finds documents that belong on both lists and returns postings 
#     of those with updated tfidf score
#     '''
#     intersection = []
#     # len1 = len(l1)
#     # len2 = len(l2)
#     # l1 = iter(sorted(l1, key=lambda x: x['id'])) # might sort after index is built instead of during query handling
#     # l2 = iter(sorted(l2, key=lambda x: x['id']))
#     if(len(l1) == 0 or len(l2) == 0):
#         return intersection
#     i1 = iter(l1)
#     i2 = iter(l2)
#     p1 = next(i1)
#     p2 = next(i2)
#     while(True):
#         try:
#             if p1['id'] < p2['id']:
#                 p1 = next(i1)
#             elif p2['id'] < p1['id']:
#                 p2 = next(i2)
#             elif p1['id'] == p2['id']:
#                 val = dict()
#                 # if tfidf:
#                 #     score = tfidf(N, p1, len1) + tfidf(N, p2, len2)
#                 # else:
#                 #     score = p1['y'] + tfidf(N, p2, len2)
#                 score = p1['y'] + p2['y'] #if tfidf is calculated beforehand
#                 val['id'] = p1['id']
#                 val['y'] = score
#                 intersection.append(val)
#                 p1 = next(i1)
#                 p2 = next(i2)
#         except StopIteration:
#             break
#     return intersection

# def main():
#     index_pos, N, documents = load_index()
#     while(True):
#         user_input = input("Press the enter key to continue or input quit to exit: ")
#         if user_input == 'quit': break
#         print()
#         # search(documents, index_pos, N, 5)
#         get_results(documents, index_pos, 5)
#         # print(input_query())
#         # # user_input = input("Press Enter to continue or input quit() to exit")
#         # print(user_input)
#     # documents.clear()
#     # index_pos.clear()


# if __name__ == "__main__":
#     main()
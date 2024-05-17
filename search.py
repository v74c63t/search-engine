
import nltk
nltk.download('stopwords')
import json
from queue import PriorityQueue
import time
from nltk.corpus import stopwords
import unicodedata
from collections import defaultdict

def input_query(HTMLq: str) -> tuple[set, float]:
    '''
    the function takes a query and make changes/parses it so it can be 
    be used to retrieve documents from the index

    HTMLq: the query string received from the gui

    the function returns a set of the parsed words in the query and
    the time at which it receive the query so it can later be used
    to calculate the query response time
    '''
    queries = HTMLq
    # we save the time that we received the query
    start = time.time()
    # the query is parsed into separate words
    words = nltk.tokenize.word_tokenize(queries.lower())
    stemmer = nltk.PorterStemmer()
    stops = set(stopwords.words('english'))
    stop = set()
    non_parsed = set()
    parsed = set()
    for word in words:
        # this will only check for documents if the word is alphanumeric
        if word.isalnum():
            # the word is stemmed and have unicode characters replaced if there are any
            stem = stemmer.stem(unicodedata.normalize('NFKD', word).encode('ascii', errors='ignore').decode())
            # we keep two sets non_parsed, simply a set of the words in the query without duplicates, and
            # parsed, a set of the words in the query without the stop words and duplicates  
            if word in stops:
                non_parsed.add(stem)
                stop.add(stem)
            else:
                parsed.add(stem)
                non_parsed.add(stem)
    if non_parsed != set():
        # if more than 70% of the query consists of stop words, we will consider them in our search
        if len(parsed)/len(non_parsed) < 0.3:
            # however we only consider 5 stop words before removing all of the rest
            if len(stop) > 5:
                # we will only take the first 5 longest stop words 
                # because typically shorter stop words are used more often
                # and contribute not that much 
                stop = sorted(stop, key=lambda x: len(x), reverse=True)
                parsed.update(stop[0:5])
                return parsed, start
            else:
                return non_parsed, start
        else:
            if len(stop) > 5:
                stop = sorted(stop, key=lambda x: len(x), reverse=True)
                parsed.update(stop[0:5])
            return parsed, start
    else:
        return non_parsed, start

def load_index() -> tuple[dict, dict]:
    '''
    this loads the document to url dictionary and the index 
    word to file position dictionary and return them so it can be
    used during retrieval 
    '''
    with open('doc_url_dev.json', 'r') as file:
        documents = json.load(file) 
    # N = len(documents.keys()) 
    with open('indexes/index_of_index.json') as file:
        index_of_index = json.load(file)
    return index_of_index, documents 

def search(documents: dict, index_of_index: dict, k: int, HTMLq: str) -> tuple[list, float]:
    '''
    this is essentially term at a time retrieval
    it gets all the postings for each word from the index file
    and returns the top k results based on their weight score
    and the time it took for the query response

    documents: the dictionary that maps document ids to document urls
    index_of_index: the dictionary that maps words to their position in the index file
    k: the top number of urls to be returned
    HTMLq: the query obtained from the input field of the gui

    returns
    results: list top k of urls
    ntime: the time the query response took
    '''
    query, start = input_query(HTMLq)
    if len(query) == 0:
        ntime = (time.time()-start)* 10**3
        return [], ntime
    score = defaultdict(int)
    posting_lists = []
    rank = PriorityQueue()
    try:
        with open('indexes/final_index.json') as file:
            for q in query:
                try:
                    # we try to find the position that the word 
                    # is in in the index file and use seek() and
                    # readline() to get the posting list  
                    pos = index_of_index[q]
                    file.seek(pos)
                    index = file.readline()
                    # we have to make sure the format is correct so
                    # it can be correctly loaded by json.loads()  
                    index = index[:-3]
                    if index[-1] != ']':
                        index += '}]}'
                    else:
                        index += '}'
                    if index[0] != '{':
                        index = '{' + index
                    index = json.loads(index)
                    posting_lists.append(index[q])
                    # the index is cleared after each query
                    index.clear()
                except(KeyError):
                    # if the word does not exist in the index 
                    # we simply skip it 
                    continue
        if len(posting_lists) == 0:
            ntime = (time.time()-start)* 10**3
            print()
            return [], ntime
        # we then go through all the postings and add their score 
        # to a dictionary with the keys being the document id 
        # and the value being the score of the document 
        # if two words in the query appear in the same document
        # the scores of both postings are added to together   
        for posting_list in posting_lists:
            for posting in posting_list:
                score[posting['id']] += posting['y']
        # we then plan it in a priority queue once all the scores 
        # have been calculated (we have to use -y so it properly
        # pops out the document with the highest score first) 
        for id, y in score.items():
            rank.put((-y, id))
        results = []
        # we then return the top k urls if possible
        # we pop ids from the priority queue and find their 
        # respective url and add it to a list until k urls are
        # added or until there are no more items in the queue  
        for _ in range(k):
            id = rank.get()[1]
            results.append(documents[str(id)])
            if rank.empty():
                break
        ntime = (time.time()-start)* 10**3
        # we then return the results and the time it took to
        # retrieve these results 
        return results, ntime
    except(KeyError):
        ntime = (time.time()-start)* 10**3
        return [], ntime
from collections import defaultdict
from bs4 import BeautifulSoup
import nltk
import os
import json
import lxml
from json import JSONEncoder
# from reportM1 import report
from pathlib import Path
import math
# debating whether to use this
import unicodedata
from urllib.parse import urldefrag

def build_index(documents):
    # index is a defaultdict with keys of strings and values of Posting lists 
    index = defaultdict(list)
    # we get all the paths of the files inside the DEV folder
    # documents = get_doc_paths(path)
    id = 0
    # we will read and parse the documents in batches of 1000 until there are no documents left
    batch_size = 1000
    urls = dict()
    while len(documents) != 0:
        print(len(documents))
        batch = documents[0:batch_size]
        documents = documents[batch_size:]
        for b in batch:
            id+=1
            with open(b, 'r', encoding='utf-8', errors='ignore') as f:
                content = json.load(f)
                url = urldefrag(content['url'])[0]
                if url in urls.values():
                    id-=1
                    continue
                urls[id] = url
                if 'content' in content:
                    content = content['content']
                    # we get the text content of the file with BeautifulSoup
                    soup = BeautifulSoup(content, 'html.parser')# get text 
                    text = soup.get_text(' ')
                    # we parse the text with nltk
                    tokens = nltk.tokenize.word_tokenize(text.lower())# parse (nltk)
                    for t in tokens:
                        # debating whether to use this
                        #norm = unicodedata.normalize('NFKD', t).encode('ascii', errors='ignore').decode()
                        # we port stem the word before it is added to the index
                        stemmer = nltk.PorterStemmer()
                        stem = stemmer.stem(unicodedata.normalize('NFKD', t).encode('ascii', errors='ignore').decode())#port stem(t) (look at nltk)
                        # as long as the word is alphanumeric it is added to the index
                        if(stem.isalnum() and stem != ""):
                            if index[stem] == []: 
                                # if there is no value associated with the word, we append a posting for that document
                                index[stem].append(Posting(id))
                            elif index[stem][-1].get_doc_id() == id: 
                                # if the previous posting for that word is for this document which we check by comparing
                                # the document ids, we add to the frequency count
                                index[stem][-1].add_count()
                            else:
                                # if there is a value associated with the word and the previous posting is not for this
                                # document, we just append a new posting for the document at the end of the list 
                                index[stem].append(Posting(id))
                    # check for importance
                    # find all words with important tags and add weights to them
                    # first find all text with certain tags
                    # then tokenize the text in those tags
                    # and find it in index to add weights to self.f
                    # importance: title > h1 > h2 = h3 > strong = b
                    importance = set(stemmer.stem(unicodedata.normalize('NFKD', word).encode('ascii', errors='ignore').decode()) 
                                     for title in soup.find_all('title') 
                                     for word in nltk.tokenize.word_tokenize(title.get_text(' ').strip().lower()) if word.isalnum() and word != "") 
                    for title in importance:
                        try:index[title][-1].importance('title')
                        except(IndexError): continue
                    importance = set(stemmer.stem(unicodedata.normalize('NFKD', word).encode('ascii', errors='ignore').decode()) 
                                     for h1 in soup.find_all('h1') 
                                     for word in nltk.tokenize.word_tokenize(h1.get_text(' ').strip().lower()) if word.isalnum() and word != "") 
                    for h1 in importance:
                        try:index[h1][-1].importance('h1')
                        except(IndexError): continue
                    importance = set(stemmer.stem(unicodedata.normalize('NFKD', word).encode('ascii', errors='ignore').decode()) 
                                     for h2 in soup.find_all('h2') 
                                     for word in nltk.tokenize.word_tokenize(h2.get_text(' ').strip().lower()) if word.isalnum() and word != "") 
                    for h2 in importance:
                        try:index[h2][-1].importance('h2')
                        except(IndexError): continue
                    importance = set(stemmer.stem(unicodedata.normalize('NFKD', word).encode('ascii', errors='ignore').decode()) 
                                     for h3_or_bold in soup.find_all(['h3','strong', 'b']) 
                                     for word in nltk.tokenize.word_tokenize(h3_or_bold.get_text(' ').strip().lower()) if word.isalnum() and word != "") 
                    for h3_or_bold in importance:
                        try:index[h3_or_bold][-1].importance('h3/strong/b')
                        except(IndexError): continue

        # we save to disk using json dump and json load
        file_path = Path('./index.json')
        # if an index.json file does not already exist, there is no partial index we need to load and merge with the current
        # index so we simply just create an index.json file to dump the index     
        if not Path.is_file(file_path):
            with open('index.json', 'w') as file:
                json.dump(index, file, cls=PostingEncoder)
        # if an index.json file does exist, we have to load the partial index from the file and merge it with the current index
        # before overwriting the file and dumping it back into the file     
        else:
            with open('index.json') as file:
                data = json.load(file)
            # we merge the index by adding the values together if the keys are the same
            for k, v in index.items():
                try:
                    data[k] += v
                except(KeyError):
                    data[k] = v
            with open('index.json', 'w') as file:
                json.dump(data, file, cls=PostingEncoder)
        # we empty out the index before continuing onto the next batch of documents
        index.clear()
    with open('doc_url.json', 'w') as file:
        json.dump(urls, file)
    #report(id)
    sort_and_tfidf(len(urls.keys()))
    urls.clear()
    return

def get_doc_paths(path):
    '''
    get all the documents paths in a folder so it can be accessed later
    '''
    documents = []
     #for root, _, files in os.walk("DEV/"):
    for root, _, files in os.walk(Path(path)):
        for name in files:
            if name.endswith((".json")): 
                documents.append(root+'/'+name)
    return documents

# may change it to be implemented during build index
def doc_url_file(documents):
    id = 0
    urls = dict()
    for doc in documents:
        id+=1
        with open(doc, 'r', encoding='utf-8', errors='ignore') as f:
            content = json.load(f)
            # urls[id] = content['url']
            url = urldefrag(content['url'])[0]
            if url in urls.values():
                id -=1
                continue
            urls[id] = url
        
    with open('doc_url.json', 'w') as file:
        json.dump(urls, file)

def sort_and_tfidf(N): # not sure if correct
    '''
    sorts the keys alphabetically
    sorts the values by doc_id
    calculates the tfidf for each term-doc pair
    writes each term-list of postings pair to a newline
    '''
    with open('index.json') as file:
        index = json.load(file)
    for _, v in index.items():
        v_len = len(v)
        for p in v:
            tf = 1 + math.log(p["y"], 10)
            idf = math.log((N/v_len), 10)
            w = tf * idf
            if p["f"] != 0:
                #not sure yet
                w *= p['f']
            p['y'] = w 
        # # sort by tfidf
        # index[k] = sorted(v, key=lambda x: x['y'], reverse=True)
        # index[k] = sorted(v, key=lambda x: x['id']) # sort by doc_id
    with open('index.json', 'w') as file:
        alphabetical = json.dumps(index, cls=PostingEncoder, sort_keys=True).replace('], ', '], \n') # sort alphabetically/puts each key-val pair on new line
        index.clear()
        #json.dump(index, file, cls=PostingEncoder)
        file.write(alphabetical)

# def index_pos():
#     # temp might change
#     c = '0'
#     pos = 0
#     index_pos = dict()
#     index_pos[c] = 0
#     with open('index.json') as file:
#         next_c = chr(ord(c) + 1)
#         line = ""
#         while next_c <= 'z':
#             lines = 1
#             line = file.readline()
#             while(line != ""):
#                 lines += 1
#                 if line[1:].startswith(next_c):
#                     index_pos[c] = (index_pos[c], lines-1) # position, num of lines
#                     index_pos[next_c] = pos
#                     pos += len(line)
#                     c = next_c
#                     if next_c == '9':
#                         next_c = 'a'
#                         break
#                     else:
#                         next_c = chr(ord(c) + 1)
#                         break
#                 else:
#                     pos += len(line)
#                 line = file.readline()
#             if line == "":
#                 if type(index_pos[c]) != tuple:
#                     index_pos[c] = (index_pos[c], lines)
#                 else:
#                     index_pos[next_c] = (index_pos[next_c], lines)
#         if line != "":
#             lines = 1
#             line = file.readline()
#             while(line != ""):
#                 lines += 1
#                 line = file.readline()
#             index_pos[c] = (index_pos[c], lines)
#     with open('index_pos.json', 'w') as file:
#         json.dump(index_pos, file)

def index_pos():
    # temp might change
    pos = 0
    index_pos = dict()
    with open('index.json') as file:
        line = file.readline()
        if line != "":
            i = line.find('":')
            word = line[2:i]
            index_pos[word] = pos
            pos += len(line)
        line = file.readline()
        while line != "":
            i = line.find('":')
            word = line[1:i]
            index_pos[word] = pos
            pos += len(line)
            line = file.readline()
    with open('index_pos.json', 'w') as file:
        json.dump(index_pos, file)



class Posting():
    # the posting class contain the document id and the frequency count of the word in that document
    def __init__(self, doc_id):
        self.id = doc_id
        self.y = 1 # term freq / will turn into tfidf later
        # self.f = defaultdict(int) not sure yet will prob give title, h, strong weights depends 3,2,1?
        self.f = 0 
    def add_count(self):
        self.y+=1
    def get_doc_id(self): 
        return self.id
    def importance(self, field):
        #not sure yet
        if field == 'title':
            self.f += 5
        elif field == 'h1':
            self.f += 4
        elif field == 'h2':
            self.f += 3
        elif field == 'h3/strong/b':
            self.f += 2
    # or just add count

# this class ensures that a Posting class object can be dumped into a json file
class PostingEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


# if __name__ == "__main__":
#     index_pos()
    # build_index(get_doc_paths('./DEV'))
    # doc_url_file(get_doc_paths('./DEV'))
    # sort_and_tfidf(53792)

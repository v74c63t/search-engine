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

def build_index(documents):
    # index is a defaultdict with keys of strings and values of Posting lists 
    index = defaultdict(list)
    # we get all the paths of the files inside the DEV folder
    # documents = get_doc_paths(path)
    id = 0
    # we will read and parse the documents in batches of 1000 until there are no documents left
    batch_size = 1000
    while len(documents) != 0:
        #print(len(documents))
        batch = documents[0:batch_size]
        documents = documents[batch_size:]
        for b in batch:
            id+=1
            with open(b, 'r', encoding='utf-8', errors='ignore') as f:
                content = json.load(f)
                if 'content' in content:
                    content = content['content']
                    # we get the text content of the file with BeautifulSoup
                    soup = BeautifulSoup(content, 'html.parser')# get text 
                    text = soup.get_text(' ')
                    # we parse the text with nltk
                    tokens = nltk.tokenize.word_tokenize(text.lower())# parse (nltk)
                    for t in tokens:
                        # we port stem the word before it is added to the index
                        stemmer = nltk.PorterStemmer()
                        stem = stemmer.stem(t)#port stem(t) (look at nltk)
                        # as long as the word is alphanumeric it is added to the index
                        if(stem.isalnum()):
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
                    importance = set(stemmer.stem(word) for title in soup.find_all('title') 
                                     for word in nltk.tokenize.word_tokenize(title.text.strip().lower()) if word.isalnum()) 
                    for title in importance:
                        index[title][-1].importance('title')
                    importance = set(stemmer.stem(h1.text.strip()) for h1 in soup.find_all('h1'))
                    importance = set(stemmer.stem(word) for h1 in soup.find_all('h1') 
                                     for word in nltk.tokenize.word_tokenize(h1.text.strip().lower()) if word.isalnum()) 
                    for h1 in importance:
                        index[h1][-1].importance('h1')
                    importance = set(stemmer.stem(word) for h2_or_h3 in soup.find_all(['h2', 'h3']) 
                                     for word in nltk.tokenize.word_tokenize(h2_or_h3.text.strip().lower()) if word.isalnum()) 
                    for h2_or_h3 in importance:
                        index[h2_or_h3][-1].importance('h2/h3')
                    importance = set(stemmer.stem(word) for bold in soup.find_all(['strong', 'b']) 
                                     for word in nltk.tokenize.word_tokenize(bold.text.strip().lower()) if word.isalnum()) 
                    for bold in importance:
                        index[bold][-1].importance('strong/b')

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
                data[k] += v
            with open('index.json', 'w') as file:
                json.dump(data, file, cls=PostingEncoder)
        # we empty out the index before continuing onto the next batch of documents
        index.clear()
    #report(id)
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
    id = 1
    urls = dict()
    for doc in documents:
        with open(doc, 'r', encoding='utf-8', errors='ignore') as f:
            content = json.load(f)
            urls[id] = content['url']
        id+=1
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
    for k, v in index.items():
        v_len = len(v)
        for p in v:
            tf = 1 + math.log(p['y'], 10)
            idf = math.log((N/v_len), 10)
            w = tf * idf
            if p['f'] != 0:
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
        elif field == 'h2/h3':
            self.f += 3
        elif field == 'strong/b':
            self.f += 2
    # or just add count

# this class ensures that a Posting class object can be dumped into a json file
class PostingEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


# if __name__ == "__main__":
#     # build_index(get_doc_paths('./DEV'))
#     doc_url_file(get_doc_paths('./DEV'))

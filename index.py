from collections import defaultdict
from bs4 import BeautifulSoup
import nltk
import os
import json
from json import JSONEncoder
from pathlib import Path
import math
import unicodedata
from urllib.parse import urldefrag
from typing import List

def build_index(documents: List[str]):
    '''
    takes in a list of document paths and builds an index based on
    the words found in these documents
    it goes through the documents in batches to create partial indices 
    that will be merged with together
    it also creates two additional files for 
    document id to url pairs {doc_id: url} and 
    words to position in the index pairs {word: pos}
    '''
    # index is a defaultdict with keys of strings and values of Posting lists 
    index = defaultdict(list)
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
                # we get rid of the url fragment and check if it we have already seen this url before 
                # if we have already seen the url before, we skip it because we already tokenized and indexed
                # the contents of that page so there is no need to do it another time
                # if we have not seen it before we will store the id with this url inside a dictionary
                # and continue to tokenize its contents    
                url = urldefrag(content['url'])[0]
                if url[-1] != '/':
                    url += '/'
                if url in urls.values():
                    id-=1
                    continue
                urls[id] = url
                if 'content' in content:
                    content = content['content']
                    # we get the text content of the file using BeautifulSoup with its html parser
                    soup = BeautifulSoup(content, 'html.parser')
                    # we get the text in this way to prevent words from getting stuck together
                    text = soup.get_text(' ')
                    # we parse/tokenize the text using nltk word_tokenize
                    tokens = nltk.tokenize.word_tokenize(text.lower())# parse (nltk)
                    for t in tokens:
                        # before adding the word to the index, we must first get rid of any unicode characters still
                        # in the word and replace it with its ascii counterpart if possible and then we stem the word
                        # using nltk PorterStemmer   
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
                    # to check for important words, we find all words with these important tags and add weights to them 
                    # we find all words with these tags: <title>, <h1>, <h2>, <h3>, <strong>, <b>
                    # we tokenize the text in between these tags and put it in a set to remove duplicates
                    # we then assign weights to each of the words based on the tags they appear in   
                    # importance: title > h1 > h2 = h3 = strong = b
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
            # if the key does not already exist in the index, a new key-value pair would be created   
            for k, v in index.items():
                try:
                    data[k] += v
                except(KeyError):
                    data[k] = v
            # we then dump the index back into the index file while also using a JSONEncoder so
            # the posting class can be properly dumped into the file   
            with open('index.json', 'w') as file:
                json.dump(data, file, cls=PostingEncoder)
        # we empty out the index before continuing onto the next batch of documents
        index.clear()
    with open('doc_url.json', 'w') as file:
        json.dump(urls, file)
    # we reformat and sort the index in alphabetical order and update each tf-idf score 
    sort_and_tfidf(len(urls.keys()))
    urls.clear()
    # we then calculate the position of each word in the index file and essentially create 
    # an index of the index 
    index_pos()
    return

def get_doc_paths(path: str) -> List[str]:
    '''
    get all the documents paths in a folder and puts it
    into a list so it can be accessed later during the 
    building of the index
    '''
    documents = []
    for root, _, files in os.walk(Path(path)):
        for name in files:
            if name.endswith((".json")): 
                documents.append(root+'/'+name)
    return documents

def sort_and_tfidf(N: int):
    '''
    this sorts the index alphabetically and calculates the tf-idf score
    for each term-document pair (extra weights are given to important words)
    it then writes it back to the index file and put each term-list of postings pair 
    onto a newline so it can be retrieved easily later
    '''
    with open('index.json') as file:
        index = json.load(file)
        index.pop("")
    for _, v in index.items():
        v_len = len(v)
        for p in v:
            # we go through each posting and update 'y' to be the 
            # tf-idf value for that document 
            tf = 1 + math.log(p["y"], 10)
            idf = math.log((N/v_len), 10)
            w = tf * idf
            if p["f"] != 0:
                # if the 'f' field is not equal to 0, this word is considered important
                # and has a weight associated with it for appearing in certain tags
                # because of that, this weight is multiplied to the tf-idf score
                w *= p['f']
            p['y'] = w 
    to_be_popped = []
    for k, v in index.items():
        if v == []:
            to_be_popped.append(k)
    for k in to_be_popped:
        index.pop(k)
    with open('index.json', 'w') as file:
        # this index is then sort alphabetically and each key-val pair is put on a new line
        alphabetical = json.dumps(index, cls=PostingEncoder, sort_keys=True).replace('], ', '], \n')
        index.clear()
        file.write(alphabetical)

def index_pos():
    '''
    essentially creates an index of the index file that
    stores the exact position a word is in the index file
    so it can be accessed with seek() during retrieval
    '''
    pos = 0
    index_pos = dict()
    with open('index.json') as file:
        # we read the index file until there are no more lines 
        # left in order to store with each word the exact position
        # it appears in in the index file
        # we use len() to calculate the position 
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
    # self.id is basically the document id
    # self.y is the score of the document
    # self.f is used to keep track of the weight of the document 
    # if the word appeared to be important 
    def __init__(self, doc_id):
        self.id = doc_id
        self.y = 1 
        self.f = 0 
    def add_count(self):
        self.y+=1
    def get_doc_id(self): 
        return self.id
    def importance(self, field):
        # importance: title > h1 > h2 = h3 = strong = b
        if field == 'title':
            self.f += 5
        elif field == 'h1':
            self.f += 4
        elif field == 'h2':
            self.f += 3
        elif field == 'h3/strong/b':
            self.f += 2

# this class ensures that a Posting class object can be dumped into a json file
class PostingEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


if __name__ == "__main__":
    build_index(get_doc_paths('./DEV'))

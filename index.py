from collections import defaultdict
from bs4 import BeautifulSoup
import nltk
import os
import json
import lxml
from json import JSONEncoder
from report import report
from pathlib import Path
import math
from operator import itemgetter
from copy import deepcopy


def build_index(path):
    # index is a defaultdict with keys of strings and values of Posting lists 
    index = defaultdict(list)
    indices = []
    # we get all the paths of the files inside the DEV folder
    documents = get_doc_paths(path)
    id = 0
    index_num = 1
    # we will read and parse the documents in batches of 1000 until there are no documents left
    batch_size = 1200
    
    while len(documents) != 0:
        file_path = Path(f'./index{index_num}.json')
        if not Path.is_file(file_path):
            batch = documents[0:batch_size]
            documents = documents[batch_size:]
            for b in batch:
                id+=1
                with open(b, 'r', encoding='utf-8', errors='ignore') as f:
                    content = json.load(f)
                    if 'content' in content:
                        content = content['content']
                        # we get the text content of the file with BeautifulSoup
                        soup = BeautifulSoup(content, features='xml')# get text 
                        text = soup.get_text()
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
        file_path = Path(f'./index{index_num}.json')
        if not Path.is_file(file_path):
            with open(f"index{index_num}.json", "w") as file:
                json.dump(index, file, cls=PostingEncoder, sort_keys=True)
        index_num += 1
        indices.append(file_path)
        if index_num == 48:
            break
        """
        # we save to disk using json dump and json load
        file_path = Path(f'./index.json')
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
            for k, v in data.items():
                index[k] += v

            with open('index.json', 'w') as file:
                json.dump(index, file, cls=PostingEncoder)
        # we empty out the index before continuing onto the next batch of documents
        #index.clear()
        """
        index = defaultdict(list)
    merge(indices)
    report(id)
    return    


def merge(indices):
    import psutil
    import ijson
    final_index = {}
    file_path = Path(f'./index.json')
    inverted_index = {}
    iterators = []
    curr_words = []
    for i in range(len(indices)):
        iterator = iter(json.load(open(indices[i])).items())
        #f = json.load(open(indices[i]))
        #f = ijson.items(open(indices[i]), "items")
        #print(next(f))
        iterators.append(iterator) 
        curr_words.append(next(iterator))
    count = 0
    process = psutil.Process(os.getpid())
    print(process.memory_info().rss)
    
    while curr_words != []:
        words = [word[0] for word in curr_words]
        min_index, min_word = min(enumerate(words), key=itemgetter(1))
        curr_words_copy = deepcopy(curr_words)
        iterators_copy = deepcopy(iterators)
        if words.count(min_word) > 1:
            postings = []
            for index, word in enumerate(words):
                if word == min_word:
                    #data = json.load(open(indices[index]))
                    data = curr_words_copy[index][1]
                    postings.append(data)
                    try:
                        curr_words_copy[index] = next(iterators_copy[index])
                    except StopIteration:
                        curr_words.pop(index)
                        iterators.pop(index)
            final_index[min_word] = postings

        else:
            #final_index[min_word] = json.load(open(indices[min_index]))[min_word]
            final_index[min_word] = curr_words[min_index][1]
            try:
                curr_words[min_index] = next(iterators[min_index])
            except StopIteration:
                curr_words.pop(min_index)
                iterators.pop(min_index)
        if count == 1000:
            if not Path.is_file(file_path):
                with open("index.json", "w") as file:
                    json.dump(final_index, file, cls=PostingEncoder)
            else:
                with open("index.json", "r+") as file:
                    file.seek(os.stat(file_path).st_size -1)
                    file.write(json.dumps(final_index, cls=PostingEncoder).replace("{", ", ", 1))
            final_index = {}
            count = 0
        else:
            count += 1       

    with open("index.json", "w") as file:
        file.seek(os.stat(file_path).st_size -1)
        file.write(json.dumps(final_index, cls=PostingEncoder).replace("{", ", ", 1))


def get_doc_paths(path):
    documents = []
     #for root, _, files in os.walk("DEV/"):
    for root, _, files in os.walk(Path(path)):
        for name in files:
            if name.endswith((".json")): 
                documents.append(root+'/'+name)
    return documents

def tfidf(N): # not sure if correct
    with open('index.json') as file:
        index = json.load(file)
    for _, v in index.items():
        v_len = len(v)
        for p in v:
            tf = 1 + math.log(p.freq_count, 10)
            idf = math.log((N/v_len))
            w = tf * idf
            p.freq_count = w # put here temporarily will prob rename/create new attribute and rebuild index later
    with open('index.json', 'w') as file:
        json.dump(index, file, cls=PostingEncoder)

def get_doc_url(documents, id):
    i = id - 1 # because id starts at 1
    doc = documents[i]
    with open(doc, 'r', encoding='utf-8', errors='ignore') as f:
        content = json.load(f)
        if 'url' in content:
            return content['url']
    return ''

class Posting():
    # the posting class contain the document id and the frequency count of the word in that document
    def __init__(self, doc_id):
        self.doc_id = doc_id
        self.freq_count = 1
    def add_count(self):
        self.freq_count+=1
    def get_doc_id(self): 
        return self.doc_id

# this class ensures that a Posting class object can be dumped into a json file
class PostingEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


if __name__ == "__main__":
    build_index("./DEV")
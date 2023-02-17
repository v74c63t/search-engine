from collections import defaultdict
from bs4 import BeautifulSoup
import nltk
import os
import json
from report import report
from pathlib import Path

def build_index():   
    # I basically a dictionary
    # N the id of the document
    # Parse the document
    # For all the tokens t in T we see if the word is already in the dictionary if not we add it as a key 
    # To the dictionary and give it an empty list of postings as a value
    # If it already was in the dictionary, append the posting to the key
    # look into port stemming (can import from nltk)
    # read in batches
    # save to disk
    # merge after each read
    index = defaultdict(list)
    documents = []
    for root, _, files in os.walk("DEV/"):
        for name in files:
            if name.endswith((".json")): # im pretty sure everything is a json file tho?
                documents.append(root+'/'+name)
    id = 0
    batch_size = # some number
    #for d in documents:
    while documents.size() != 0:
        batch = documents[0:batch_size]
        documents = documents[batch_size:]
        for b in batch:
            id+=1
            with open(b, 'r') as f:
                data = json.load(f)
                if "content" in data:
                    content = data["content"]

                    soup = BeautifulSoup(content, "html.parser")#"lxml")
                    text = soup.get_text()
                    
                    tokens = nltk.tokenize.word_tokenize(text.lower())# parse (nltk)
                    tokens = [word for word in tokens if word.isalnum()]
                for t in tokens:
                    stem = nltk.stem.PorterStemmer(t)#port stem(t) (look at nltk) # need to fix b/c some stems are wrong
                    if index[stem] == []: index[stem] = Posting(id)
                    elif index[stem][-1].getdoc_id() == id: index[stem][-1].add_count()
                    else: index[stem].append(Posting(id))
        # CHECK IF THIS IS WORKS
        file_path = Path('./index.json')
        if not Path.is_file(file_path):
            with open('index.json', 'w') as file:
                json.dump(index, file)
        else:
            with open('index.json') as file:
                data = json.load(file)
            for k, v in data:
                index[k] += v
            with open('index.json', 'w') as file:
                json.dump(index, file)
        # save to disk json dump json loads???
        # json load to get dictionary from file/disk?
        # merge maybe using a for loop to add values from second dictionary to first?
        # json dump to store to file/disk? make sure to overwrite the file
        index.clear() # empty out index
    report(id)
    return


class Posting():
    # we need a posting class
    # posting will contain the document id and the frequency count of the word in that document?
    def __init__(self, doc_id):
        self.doc_id = doc_id
        self.freq_count = 1
    def add_count(self):
        self.freq_count+=1
    def get_doc_id(self): 
        return self.doc_id

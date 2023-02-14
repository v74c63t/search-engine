from collections import defaultdict
from bs4 import BeautifulSoup
import nltk

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
    for root, dirs, files in os.walk("DEV/"):
        for name in files:
            if name.endswith((".json")):
                documents.append(root+'/'+name)
    id = 0
    batch_size = # some number
    #for d in documents:
    while documents.size() != 0:
        batch = documents[0:batch_size]
        documents = documents[batch_size:]
        for b in batch:
            id+=1
            with open(b, 'r'):
                text = # get text from file
                tokens = nltk.tokenize.word_tokenize(text.lower())# parse (nltk)
                for t in tokens:
                    stem = nltk.stem.PorterStemmer(t)#port stem(t) (look at nltk)
                    if index[stem] == []: index[stem] = Posting(id)
                    elif index[stem][-1].getdoc_id() == id: index[stem][-1].add_count()
                    else: index[stem].append(Posting(id))
        # save to disk
        # merge
        # empty out index

    return


class Posting():
    # we need a posting class
    # posting will contain the document id and the frequency count of the word in that document?
    def __init__(self, doc_id):
        self.doc_id
        self.freq_count = 1
    def add_count(self):
        self.freq_count+=1
    def get_doc_id(self): return self.doc_id

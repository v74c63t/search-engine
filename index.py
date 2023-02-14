from collections import defaultdict

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
    batch = 
    for d in documents:
        for b in batch:
            id+=1
            tokens = # parse (nltk)
            for t in tokens:
                t = #port stem(t) (look at nltk)
                if index[t] == []: index[t] = Posting(id)
                elif index[t][-1].getdoc_id() == id: index[t][-1].add_count()
                else: index[t].append(Posting(id))
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

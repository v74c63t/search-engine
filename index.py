   
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
    return


class Posting():
    # we need a posting class
    # posting will contain the document id and the frequency count of the word in that document?
    def __init__(self):
        self.doc_id
        self.freq_count
    def add_count(self):
        self.freq_count+=1

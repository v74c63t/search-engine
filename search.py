from pathlib import Path
import index
import json

data = json.load("./index.json") # store in global variable for now

def search():
    file_path = Path('./index.json')
    documents = index.get_doc_paths("./DEV")   
    if not Path.is_file(file_path):
        index.build_index(documents)
        index.tfidf(len(documents))
    #query = input()
    # figure out what to do with index


def split(words):
    # merge sort
    if len(words) > 2:
        mid = len(words) // 2
        merge(split(words[:mid]), split(words[mid:]))
    elif len(words) == 1:
        return list(posting.get_doc_id() for posting in data[words[0]])
    else:
        ids1 = list(posting.get_doc_id() for posting in data[words[0]])
        ids2 = list(posting.get_doc_id() for posting in data[words[1]])
        return merge(ids1, ids2)


def merge(ids1, ids2):
    # returns common doc ids
    merged = []
    i1 = 0
    i2 = 0

    while i1 < len(ids1) and i2 < len(ids2):
        id1 = ids1[i1]
        id2 = ids2[i2]
        if id1 == id2:
            merged.append(id1)
            i1 += 1
            i2 += 1
        elif id1 < id2:
            i1 += 1
        else:
            i2 += 1
    return merged


def find_documents(query):
    split(query.split())

    # after finding common documents, go through positions and calculcate distance from each other
    # rank document ids based on distances
    # maybe create another index that associates document id to url
    

if __name__ == "__main__":
    search()
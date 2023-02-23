from pathlib import Path
import index
import nltk

def search():
    file_path = Path('./index.json')
    documents = index.get_doc_paths()   
    if not Path.is_file(file_path):
        index.build_index(documents)
        index.tfidf(len(documents))
    query = input()
    #queries = []
    stemmer = nltk.PorterStemmer
    postings = []
    for q in query.split():
        #queries.append(stemmer.stem(q))
        postings.append(index[stemmer.stem(q)])
    

    # figure out what to do with index
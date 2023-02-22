from pathlib import Path
import index


def search():
    file_path = Path('./index.json')
    documents = index.get_doc_paths()   
    if not Path.is_file(file_path):
        index.build_index(documents)
        index.tfidf(len(documents))
    query = input()
    # figure out what to do with index
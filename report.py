import json
import sys
def report(num_of_docs):
    #json load the index from file/disk
    with open('index.json') as file:
        index = json.load(file)
    # check how many keys are in teh dictionary
    # that should be the amount of unique words
    num_of_unique = len(index.keys())
    with open('report.txt', 'w') as f:
        f.write(f'Number of documents: {num_of_docs}\n')
        f.write(f'Number of unique words: {num_of_unique}\n')
        # figure out how to get size of index on disk
        bytes = 381129773
        kb = bytes/1000
        f.write(f'Total size of index on disk: {kb} KB')
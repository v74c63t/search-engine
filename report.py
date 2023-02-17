
def report(num_of_docs):

    index = #json load the index from file/disk
    # check how many keys are in teh dictionary
    # that should be the amount of unique words
    num_of_unique = len(index.keys())
    with open('report.txt', 'w') as f:
        f.write(f'Number of documents: {num_of_docs}\n')
        f.write(f'Number of unique words: {num_of_unique}')
        # figure out how to get size of index on disk

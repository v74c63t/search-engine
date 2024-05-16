from collections import defaultdict
from bs4 import BeautifulSoup
import nltk
import os
import json
from json import JSONEncoder
from pathlib import Path
import math
import unicodedata
from urllib.parse import urldefrag
import ast
import time

def build_index(documents):
    '''
    takes in a list of documents and builds an index based on
    the words found in these documents
    it goes through the documents in batches to create partial indices 
    that will be merged with together
    it also creates two additional files for 
    document id to url pairs {doc_id: url} and 
    words to position in the index pairs {word: pos}

    documents: a list of document paths obtained from get_doc_paths()
    '''
    # index is a defaultdict with keys of strings and values of Posting lists 
    start = time.time()
    partial = 1 # this is the partial index file number
    index = defaultdict(list)
    id = 0
    # we will read and parse the documents in batches of 1000 until there are no documents left
    batch_size = 1000
    urls = dict()
    while len(documents) != 0:
        print(f'{len(documents)} documents left to read and parse')
        batch = documents[0:batch_size]
        documents = documents[batch_size:]
        for b in batch:
            id+=1
            with open(b, 'r', encoding='utf-8', errors='ignore') as f:
                content = json.load(f)
                # we get rid of the url fragment and check if it we have already seen this url before 
                # if we have already seen the url before, we skip it because we already tokenized and indexed
                # the contents of that page so there is no need to do it another time
                # if we have not seen it before we will store the id with this url inside a dictionary
                # and continue to tokenize its contents    
                url = urldefrag(content['url'])[0]
                if url[-1] != '/':
                    url += '/'
                if url in urls.values():
                    id-=1
                    continue
                urls[id] = url
                if 'content' in content:
                    content = content['content']
                    # we get the text content of the file using BeautifulSoup with its html parser
                    soup = BeautifulSoup(content, 'html.parser')
                    # we get the text in this way to prevent words from getting stuck together
                    text = soup.get_text(' ')
                    # we parse/tokenize the text using nltk word_tokenize
                    tokens = nltk.tokenize.word_tokenize(text.lower())# parse (nltk)
                    for t in tokens:
                        # before adding the word to the index, we must first get rid of any unicode characters still
                        # in the word and replace it with its ascii counterpart if possible and then we stem the word
                        # using nltk PorterStemmer   
                        stemmer = nltk.PorterStemmer()
                        stem = stemmer.stem(unicodedata.normalize('NFKD', t).encode('ascii', errors='ignore').decode())#port stem(t) (look at nltk)
                        # as long as the word is alphanumeric it is added to the index
                        if(stem.isalnum() and stem != ""):
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
                    # to check for important words, we find all words with these important tags and add weights to them 
                    # we find all words with these tags: <title>, <h1>, <h2>, <h3>, <strong>, <b>
                    # we tokenize the text in between these tags and put it in a set to remove duplicates
                    # we then assign weights to each of the words based on the tags they appear in   
                    # importance: title > h1 > h2 = h3 = strong = b
                    importance = set(stemmer.stem(unicodedata.normalize('NFKD', word).encode('ascii', errors='ignore').decode()) 
                                     for title in soup.find_all('title') 
                                     for word in nltk.tokenize.word_tokenize(title.get_text(' ').strip().lower()) if word.isalnum() and word != "") 
                    for title in importance:
                        try:index[title][-1].importance('title')
                        except(IndexError): continue
                    importance = set(stemmer.stem(unicodedata.normalize('NFKD', word).encode('ascii', errors='ignore').decode()) 
                                     for h1 in soup.find_all('h1') 
                                     for word in nltk.tokenize.word_tokenize(h1.get_text(' ').strip().lower()) if word.isalnum() and word != "") 
                    for h1 in importance:
                        try:index[h1][-1].importance('h1')
                        except(IndexError): continue
                    importance = set(stemmer.stem(unicodedata.normalize('NFKD', word).encode('ascii', errors='ignore').decode()) 
                                     for h2 in soup.find_all('h2') 
                                     for word in nltk.tokenize.word_tokenize(h2.get_text(' ').strip().lower()) if word.isalnum() and word != "") 
                    for h2 in importance:
                        try:index[h2][-1].importance('h2')
                        except(IndexError): continue
                    importance = set(stemmer.stem(unicodedata.normalize('NFKD', word).encode('ascii', errors='ignore').decode()) 
                                     for h3_or_bold in soup.find_all(['h3','strong', 'b']) 
                                     for word in nltk.tokenize.word_tokenize(h3_or_bold.get_text(' ').strip().lower()) if word.isalnum() and word != "") 
                    for h3_or_bold in importance:
                        try:index[h3_or_bold][-1].importance('h3/strong/b')
                        except(IndexError): continue

        # we save to disk using json dump and json load
        print()
        print(f'Saving current batch to partial index {partial}')
        file_path = Path(f'./indexes/partial_index{partial}.txt')
        if not Path.is_dir(Path('./indexes')):
            os.mkdir('indexes')
        file = open(file_path, "w")
        # this is to prevent empty keys
        try:
            index.pop("")
        except(KeyError):
            pass
        # this is to prevent empty values
        to_be_popped = []
        for k, v in index.items():
            if v == []:
                to_be_popped.append(k)
        for k in to_be_popped:
            index.pop(k)
        alphabetical = json.dumps(index, cls=PostingEncoder, sort_keys=True).replace('], ', '], \n')
        file.write(alphabetical)
        file.close()
        print(f'{file_path} was created')
        print()
        partial += 1
        # we empty out the index before continuing onto the next batch of documents
        index.clear()
    # with open('doc_url_analyst.json', 'w') as file:
    #     json.dump(urls, file)

    # we save the doc id to document dictionary to a file
    print('Saving id to document pairs')
    print()
    with open('doc_url_dev.json', 'w') as file:
        json.dump(urls, file)
    
    num_urls = len(urls.keys())
    print(f'{num_urls} documents read and parsed')
    urls.clear()
    
    # now all the partial indexes will be merged into one big index
    print('Merging all partial indexes')
    merge_partial_indexes('indexes')

    # once everything is merged, a weighted tf-idf score will be calculated for each term
    print('Calculating weighted tf-idf scores')
    calc_tfidf(num_urls)
    print()

    # we then calculate the position of each word in the index file and essentially create an index of the index 
    # index_pos()
    print('Creating index of index')
    index_of_index()
    print()
    end = time.time() - start
    print(f'Index was successfully built in {end / 60} minutes')
    return

def merge_partial_indexes(path):
    indexes = []
    for root, _, files in os.walk(Path(path)):
        for name in files:
            if 'partial_index' in name:
                indexes.append(root+'/'+name)
    # all the partial index file names are collected for merging
    print('Partial indexes: ', indexes)
    print()
    i = 1

    while len(indexes) > 1:
        file1 = open(Path(indexes[0]), "r")
        file2 = open(Path(indexes[1]), "r")
        print(f'Merging {indexes[0]} and {indexes[1]}')
        merged_path = merge_two_indexes(file1, file2, i)
        print(f'Finished merging into {merged_path}')
        print(f'Deleting {indexes[0]} and {indexes[1]}')
        print()
        # the merged index is added back to the list of indexes needed to be checked/merged
        indexes.append(merged_path)
        # the checked indexes will now be deleted
        os.remove(indexes[0])
        indexes.pop(0)
        os.remove(indexes[0])
        indexes.pop(0)
        i+=1
    os.rename(indexes[0], 'indexes/merged_index.json')

def merge_two_indexes(file1, file2, i):
    merge_path = f"indexes/temp_merge{i}.txt"
    temp_merge_file = open(Path(merge_path), "w")
    line1 = file1.readline()
    line2 = file2.readline()
    first = True
    prev_line = ""
    while line1 != "" and line2 != "":
        temp_dict = dict()
        new_line = ""
        if line1.startswith("{"):
            key1 = line1[2:line1.find('": ')]
            line1 = line1[1:]
        else:
            key1= line1[1:line1.find('": ')]
        if line2.startswith("{"):
            key2 = line2[2:line2.find('": ')]
            line2 = line2[1:]
        else:
            key2= line2[1:line2.find('": ')]
        if line1.endswith("], \n"):
            val1 = ast.literal_eval(line1[line1.find('": ')+3:-3])
        else:
            val1 = ast.literal_eval(line1[line1.find('": ')+3:-1])
        if line2.endswith("], \n"):
            val2 = ast.literal_eval(line2[line2.find('": ')+3:-3])
        else:
            val2 = ast.literal_eval(line2[line2.find('": ')+3:-1])
        if key1 == key2:
            temp_dict[key1] = val1 + val2
            if first:
               new_line = json.dumps(temp_dict, cls=PostingEncoder)[:-1] + ', \n' 
               first = False
            else:
                new_line = json.dumps(temp_dict, cls=PostingEncoder)[1:-1] + ', \n'
            line1 = file1.readline()
            line2 = file2.readline()
        elif key1 < key2:
            new_line = line1
            if new_line.endswith('}'):
                new_line = new_line.replace(']}', '], \n')
            if first:
                new_line = '{' + new_line
                first = False
            line1 = file1.readline()
        elif key2 < key1:
            new_line = line2
            if new_line.endswith('}'):
                new_line = new_line.replace(']}', '], \n')
            if first:
                new_line = '{' + new_line
                first = False
            line2 = file2.readline()
        if new_line.endswith('}'):
            new_line = new_line.replace(']}', '], \n')
        if prev_line != "" and new_line != "":
            temp_merge_file.write(prev_line)
        if new_line != "":
            prev_line = new_line

    while line1 != "":
        new_line = ""
        if line1.startswith("{") and first:
            new_line = line1
            first = False
        elif line1.startswith("{"):
            new_line = line1[1:]
        else:
           new_line = line1
        if prev_line != "":
            temp_merge_file.write(prev_line)
        if new_line.endswith('}'):
            new_line = new_line.replace(']}', '], \n')
        prev_line = new_line
        line1=file1.readline()
    
    while line2 != "":
        new_line = ""
        if line2.startswith("{") and first:
            new_line = line2
            first = False
        elif line2.startswith("{"):
            new_line = line2[1:]
        else:
           new_line = line2
        if prev_line != "":
            temp_merge_file.write(prev_line)
        if new_line.endswith('}'):
            new_line = new_line.replace(']}', '], \n')
        prev_line = new_line
        line2=file2.readline()

    temp_merge_file.write(prev_line.replace('], \n', ']}'))
    file1.close()
    file2.close()
    temp_merge_file.close()
    return merge_path


def get_doc_paths(path):
    '''
    get all the documents paths in a folder and puts it
    into a list so it can be accessed later during the 
    building of the index

    path: the path to the folder containing all the documents
    documents: a list of all the document paths
    '''
    documents = []
    for root, _, files in os.walk(Path(path)):
        for name in files:
            if name.endswith((".json")): 
                documents.append(root+'/'+name)
    return documents

def calc_tfidf(N):
    # we go line by line to calculated the weighted tf-idf score for each term 
    # and save that information into the final index file
    merged_index = open('indexes/merged_index.json', 'r')
    final_index = open('indexes/final_index.json', 'w')
    line = merged_index.readline()
    first = True
    while line != "":
        last = True
        temp_line = line
        if not temp_line.startswith('{'):
            temp_line = '{' + temp_line
        if not temp_line.endswith(']}'):
            last = False
            temp_line = temp_line.replace('], \n', ']}')
        line_dict = json.loads(temp_line)
        key = list(line_dict.keys())[0]
        if key == '':
            line = merged_index.readline()
            continue
        postings = line_dict[key]
        if postings == []:
            line = merged_index.readline()
            continue
        num_postings = len(postings)
        for posting in postings:
           # we go through each posting and update 'y' to be the 
            # tf-idf value for that document 
            tf = 1 + math.log(posting["y"], 10)
            idf = math.log((N/num_postings), 10)
            w = tf * idf
            if posting["f"] != 0:
                # if the 'f' field is not equal to 0, this word is considered important
                # and has a weight associated with it for appearing in certain tags
                # because of that, this weight is multiplied to the tf-idf score
                w *= posting['f']
            posting['y'] = w 
        write = json.dumps(line_dict)[1:]
        if first:
            write = '{' + write
            first = False
        if last:
            final_index.write(write)
        else:
            final_index.write(write.replace(']}', '], \n'))
        line = merged_index.readline()
    merged_index.close()
    os.remove('indexes/merged_index.json')
    final_index.close()

def index_of_index():
    '''
    essentially creates an index of the index file that
    stores the exact position a word is in the index file
    so it can be accessed with seek() during retrieval
    '''
    pos = 0
    index_pos = dict()
    with open('indexes/final_index.json') as file:
        # we read the index file until there are no more lines 
        # left in order to store with each word the exact position
        # it appears in in the index file
        # we use len() to calculate the position 
        line = file.readline()
        if line != "":
            i = line.find('":')
            word = line[2:i]
            index_pos[word] = pos
            pos += len(line)
        line = file.readline()
        while line != "":
            i = line.find('":')
            word = line[1:i]
            index_pos[word] = pos
            pos += len(line)
            line = file.readline()
    with open('indexes/index_of_index.json', 'w') as file:
        json.dump(index_pos, file)



class Posting():
    # self.id is basically the document id
    # self.y is the score of the document
    # self.f is used to keep track of the weight of the document 
    # if the word appeared to be important 
    def __init__(self, doc_id):
        self.id = doc_id
        self.y = 1 
        self.f = 0 
    def add_count(self):
        # used to add frequency count
        self.y+=1
    def get_doc_id(self): 
        return self.id
    def importance(self, field):
        # importance: title > h1 > h2 = h3 = strong = b
        # depending on the tag the word is found in, it will have
        # a different multiplier that will change its tf-idf score
        if field == 'title':
            self.f += 5
        elif field == 'h1':
            self.f += 4
        elif field == 'h2':
            self.f += 3
        elif field == 'h3/strong/b':
            self.f += 2

# this class ensures that a Posting class object can be dumped into a json file
class PostingEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


if __name__ == "__main__":
    build_index(get_doc_paths('./DEV'))

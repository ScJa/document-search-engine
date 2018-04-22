import itertools
import os
import sys
import spacy
from bs4 import BeautifulSoup
import pickle
import pprint
import codecs
import snowballstemmer

path = "../data/TREC8all/Adhoc"


def count_unique(id_):
    if id_ in d_doc_unique_words_count.keys():
        d_doc_unique_words_count[id_] = d_doc_unique_words_count[id_] + 1
    else:
        d_doc_unique_words_count[id_] = 1


def iter_and_parse_all_files(p):
    for root, dirs, files in os.walk(p):
        for file in files:
            if not file.startswith('.'):
                print('using: ' + str(os.path.join(root, file)))
                path = os.path.join(root, file)
                text_file = codecs.open(path, 'r', "iso-8859-1").read()
                soup = BeautifulSoup(text_file, 'lxml')
                for doc in soup.find_all("doc"):
                    strdoc = doc.docno.string.strip()
                    texts = doc.find_all("text")
                    if len(texts) is not 0:
                        text_only = str(doc.find_all("text")[0])
                    # print("Yield id: "+ strdoc)
                    yield (strdoc, text_only)


def gen_items(path):
    path = next(path)
    # print(path)
    text_file = codecs.open(path, 'r', "iso-8859-1").read()
    soup = BeautifulSoup(text_file, 'lxml')
    for doc in soup.find_all("doc"):
        strdoc = doc.docno.string.strip()
        texts = doc.find_all("text")
        if len(texts) is not 0:
            text_only = str(doc.find_all("text")[0])
        # print("Yield id: "+ strdoc)
        yield (strdoc, text_only)


# command line arguments, all are ON by DEFAULT
lemmatize = False
stop_words = False
stem = False
case_fold = False
sys.argv.pop(0)
if len(sys.argv) == 0:
    lemmatize = True
    stop_words = True
    print("""Using default settings:
- case-folding OFF
- stemming OFF
- lemmatization ON
- stop word filters ON
    """)
else:
    for argu in sys.argv:
        if argu == "-none":
            lemmatize = False
            stop_words = False
            stem = False
            case_fold = False
        elif argu == "-lemm":
            if stem:
                print("Stemming and lemmatization do not work in combination.")
                print("Program is exiting.")
                sys.exit(1)
            lemmatize = True
        elif argu == "-stop":
            stop_words = True
        elif argu == "-stem":
            if lemmatize:
                print("Stemming and lemmatization do not work in combination.")
                print("Program is exiting.")
                sys.exit(1)
            stem = True
        elif argu == "-case":
            case_fold = True
        else:
            print("The argument {0} is not valid.".format(argu))
            print("""-case turns on case-folding.
-lemm turns on the lemmatization. Does NOT work in combination with stemming.
-stem turns on stemming. Does NOT work in combination with lemmatizing.
-stop turns on the stop word filter.

-none turns everything OFF and only runs with basic tokens. ignores all other args            
Program is exiting.""")
            sys.exit(1)

print("Using {} as a path for files to index. Changeable in the beginning of the script.".format(path))

# cli end - index start
nlp = spacy.load('en')
stemmer = snowballstemmer.stemmer("english")
file_counter = 0
word_counter = 0
d = {}
d_doc_words_count = {}
d_doc_unique_words_count = {}

numer_of_files = 1
for root, dirs, files in os.walk("../data/TREC8all/Adhoc"):
    for file in files:
        if not file.startswith('.'):
            numer_of_files += 1

gen1, gen2 = itertools.tee(iter_and_parse_all_files(path))
ids = (id_ for (id_, text) in gen1)
texts = (text for (id_, text) in gen2)
docs = nlp.pipe(texts, batch_size=100, n_threads=6)

for id_, doc in zip(ids, docs):
    doc_word_counter = 0
    file_counter += 1
    for token in doc:
        # filter out stopwords
        if not stop_words or (token.is_alpha and not token.is_stop and len(token.orth_) > 1):
            doc_word_counter = doc_word_counter + 1
            # take processed lemma or original depending on settings
            strtok = token.lemma_.strip() if lemmatize else token.orth_.strip()
            if case_fold:
                strtok = strtok.casefold()
            if stem:
                strtok = stemmer.stemWord(strtok)
            if strtok not in d.keys():
                count_unique(id_)
                d[strtok] = {id_: 1}
            elif strtok in d.keys():
                # either increase counter or add document
                if id_ in d[strtok].keys():
                    d[strtok][id_] = d[strtok][id_] + 1
                else:
                    count_unique(id_)
                    d[strtok][id_] = 1
    # take only first k items to test
    # if file_counter == 1000:
        # break
    word_counter = word_counter + doc_word_counter
    d_doc_words_count[id_] = doc_word_counter

d_doc_words_count["word_counter"] = word_counter
d_doc_words_count["doc_counter"] = file_counter

# test output
# pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(d_doc_words_count)
# pp.pprint(d_doc_unique_words_count)
# print(file_counter)

pickle.dump(d_doc_words_count, open("word_count.p", "wb"))
pickle.dump(d, open("inv_ind.p", "wb"))
pickle.dump(d_doc_unique_words_count, open("unique_words_count.p", "wb"))

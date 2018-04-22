# Document Search Engine
### Searches over a million articles in three seconds and creates a document ranking based on simularity functions like BM25.

## Overview

This project uses Python 3 and spacY and NLTK for the basic libraries and coreNLP in the map reduce example.
Indexing all the documents in python takes about 3 Hours. The map-reduce implementation only requires 12 minutes.
The searcher uses the indexes provided and can score documents based on cosine similarity in a few seconds (1000 entries ranking list).
You can score the topics based on TF-IDF, BM25 and BM25VA. 
The score results have been evaluated by trec_eval and have an average MAP of ~0.16.
The articles used in this project where part of the (Tipster Collection)[https://catalog.ldc.upenn.edu/LDC93T3A]

´
## Run requirements

Everything was built on Python 3.6 but should run on earlier versions as well.
Package requirements:

- spacy (also need to download a model "python -m spacy download en")
- BeautifulSoup 
- codecs
- snowball-stemmer


## Index

We create three different dictionaries during the indexing phase.
We run through all the documents and build the dictionaries by adding new entries.
The dictionaries are stored in pickle format, and are around 500MB big.

- Inverted index with the words as keys, as values we save the docNo and the occurrence rate (see below)
- Word counter index which contains the length of all documents
- Word unique counter index which is needed for BM25VA

### Examples:

Inverted index:
{write : {doc1 : 2, doc2: 5},
zone : {doc5 : 1}}

Word counter:
{doc1 : 100}

Unique word conter:
{doc1 : 35}


The following metrics are calculated as well
- total number of documents
- total number of words in all documents

### Natural language pre-processing

Several pre-processing options are implemented an can be used via the commandline (lemmatization, stemming, stopwords removal, case folding).
They can be used in any combination apart from lemmatization and stemming together.
We use spacy for the tokenization, stopwords removal and case folding. For stemming we use snowball-stemmer.

Several *Special strings* are handled. Basic stopwords are already removed in spacy via
- default english stopwords (`en.STOPWORDS`)
- spacy doesn't sort out word fragments which contain some special characters like "-", we chose to remove them with isalpha as well. It could be argued to handle these differently.
- custom stopwords
All of these are excluded from the tokens which later on are stored in the index.

Case-folding is implemented with the python string method "casefold()".

### Map reduce indexing

Overall runtime to produce output files around 12 minutes. This is pretty impressive, compared that the python implementation (non multi-threaded) is taking around 3 hours.
Notably as well, as the first 60 Seconds or so are just spent loading the nlp library and starting up spark and not actually executing any transformations.

Two output files will be generated in json format. The first one containing the inverted index of size 1.4G, the second one containing the
lookup table of words / distinct words per document to compute the scores of 17m. With a structure of

```
+----------------+--------------------------------------------------------------------------+
|word            |documents                                                                 |
+----------------+--------------------------------------------------------------------------+
|Abner           |[[LA012189-0001,1]]                                                       |
|Castaneda       |[[LA011589-0001,11], [LA011090-0001,2]]                                   |
|Easter          |[[LA041690-0001,1], [LA102389-0001,1], [LA111389-0001,1], [FBIS4-34590,2]]|
...
```

As the files are not standard UTF-8 encoded we implemented a custom hadoop file input format to read the documents with their corresponding correct format.
In a real production setup a proper hadoop file format would be used like parquet, but for simplicity of integrating with python we chose to use JSON.

### Scoring

We have implemented *tf-idf*, *bm25* and *bm25va* scoring. The ranking works as follows:
For each word that is both in the topic and in the document we calculate the score of both the topic and the documents. 
We use cosine similarity for ranking, however we kind of calculate it while creating the vectors.
We add up the upper part of cosine similarity A*B for all documents if they have the word (otherwise it the product is 0).
We add up the "vector_betrag" (x²) while going through the words and documents and use sqrt on it after the loop.
Then we have another loop to connect the lower and upper part of the cosine similarity for all documents.
For each topic word we iterate over all the entries of the word in the inverted index, therefore all documents with at least one same word get scored and ranked.
In the end we sort them and only use the best 1000.

The tf-idf, bm25 and bm25va implementations are pretty straightforward and carefully put into methods to easily see how they are implemented.
One thing worth mentioning is that we implemented the term frequency as: word_occurrence / document_length (in words).
However all methods are written to be able to be easily looked up in the search.py.

It is interesting that the differences in the table below are so small. TF-IDF surely performed better because we added the document length to it, however we thought
it would still perform worse.
We were also surprised that BM25VA performed worse than BM25, it even made us check our implementation again (however everything seems correctly implemented).
We have some ideas to why this could be the case. The default "b"-value in BM25 of 0.75 is fits probably pretty well for all the documents we indexed. They articles
are "as normal as texts get" on average, so the default value should perform very well. If all the articles however were extremely long or just a few words short, than
the default b value would probably fail. With the average length of 261 words per document it fits well. In addition to that we assume that the b-calculation of BM25VA
is only "vague". That means the b-value is never completely wrong, but also not optimized. In every case the b-values could be adjusted by hand to achieve better results.
Because of this we think that BM25VA is only good if you know nothing about the texts or have completely different texts (very short and very long), which was not the case
in this assignment.

Calculations can be found in the report/calculations folder. In the calculations.pdf file all scores have been calculated by hand. TF-IDF with a normal topic. For BM25/VA
we used a test topic because the last calculation was too long.

Note: All scores are from the default settings of the indexer.py - lemmatization and stopwords on.

### Scores

```
+---+------+------+------+
|   |TF-IDF|BM25  |BM25VA|
+---+------+------+------+
|401|0.0069|0.0070|0.0070|
|402|0.0860|0.0904|0.0929|
|403|0.5686|0.5890|0.5828|
|404|0.2085|0.2089|0.2094|
|405|0.0290|0.0359|0.0333|
|406|0.3575|0.3471|0.3643|
|407|0.1488|0.1779|0.1627|
|408|0.0848|0.0968|0.0927|
|409|0.0521|0.0662|0.0604|
|410|0.7273|0.7597|0.7533|
|411|0.0194|0.0204|0.0195|
|412|0.0697|0.0538|0.0586|
|413|0.0644|0.0692|0.0692|
|414|0.1612|0.1814|0.1784|
|415|0.1960|0.2000|0.1985|
|416|0.2827|0.3135|0.3145|
|417|0.2319|0.2401|0.2628|
|418|0.2087|0.2147|0.2126|
|419|0.0839|0.0879|0.0871|
|420|0.3708|0.3190|0.3197|
|421|0.0141|0.0135|0.0132|
|422|0.0828|0.0612|0.0638|
|423|0.4822|0.4833|0.4835|
|424|0.0808|0.1005|0.0904|
|425|0.2519|0.2514|0.2531|
|426|0.0525|0.0498|0.0514|
|427|0.0532|0.0713|0.0698|
|428|0.1291|0.1214|0.1230|
|429|0.2560|0.2527|0.2543|
|430|0.1421|0.1844|0.1831|
|431|0.1093|0.1195|0.1149|
|432|0.0002|0.0002|0.0002|
|433|0.1846|0.1965|0.1878|
|434|0.2375|0.2404|0.2393|
|435|0.0094|0.0081|0.0085|
|436|0.0171|0.0228|0.0203|
|437|0.0046|0.0067|0.0058|
|438|0.1079|0.1050|0.1068|
|439|0.0019|0.0027|0.0023|
|440|0.0075|0.0049|0.0057|
|441|0.3313|0.3487|0.3522|
|442|0.0212|0.0208|0.0217|
|443|0.0392|0.0370|0.0384|
|444|0.7864|0.7864|0.7864|
|445|0.0529|0.0597|0.0605|
|446|0.0388|0.0345|0.0360|
|447|0.1579|0.1929|0.1859|
|448|0.0075|0.0075|0.0078|
|449|0.0399|0.0431|0.0432|
|450|0.1719|0.1928|0.1879|
|avg|0.1566|0.1620|0.1615|
+---+------+------+------+
```

Some topics scored a very high MAP across the board while others an abysmally low one.
It's a strong sign that something in our inverted index is not optimal.

Our understanding to the problem is, after analyzing some low score topics, that we do not give a higher weight to words in the title and description.
However, it is clear that the title words are much for important.
A small improvement can be made by removing the extra **description** and **narrative** entry from the topics. It increases the avg score by around $0.002$.

Examples:
Topic 401 only has a score of around 0.007.
In the topic we can see, that it talks about foreign minorities in Germany.
However the narrative talks about a new document (by the government?) which is
about immigration. The whole narrative in this topic kind of "confuses" the scorer
by using a lot of words to describe something that is only relevant if you know the
context. So the matching documents also focus on irrelevant terms like "document" and semi relevant ones like "immigration".

Topic 432 only has score of 0.0002
Similar case as above. Profiling is the most important word after police probably, however the narrative talks about different things.
Here is the topic dictionary it is mostly filled with not relevant words:
```
{   'carry': 1,
    'consider': 1,
    'contraband': 1,
    'criterion': 1,
    'department': 2,
    'description': 1,
    'detention': 1,
    'discus': 1,
    'discuss': 1,
    'document': 2,
    'force': 1,
    'foreign': 1,
    'identify': 1,
    'individual': 1,
    'likely': 1,
    'motorist': 3,
    'narrative': 1,
    'police': 3,
    'profile': 1,
    'profiling': 1,
    'relevant': 2,
    'report': 1,
    'security': 1,
    'stop': 1,
    'use': 1
}
```

### Evaluation of significance

We additionally used the R scripts to evaluate if any of the implemented scoring methods would produce significantly better results than the others.
https://github.com/geoHeil/advancedInformationRetrieval/blob/master/project1/evalR/Revaluate.R, however shows that they are not:

```
omnibus hypothesis not rejected (p = 0.154112082693036).  your systems are not statistically distinguishable!NULL`
```

### Running the project

please see the main README at the project root https://github.com/geoHeil/advancedInformationRetrieval for instructions how to run.

### Wrap-up

It was impressive to see
- how easy and fast it is to implement a fast searcher if you have an inverted index.
- the speed improvements of using a multi threaded implementation of the index which possibly would also scale well in a distributed system.
- how simple it is to parallelize operations in spark.
- the ease of performing several different NLP tasks in spaCy (tokenization, lemmatizaton, POS-tagging, ....)

### Co-Author: Georg Heiler @geoHeil
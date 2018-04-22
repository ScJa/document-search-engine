# build your own search engine.

We choose task 1.3 using python as the main programming language, but will resort to scala for the map reduce index. 

## project information

We will use spacY and NLTK for the basic libraries and coreNLP in the map reduce example.
During the development of the algorithms we used several jupyter notebooks as scratchpads to easily play with different ideas.

**to run**

- download the data from:
    -  https://dl.dropboxusercontent.com/u/17483665/TUWien/AIR/TREC8all.zip
    -  spacy model data
        
        ```
        python -m spacy download en
        ```

    -  put it into the data folder and then unzip to TREC8all
    -  install all the python dependencies listed below in the *libraries used* section via `pip install -upgrade dependencyName` for a current python (we only tested with 3.6)

- to run it execute the shell files (in the scripts folder) as outlined below after configuring parameters:
```
./scripts/indexer.sh
./scripts/searcher.sh (needs the files produced by the indexer)
```
- more detailed settings are in the readme.md in the scripts folder

**to validate via trec eval**

- prepare trec eval

```
git clone https://github.com/usnistgov/trec_eval
cd trec_eval
make
```

- to test it with the sample data execute

```
./indexer.sh
./search.sh
./trec_eval/trec_eval -q -c data/TREC8all/qrels.trec8.adhoc.parts1-5 scripts/scores_tf-idf.txt
```

## report information

we will use asciidoc to create the report via asciidoctor. Asciidoctor is a ruby gem, i.e. requries ruby to be installed.
To create the documentation run ´gem install asciidoctor´, then run `asciidoctor report/report.adoc`
However, this is only required if you want to see a nice representation / custom layout. Github will automatically perform a basic
rendering of the document for you.

## libraries used
We must build the index on our own, but it is ok to use some library to perform simple tasks (tokenization, lemmatization, data structures).

- beautifulsoup 4 to parse the SGML files
- pyfs for file handling, installed as `pip install pyfs` but used as `fs`
- spacy and their models for en as outlined at the top
- snowballstemmer
- apache spark with core-nlp for the distributed map reduce indexing. Dependencies for map reduce ar outlined in the README in the folder of *mapReduceIndexing*

## TODOs
- use an alternative index implementation (scip-lists)
- report
	- Show how the score is calculated for two documents adjacent in the ranked list

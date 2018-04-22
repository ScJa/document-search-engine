## Indexer

How to run:

$ python indexer.py [-case | -lemm | -stem | -stop] [-none]

-case turns on case-folding.
-lemm turns on the lemmatization. Does NOT work in combination with stemming.
-stem turns on stemming. Does NOT work in combination with lemmatizing.
-stop turns on the stop word filter.
                
-none turns everything OFF and only runs with basic tokens. ignores all other args


DEFAULT SETTINGS:

- case-folding OFF
- stemming OFF
- lemmatization ON
- stop word filters ON

## Searcher

$ python search.py path_to_topics

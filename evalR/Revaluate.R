# evaluation of significance
# library(CranfieldMCP) # not really working
require(lme4)
source('evalR/CranfieldMCP/R/read.eval.R')
source('evalR/CranfieldMCP/R/pairwise.test.R')

# read data
# read.eval function reads output from trec eval -q
#############
# no longer necessary, already checked in scoring results.
# tfidf:. ./trec_eval/trec_eval -q -c data/TREC8all/qrels.trec8.adhoc.parts1-5 scripts/scores_tf-idf.txt >> evals/input.tfidf.txt
# bm25:  ./trec_eval/trec_eval -q -c data/TREC8all/qrels.trec8.adhoc.parts1-5 scripts/scores_bm25.txt >> evals/input.bm25.txt
# bm25VA: TODO 
#############

res <- read.eval("evals/")

# this is throwing an error 
#  Fehler in mkRespMod(fr, REML = REMLpass) : response must be numeric 
pairwise.test(res, "map",
              H=c("S1 - S0", "S2 - S0", "S1’ - S1",
                  "S2’ - S2", "S1 - S2", "S1’ - S2’"),
              alternative="greater")


# result is:
# omnibus hypothesis not rejected (p = 0.154112082693036).  your systems are not statistically distinguishable!NULL
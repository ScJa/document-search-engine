import pickle
import spacy
import codecs
import sys
import math
import os
from bs4 import BeautifulSoup


def tf(word_occ, word_count):
    return word_occ / word_count


def idf(doc_count, contains_count):
    return math.log(doc_count / contains_count)


def avgdl(all_dwords_count, doc_count):
    return all_dwords_count / doc_count


def tf_idf(word_occ, word_count, doc_count, contains_count):
    return tf(word_occ, word_count) * idf(doc_count, contains_count)


def bm25(word_occ, word_count, doc_count, contains_count, all_dwords_count, b=0.75, k=1.2):
    return (idf(doc_count, contains_count) * (tf(word_occ, word_count) * (k + 1)) /
            (tf(word_occ, word_count) + k * (1 - b + b * word_count / avgdl(all_dwords_count, doc_count))))


mavgtf_v = None


def avgtf(word_count, unique_word_count):
    return word_count / unique_word_count


def mavgtf(doc_count):
    global mavgtf_v
    if mavgtf_v is None:
        sum_m = 0
        for docno, u_c in unique_word_counters.items():
            sum_m = sum_m + avgtf(word_counters[docno], u_c)
        mavgtf_v = sum_m / doc_count
    return mavgtf_v


def bva(word_count, doc_count, all_dwords_count, unique_word_count):
    mavgtf_l = mavgtf(doc_count)
    return (pow(mavgtf_l, -2) * avgtf(word_count, unique_word_count) + (1 - pow(mavgtf_l, -1)) *
            word_count / avgdl(all_dwords_count, doc_count))


def score_topic(topic_words, topic_word_count):
    topic_vector = {}
    for tk, tv in topic_words.items():
        if scoring_method == "tf-idf":
            topic_vector[tk] = (tf_idf(tv, topic_word_count, word_counters["doc_counter"], len(iInd[tk]) + 1))
        elif scoring_method == "bm25":
            topic_vector[tk] = (bm25(tv, topic_word_count, word_counters["doc_counter"], len(iInd[tk]) + 1,
                           word_counters["word_counter"]))
        elif scoring_method == "bm25va":
            b = bva(topic_word_count, word_counters["doc_counter"], word_counters["word_counter"], len(topic_words))
            topic_vector[tk] = (bm25(tv, topic_word_count, word_counters["doc_counter"], len(iInd[tk]) + 1,
                           word_counters["word_counter"], b))
    return topic_vector


def build_vectors(topic_words, topic_word_count):
    topic_vector = score_topic(topic_words, topic_word_count)
    topic_vector = {}
    document_vectors = {}
    for tk, tv in topic_words.items():
        if scoring_method == "tf-idf":
            topic_vector[tk] = (tf_idf(tv, topic_word_count, word_counters["doc_counter"], len(iInd[tk]) + 1))
        elif scoring_method == "bm25":
            topic_vector[tk] = (bm25(tv, topic_word_count, word_counters["doc_counter"], len(iInd[tk]) + 1,
                           word_counters["word_counter"]))
        elif scoring_method == "bm25va":
            b = bva(topic_word_count, word_counters["doc_counter"], word_counters["word_counter"], len(topic_words))
            topic_vector[tk] = (bm25(tv, topic_word_count, word_counters["doc_counter"], len(iInd[tk]) + 1,
                           word_counters["word_counter"], b))
        for dk, dv in iInd[tk].items():
            if scoring_method == "tf-idf":
                document_vectors[dk][tk] = tf_idf(dv, word_counters[dk], word_counters["doc_counter"], len(iInd[tk]) + 1)
            elif scoring_method == "bm25":
                document_vectors[dk][tk] = bm25(dv, word_counters[dk], word_counters["doc_counter"], len(iInd[tk]) + 1,
                               word_counters["word_counter"])
            elif scoring_method == "bm25va":
                b = bva(word_counters[dk], word_counters["doc_counter"], word_counters["word_counter"],
                        unique_word_counters[dk])
                document_vectors[dk][tk] = bm25(dv, word_counters[dk], word_counters["doc_counter"], len(iInd[tk]) + 1,
                               word_counters["word_counter"], b)
    return topic_vector, document_vectors


def score(topic_words, topic_word_count):
    scores_upper = {}
    vector_betrag_topic = 0
    vector_betrag_doc = {}
    for tk, tv in topic_words.items():
        if scoring_method == "tf-idf":
            t_score = tf_idf(tv, topic_word_count, word_counters["doc_counter"], len(iInd[tk]) + 1)
        elif scoring_method == "bm25":
            t_score = bm25(tv, topic_word_count, word_counters["doc_counter"], len(iInd[tk]) + 1,
                           word_counters["word_counter"])
        elif scoring_method == "bm25va":
            b = bva(topic_word_count, word_counters["doc_counter"], word_counters["word_counter"], len(topic_words))
            t_score = bm25(tv, topic_word_count, word_counters["doc_counter"], len(iInd[tk]) + 1,
                           word_counters["word_counter"], b)
        vector_betrag_topic += t_score * t_score
        for dk, dv in iInd[tk].items():
            if scoring_method == "tf-idf":
                d_score = tf_idf(dv, word_counters[dk], word_counters["doc_counter"], len(iInd[tk]) + 1)
            elif scoring_method == "bm25":
                d_score = bm25(dv, word_counters[dk], word_counters["doc_counter"], len(iInd[tk]) + 1,
                               word_counters["word_counter"])
            elif scoring_method == "bm25va":
                b = bva(word_counters[dk], word_counters["doc_counter"], word_counters["word_counter"],
                        unique_word_counters[dk])
                d_score = bm25(dv, word_counters[dk], word_counters["doc_counter"], len(iInd[tk]) + 1,
                               word_counters["word_counter"], b)
            if scores_upper.get(dk) is None:
                scores_upper[dk] = t_score * d_score
            else:
                scores_upper[dk] = scores_upper[dk] + t_score * d_score
            if vector_betrag_doc.get(dk) is None:
                vector_betrag_doc[dk] = d_score * d_score
            else:
                vector_betrag_doc[dk] = vector_betrag_doc[dk] + d_score * d_score

    # cosine similiarty
    vector_betrag_topic = math.sqrt(vector_betrag_topic)
    scores = {}
    for doc, upper in scores_upper.items():
        scores[doc] = upper / (vector_betrag_topic * math.sqrt(vector_betrag_doc[doc]))

    return scores



def output_topic(scores, topicNo):
    output_file = open('scores_{}.txt'.format(scoring_method), 'a')
    rank_counter = 1
    for score in [(k, scores[k]) for k in sorted(scores, key=scores.get, reverse=True)]:
        output_file.write("{} Q0 {} {} {} group2\n".format(topicNo, score[0], rank_counter, score[1]))
        rank_counter += 1
        if rank_counter == 1001:
            break
    output_file.close()


def process_topic(docs, topicNo):
    topic_words = {}
    word_count = 0

    for doc in docs:
        for token in doc:
            if token.is_alpha and not token.is_stop and len(token.orth_) > 1:
                word_count = word_count + 1
                strtok = token.lemma_.strip()
                if strtok not in topic_words.keys():
                    topic_words[strtok] = 1
                else:
                    topic_words[strtok] = topic_words[strtok] + 1

    scores = score(topic_words, word_count)
    output_topic(scores, topicNo)


if len(sys.argv) != 2:
    print("Please enter only the filepath to the topic as a parameter. (All topics in this file will be scored, should"
          " there be more than one)")
soup = BeautifulSoup(codecs.open(sys.argv[1], 'r', "iso-8859-1").read(), "lxml")


print("Choose a scoring method. Options are: \"tf-idf\", \"bm25\" or \"bm25va\".")
scoring_method = input()
if scoring_method != "tf-idf" and scoring_method != "bm25" and scoring_method != "bm25va":
    print("Please either enter \"tf-idf\", \"bm25\" or \"bm25va\". Exiting..")
    sys.exit(0)

if os.path.exists('scores_{}.txt'.format(scoring_method)):
    print('Output file scores_{}.txt already exists. Please delete it or specify another one.'.format(scoring_method))
    sys.exit(0)

print("All data is being loaded. This can take a few minutes.")
iInd = pickle.load(open("inv_ind_f.p", "rb"))
word_counters = pickle.load(open("word_count_f.p", "rb"))
unique_word_counters = pickle.load(open("unique_words_count_f.p", "rb"))
nlp = spacy.load('en')
print("Data loaded successfully, starting with scoring.")

for topic in soup.find_all("top"):
    topicNo = [int(s) for s in topic.num.text.split() if s.isdigit()][0]
    print("Processing topic {}.".format(topicNo))
    texts = [topic.desc.text, topic.narr.text, topic.title.text]
    topic_tokens = nlp.pipe(texts)
    process_topic(topic_tokens, topicNo)

print("All topics processed. Output can be found in \"scores_{}.txt\".".format(scoring_method))



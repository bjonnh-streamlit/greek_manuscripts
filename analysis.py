#!/usr/bin/env python3

import nltk
from nltk import ngrams
import numpy as np
import itertools
import pandas as pd

import textract
from lib.decoder import Decoder
from lib.logger import Logger

DEBUG = False


def processor(file):
    full_text = textract.process(file, extension="docx").decode('utf-8')

    logger = Logger()

    decoder = Decoder(logger)

    count = 100

    for line in full_text.splitlines():
        decoder.process_line(line, keep_full_text=True)
        if DEBUG:
            count -= 1
            if count == 0:
                break

    logger.info(f"Analyzing {file}")

    messages = ""
    for message in logger.messages:
        messages += message.__str__() + "\n"
    print(messages)

    full_text_as_list = decoder.full_text_by_section()
    print(f"We have {len(full_text_as_list)} sections.")
    data = list(itertools.chain.from_iterable(full_text_as_list))

    matrix, vocab_index = generate_co_occurrence_matrix(data, 8)
    data_matrix = pd.DataFrame(matrix, index=vocab_index, columns=vocab_index)
    words_by_occurence = data_matrix.sum(axis=0).sort_values(ascending=False)
    print(words_by_occurence[0:10])
    start_by = [word for word in words_by_occurence.index if word.startswith("πυρε")]+["ἑκτικῶν"]
    print(start_by)

    #word = "φύλλο" #words_by_occurence.index[0]
    for word in start_by:
        print(f"Top 10 words related to {word}: ")
        top10 = data_matrix[word].sort_values(ascending=False)[0:10]
        print(top10[top10 > 0])


    #nlp = spacy.load("el_core_news_lg")
    # for doc in nlp.pipe(full_text): #, disable=["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer"]):
    #     # Do something with the doc here
    #     entities = []
    #     for ent in doc.ents:
    #         if ent.text != "":
    #             print([(ent.text, ent.label_)])

    # For POS tagging
    #doc = nlp(full_text)
    #print(doc.text)
    #for token in doc:
    #    print(token.text, token.pos_, token.dep_)


# Source? somewhere online
# looks like people have copy/pasted that a lot

def combine_ngrams_to_repeated_couples(ngram, distance):
    output = []

    for i in range(1, len(ngram)):
        repeats = distance - i
        output += [(ngram[0], ngram[i])] * repeats

    return output


def generate_co_occurrence_matrix(corpus, distance):
    vocab = set(corpus)
    vocab = list(vocab)
    vocab_index = {word: i for i, word in enumerate(vocab)}

    # Create ngrams from all words in corpus
    calculated_ngrams = ngrams(corpus, distance)
    repeated_ngrams = []

    for ngram in calculated_ngrams:
        repeated_ngrams += combine_ngrams_to_repeated_couples(ngram, distance)
    for ngram in ngrams(reversed(corpus), distance):
        repeated_ngrams += combine_ngrams_to_repeated_couples(ngram, distance)

    # Frequency distribution of ngrams ((word1, word2), num_occurrences)
    ngram_freq = nltk.FreqDist(repeated_ngrams).most_common(len(repeated_ngrams))

    # Initialise co-occurrence matrix
    # co_occurrence_matrix[current][previous]
    co_occurrence_matrix = np.zeros((len(vocab), len(vocab)))

    # Loop through the ngrams taking the current and previous word,
    # and the number of occurrences of the ngram.
    for ngram in ngram_freq:
        current = ngram[0][1]
        previous = ngram[0][0]
        count = ngram[1]
        pos_current = vocab_index[current]
        pos_previous = vocab_index[previous]
        co_occurrence_matrix[pos_current][pos_previous] = count
    co_occurrence_matrix = np.matrix(co_occurrence_matrix)

    # return the matrix and the index
    return co_occurrence_matrix, vocab_index


def __main__():
    processor("./data/Galen Simpl Med 06-08 checked December 10 2021.docx")
    #print(combine_ngrams_to_repeated_couples(["1", "2", "3", "4"], 4))


if __name__ == '__main__':
    __main__()

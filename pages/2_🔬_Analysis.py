#!/usr/bin/env python3
import tempfile

import nltk
from nltk import ngrams
import numpy as np
import itertools
import pandas as pd

import textract
from lib.decoder import Decoder
from lib.logger import Logger

import streamlit as st

from lib.reference import Reference

DEBUG = False
logger = Logger()



st.set_page_config(
    page_title="Analysis",
    page_icon="🔬",
    layout="wide"
)

def processor(file):
    full_text = textract.process(file, extension="docx").decode('utf-8')

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
    logger.info(messages)

    full_text_as_list = decoder.full_text_by_section()
    logger.info(f"We have {len(full_text_as_list)} sections.")
    data = list(itertools.chain.from_iterable(full_text_as_list))

    matrix, vocab_index = generate_co_occurrence_matrix(data, 8)
    data_matrix = pd.DataFrame(matrix, index=vocab_index, columns=vocab_index)
    words_by_occurence = data_matrix.sum(axis=0).sort_values(ascending=False)

    return decoder, words_by_occurence, data_matrix

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


st.title("Greek manuscript analyzer")


uploaded_file = st.file_uploader('Manuscript file', type='docx', help='Please upload a manuscript file in the right format')

@st.experimental_memo
def process_data(uploaded_file_name):
    logger.info(f"Opening {uploaded_file_name}")
    with tempfile.NamedTemporaryFile() as in_file:
        in_file.write(uploaded_file.read())
        in_file.flush()
        decoder, words_by_occurence, data_matrix = processor(in_file.name)
        return decoder.state, words_by_occurence, data_matrix


if uploaded_file is not None:
    st.session_state['uploaded_file'] = uploaded_file.name

    st.write("Uploaded file:", uploaded_file.name)

    decoder_state, words_by_occurence, data_matrix = process_data(uploaded_file.name)
    sections = list(decoder_state.sections)
    sections.sort()

    selected_section = st.selectbox('Section', sections)
    subsections = list(decoder_state.subsections[selected_section])
    subsections.sort()
    selected_subsection = st.selectbox('Subsection', subsections)

    text = decoder_state.full_text[Reference(selected_section, selected_subsection)]

    st.subheader("Text")
    st.write(" ".join(text))
    st.subheader("Top 10 words")
    st.dataframe(words_by_occurence)
    st.subheader("Word lookup")
    word_lookup = st.text_input("Word to lookup", "")
    if word_lookup != '' and word_lookup in data_matrix.index:
        top10 = data_matrix[word_lookup].sort_values(ascending=False)[0:10]
        st.write(f"Top 10 words related to {word_lookup}")
        st.dataframe(top10[top10 > 0])



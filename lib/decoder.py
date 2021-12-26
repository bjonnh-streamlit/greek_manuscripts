import os.path
from collections import defaultdict
from itertools import groupby

from cltk.alphabet.text_normalization import cltk_normalize
from cltk.lemmatize import GreekBackoffLemmatizer
from cltk.data.fetch import FetchCorpus

from .reference import Reference

from greek_accentuation.characters import base

import re

# Sections are either enclosed in [] or starting with vol
regexp_section = re.compile(r"((^\[.*]$)|(^vol.*$))")
regexp_line = re.compile(r"([\d.]*)(\s?)(.*)")
regexp_removechars = re.compile(r"[,\.:·\[\]]*")

def greek_word_basifier(word):
    """A function that helps sorting words by their base letters not diacritics ones
    We add the word at the end to have a correct ordering."""
    str_word = str(word)
    sort_key = "".join([base(ch) for ch in str_word]) + str_word
    return sort_key


class Decoder:
    def __init__(self):
        self.section = ""
        self.subsection = ""
        self.line_counter = 1
        self.nlp = None

        # word to positions as list
        self.word_occurrences = defaultdict(list)

        # reversed index
        self.reversed_word_occurrences = defaultdict(list)

    def set_section(self, section):
        self.section = section.replace("[", "").replace("]", "")

    def current_reference(self):
        return Reference(self.section, self.subsection, self.line_counter)

    def process_text_line(self, text_line):
        words = text_line.split()
        for word in words:
            cleaned_word = re.sub(regexp_removechars, "", word).strip()
            if cleaned_word != "":
                self.word_occurrences[cleaned_word].append(self.current_reference())
                self.reversed_word_occurrences[cleaned_word[::-1]].append(self.current_reference())

    def process_line(self, _line):
        clean_line = _line.strip()
        if clean_line == "":
            return

        line_match = regexp_line.match(_line)
        if regexp_section.match(clean_line):
            self.set_section(clean_line)
            self.line_counter = 0
        elif line_match:
            self.line_counter += 1
            subsection = line_match.group(1)
            if subsection != "":
                self.subsection = subsection
            self.process_text_line(line_match.group(3).strip())
        else:
            print(f"Can't handle {clean_line}")

    @staticmethod
    def nice_printer_references(content):
        """Prints the sections only when it is a new one."""
        output = ""
        for thing in groupby(content, lambda entry: entry.subsection):
            list_of_subref = [f"{ref.section}.{ref.line}" for ref in thing[1]]
            output += f"{thing[0]} ({' ‖ '.join(list_of_subref)})"
        return output

    def word_info(self, word, source):
        content = source[word]

        return f"({len(content)}) {self.nice_printer_references(content)}"

    def index(self, reverse=False):
        if reverse:
            source = self.reversed_word_occurrences
        else:
            source = self.word_occurrences

        for word in sorted(source.keys(), key=lambda kv: greek_word_basifier(kv)):
            yield word, self.word_info(word, source)

    def count(self):
        counts = {}

        for word in self.word_occurrences.keys():
            counts[word] = len(self.word_occurrences[word])
        # We have to use a little trick here as we want to reverse the numbers but not the words.
        return sorted(counts.items(), key=lambda kv: (-kv[1], greek_word_basifier(kv[0])))

    def lemma(self, debug=False):
        """Produce the lemmatized sorted output"""
        corpus_downloader = FetchCorpus(language="grc")
        corpus_downloader.import_corpus("grc_models_cltk")

        lemmatizer = GreekBackoffLemmatizer()
        output = defaultdict(set)

        words = set()
        for word in self.word_occurrences.keys():
            words.add(cltk_normalize(word))
        if debug:
            print(f" Normalized, found {len(words)} unique words")
        for word in words:
            lemma = lemmatizer.lemmatize([word])[0]
            output[lemma[1]].add(word)

        output_sorted = [(entry[0], sorted(entry[1], key=lambda kv: greek_word_basifier(kv))) for entry in
                         sorted(output.items(), key=lambda kv: greek_word_basifier(kv[0]))]
        return output_sorted
import hashlib
from collections import defaultdict
from itertools import groupby
import itertools
from typing import Optional

from cltk.alphabet.text_normalization import cltk_normalize
from cltk.lemmatize import GreekBackoffLemmatizer
from cltk.data.fetch import FetchCorpus

from .decoder_state import DecoderState
from .logger import Logger
from .normalizer import Normalizer
from .reference import Reference

from greek_accentuation.characters import base

import re

from pyuca import Collator

from lib.validator import Validator

# Sections are either enclosed in [] or starting with vol
regexp_section = re.compile(r"((^\[.*]$)|(^vol.*$))")
regexp_line = re.compile(r"([\d.]*)(\s?)(.*)")  # Numbers in the form xxx(.yyy.zzz...) are sub sections the rest is text
regexp_removechars = re.compile(r"[,\.:·\[\]]*")
regexp_removechars_nlp = re.compile(r"[:·\[\]]*")

basifier_cache = {}
all_letters = set()
# Some words used internally for sections etc
excluded_words = {"tit", "sec"}


def greek_word_basifier(word):
    """A function that helps to sort words by their base letters not diacritics ones
    We add the word at the end to have a correct ordering."""
    if word in basifier_cache:
        return basifier_cache[word]

    str_word = str(word)
    word = ""
    for ch in str_word:
        bch = base(ch)
        if bch in ["α", "ε", "ι", "ο"]:
            if ch in ["ά", "έ", "ί", "ό"]:
                word += f"{bch}·10"  # Big cheat here, but we want to be able to sort things properly and natural sorting doesn't
            elif ch in ["ὰ", "ὲ", "ὶ", "ὸ"]:
                word += f"{bch}·11"
            elif ch in ["α", "ε", "ι", "ο"]:
                word += f"{bch}·12"

        elif bch in ["Α", "Ν", "Β", "Ξ", "Γ", "Ο", "Δ", "Π", "Ε", "Ρ", "Ζ", "Σ", "Η", "Τ", "Θ", "Υ", "Ι", "Φ", "Κ",
                     "Χ", "Λ", "Ψ", "Μ", "Ω"]:
            word += f"{bch}ααα"
        else:
            word += bch
    sort_key = word + " " + str_word

    basifier_cache[word] = sort_key
    return sort_key


class Decoder:
    def __init__(self, logger: Optional[Logger] = None):
        if logger is None:
            logger = Logger()

        self.state = DecoderState()
        self.normalizer = Normalizer()

        self.logger = logger
        self.validator = Validator()

        # Current section
        self.section = ""
        # Current subsection
        self.subsection = ""
        self.line_counter = 1
        self.nlp = None

        self._current_reference = None
        self._short_current_reference = None

        self.unfinished_word = ""

    def set_title(self, title):
        self.state.title = title


    def full_text(self):
        return " ".join(itertools.chain(*self.state.full_text.values()))

    def full_text_by_section(self):
        old_section = None
        blocks = []
        current_block = []
        for reference in self.state.full_text.keys():
            if reference.section != old_section:
                old_section = reference.section
                if len(current_block) > 0:
                    blocks.append(current_block)
                current_block = []
            current_block += self.state.full_text[reference]

        return blocks

    def set_section(self, section):
        self.section = section.replace("[", "").replace("]", "")
        self.reset_unfinished_word()

    def set_subsection(self, subsection):
        self.subsection = subsection
        self.reset_unfinished_word()

    def reset_unfinished_word(self):
        self.unfinished_word = ""

    # Computes and store the current reference in self._current_reference
    # it stores a reference to the section and subsection as well in self._short_current_reference
    # and we keep a list of all references in self.short_references
    def set_current_reference(self) -> None:
        local_ref = Reference(self.section, self.subsection, self.line_counter)
        short_local_ref = Reference(self.section, self.subsection)
        if self._current_reference != local_ref:
            self._current_reference = local_ref
        if self._short_current_reference != short_local_ref:
            self._short_current_reference = short_local_ref
            self.state.short_references.append(self._short_current_reference)
            self.state.sections.add(short_local_ref.section)
            self.state.subsections[short_local_ref.section].add(short_local_ref.subsection)

    def process_text_line(self, text_line, keep_full_text=False):
        self.set_current_reference()

        words = text_line.split()
        for pre_word in words:
            word = self.normalizer.process(pre_word)
            valid = self.validator.validate(word)
            if valid is not True:
                self.logger.error(f"Invalid string {valid} in word {word} at {self._current_reference}")

            cleaned_word = re.sub(regexp_removechars, "", word).strip()

            if (cleaned_word != "") and (cleaned_word not in excluded_words):
                self.state.word_occurrences[cleaned_word].append(self._current_reference)
                self.state.reversed_word_occurrences[cleaned_word[::-1]].append(self._current_reference)
                if cleaned_word == "δήξεως":
                    print(f"Adding δήξεως section {self._current_reference} {self._short_current_reference}")
                if keep_full_text:
                    self.state.full_text[self._short_current_reference].append(cleaned_word)
                    self.state.full_text_word_linked[self._short_current_reference].append((word, cleaned_word))

    def process_line(self, _line, keep_full_text=False):
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
                self.set_subsection(subsection)

            text_line = line_match.group(3).strip().split(" ")
            # We append the unfinished word on next line
            if len(text_line) > 0 and self.unfinished_word != "":
                text_line[0] = self.unfinished_word + text_line[0]

            # If line ends by -, we have to keep that word and join it to the next line
            if text_line[-1][-1] == "-":
                self.unfinished_word = text_line[-1].rstrip("-")
                text_line = text_line[:-1]
            self.process_text_line(" ".join(text_line), keep_full_text=keep_full_text)
        else:
            self.logger.error(f"Can't handle {clean_line}")

    def count(self):
        counts = {}

        for word in self.state.word_occurrences.keys():
            counts[word] = len(self.state.word_occurrences[word])
        # We have to use a little trick here as we want to reverse the numbers but not the words.
        return sorted(counts.items(), key=lambda kv: (-kv[1], self.state.pyuca_collator.sort_key(kv[0])))

    def lemma(self, debug=False):
        """Produce the lemmatized sorted output"""
        corpus_downloader = FetchCorpus(language="grc")
        corpus_downloader.import_corpus("grc_models_cltk")

        lemmatizer = GreekBackoffLemmatizer()
        output = defaultdict(set)

        words = set()
        for word in self.state.word_occurrences.keys():
            words.add(cltk_normalize(word))
        if debug:
            self.logger.info(f" Normalized, found {len(words)} unique words")
        for word in words:
            lemma = lemmatizer.lemmatize([word])[0]
            output[lemma[1]].add(word)

        output_sorted = [(entry[0], sorted(entry[1], key=self.state.pyuca_collator.sort_key)) for entry in
                         sorted(output.items(), key=lambda kv: self.state.pyuca_collator.sort_key(kv[0]))]
        return output_sorted

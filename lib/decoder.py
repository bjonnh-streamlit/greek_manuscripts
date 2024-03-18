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

        self.pyuca_collator = Collator()

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

        # word to positions as list
        self.word_occurrences = defaultdict(list)

        # reversed index
        self.reversed_word_occurrences = defaultdict(list)

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
                self.word_occurrences[cleaned_word].append(self._current_reference)
                self.reversed_word_occurrences[cleaned_word[::-1]].append(self._current_reference)
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

    @staticmethod
    def nice_printer_references(content):
        """Prints the sections only when it is a new one."""
        output = []
        for thing in groupby(content, lambda entry: entry.subsection):
            list_of_subref = [f"{ref.section}.{ref.line}" for ref in thing[1]]
            output += [f"{thing[0]} ({' ‖ '.join(list_of_subref)})"]
        return "; ".join(output) + "."

    def word_info(self, word, source, raw=False):
        content = source[word]
        if raw:
            return {"count": len(content), "references": content}
        else:
            return f"({len(content)}) − {self.nice_printer_references(content)}"

    def index(self, reverse=False, raw=False):
        if reverse:
            source = self.reversed_word_occurrences
        else:
            source = self.word_occurrences

        for word in sorted(source.keys(), key=self.pyuca_collator.sort_key):
            yield word, self.word_info(word, source, raw)

    def count(self):
        counts = {}

        for word in self.word_occurrences.keys():
            counts[word] = len(self.word_occurrences[word])
        # We have to use a little trick here as we want to reverse the numbers but not the words.
        return sorted(counts.items(), key=lambda kv: (-kv[1], self.pyuca_collator.sort_key(kv[0])))

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
            self.logger.info(f" Normalized, found {len(words)} unique words")
        for word in words:
            lemma = lemmatizer.lemmatize([word])[0]
            output[lemma[1]].add(word)

        output_sorted = [(entry[0], sorted(entry[1], key=self.pyuca_collator.sort_key)) for entry in
                         sorted(output.items(), key=lambda kv:self.pyuca_collator.sort_key(kv[0]))]
        return output_sorted

    def to_html(self):
        content = ""
        content += "<h2>Text</h2>"
        print(self.state.full_text_word_linked.keys())
        for reference in self.state.full_text_word_linked.keys():
            current_block = self.state.full_text_word_linked[reference]
            content += f"<a name=\"sec_{reference.section}_{reference.subsection}\"><h3>{reference.nice_print()}</h3></a>\n"
            for word in current_block:
                content += f"<a href=\"#word_{word[1]}\">{word[0]} </a>"

        content += "<h2>Index</h2>\n"
        for word, word_info in self.index(raw=True):
            content += f"\n<a name=\"word_{word}\"><h3>{word}</h3></a>\n"
            content += f"<p>{word_info['count']} occurrences<br>"
            for thing in groupby(word_info["references"], lambda entry: entry.subsection):
                list_of_subref = [f"<a class=\"underlined\" onclick=\"highlightLinks('#word_{word}')\" href=\"#sec_{ref.section}_{ref.subsection}\">{ref.section}.{ref.line}</a>" for ref in thing[1]]
                content += "; ".join([f"{thing[0]} ({' ‖ '.join(list_of_subref)})"]) + " - "
            content += "</p>"

        html_document = f"""<!DOCTYPE html>
<html>
<head>
    <title>Document</title>
    <style>
       a {{
            text-decoration: none;
            color: black; 
        }}
        a:hover {{
            color: #AAAAFF;
        }}
        .underlined {{ 
            text-decoration: underline; 
            color: #AAAAAA;
        }}
        .highlighted {{
            background-color: yellow;
        }}
    </style>
</head>
<body>
    {content}
</body>
<script>
function highlightLinks(href) {{
    var links = document.getElementsByTagName('a');

    // Iterate over the links
    for (var i = 0; i < links.length; i++) {{
        // Check if the link's text matches the input text
        if (links[i].getAttribute('href') === href) {{
            links[i].classList.add('highlighted');
        }} else {{
            links[i].classList.remove('highlighted');
        }}
    }}
}}
</script>
</html>"""
        return html_document


# Missing ref: 08.16.08 (12.096.15)

import textract
from enum import Enum
import re
from collections import defaultdict
from cltk import NLP

FILE = "data/Galen Simpl Med 01 (Convert'd) Books 06-11.doc"

# Sections are either enclosed in [] or starting with vol
regexp_section = re.compile(r"((^\[.*\]$)|(^vol.*$))")
regexp_line = re.compile(r"([\d\.]*)(\s?)(.*)")


class DecoderStates(Enum):
    UNKNOWN = 0
    IN_SECTION = 1
    IN_TEXT = 2
    IN_SUBSECTION = 3


class Decoder:
    ALLOWED_STATES_TRANSITIONS = {
        DecoderStates.UNKNOWN: [DecoderStates.IN_SECTION],
        DecoderStates.IN_SECTION: [DecoderStates.IN_SUBSECTION],
        DecoderStates.IN_TEXT: []
    }
    nlp = NLP(language='grc')

    def __init__(self):
        self.STATE = DecoderStates.UNKNOWN
        self.section = ""
        self.subsection = ""
        self.line_counter = 1

        # word to positions as list
        self.word_occurrences = defaultdict(list)

        # reversed index
        self.reversed_word_occurrences = defaultdict(list)

    def set_section(self, section):
        self.section = section.replace("[", "").replace("]", "")

    def current_reference(self):
        return f"{self.subsection} ({self.section}.{self.line_counter})"

    def lemmatize(self, text):
        print(text)
        print(self.nlp.analyze(text).lemmata)

    def process_textline(self, textline):
        words = textline.split()
        for word in words:
            cleaned_word = word.replace(",", "").replace(".", "").replace(":", "").replace("·", "").strip()
            if cleaned_word != "":
                self.word_occurrences[cleaned_word].append(self.current_reference())
                self.reversed_word_occurrences[cleaned_word[::-1]].append(self.current_reference())

    def process_line(self, line, with_lemmatization=False):
        clean_line = line.strip()
        if clean_line == "":
            return

        line_match = regexp_line.match(line)
        if regexp_section.match(clean_line):
            self.set_section(clean_line)
            self.line_counter = 0
        elif line_match:
            self.line_counter += 1
            subsection = line_match.group(1)
            if subsection != "":
                self.subsection = subsection
            self.process_textline(line_match.group(3).strip())
            if with_lemmatization:
                self.lemmatize(line)
        else:
            print(f"Can't handle {clean_line}")

    def word_info(self, word, source):
        content = source[word]

        return f"{word}: ({len(content)}) {', '.join(content)}"

    def index(self, reversed=False):
        if reversed:
            source = self.reversed_word_occurrences
        else:
            source = self.word_occurrences

        for word in sorted(source.keys()):
            print(decoder.word_info(word, source))

    def count(self):
        counts = {}

        for word in self.word_occurrences.keys():
            counts[word] = len(self.word_occurrences[word])
        return sorted(counts.items(), key=lambda kv: kv[1], reverse=True)


text = textract.process(FILE).decode('utf-8')

decoder = Decoder()

for line in text.splitlines():
    decoder.process_line(line, with_lemmatization=False)

# Processing of Galien takes ~ 3s
# Lemmatization of Galien takes ~ 22min

# for it in decoder.count()[0:100]:
#    print(it)

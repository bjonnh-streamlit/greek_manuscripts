import textract
from cltk.lemmatize import GreekBackoffLemmatizer
from docx import Document
from docx.enum.section import WD_SECTION_START
from cltk.alphabet.text_normalization import cltk_normalize
from enum import Enum
import re
from collections import defaultdict
from docx.shared import Pt

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

    def __init__(self):
        self.STATE = DecoderStates.UNKNOWN
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
        return f"{self.subsection} ({self.section}.{self.line_counter})"

    def lemma(self, debug=False):
        lemmatizer = GreekBackoffLemmatizer()
        output = defaultdict(set)
        total = len(self.word_occurrences)

        words = set()
        for word in self.word_occurrences.keys():
            words.add(cltk_normalize(word))
        if debug:
            print(f" Normalized, found {len(words)} unique words")
        for word in words:
            lemma = lemmatizer.lemmatize([word])[0]
            output[lemma[1]].add(word)

        return sorted(output.items())

    def process_textline(self, textline):
        words = textline.split()
        for word in words:
            cleaned_word = word.replace(",", "").replace(".", "").replace(":", "").replace("·", "").strip()
            if cleaned_word != "":
                self.word_occurrences[cleaned_word].append(self.current_reference())
                self.reversed_word_occurrences[cleaned_word[::-1]].append(self.current_reference())

    def process_line(self, line):
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
        else:
            print(f"Can't handle {clean_line}")

    def word_info(self, word, source):
        content = source[word]

        return f"({len(content)}) {', '.join(content)}"

    def index(self, reversed=False):
        if reversed:
            source = self.reversed_word_occurrences
        else:
            source = self.word_occurrences

        for word in sorted(source.keys()):
            yield word, decoder.word_info(word, source)

    def count(self):
        counts = {}

        for word in self.word_occurrences.keys():
            counts[word] = len(self.word_occurrences[word])
        return sorted(counts.items(), key=lambda kv: kv[1], reverse=True)


WNS_COLS_NUM = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}num"


class DocxGenerator:
    def __init__(self, filename):
        self.filename = filename

    def __enter__(self):
        document = Document()
        style = document.styles["Normal"]
        font = style.font
        font.name = "Galatia sil"
        font.size = Pt(10.5)

        section = document.add_section(WD_SECTION_START.CONTINUOUS)
        section._sectPr.xpath("./w:cols")[0].set(WNS_COLS_NUM, str(2))
        self.p = document.add_paragraph()
        self.document = document
        return self

    def write(self, text, bold=False):
        out = self.p.add_run(text)
        if bold:
            out.bold = True

    def __exit__(self, type, value, traceback):
        self.document.save(self.filename)


text = textract.process(FILE).decode('utf-8')

decoder = Decoder()

for line in text.splitlines():
    decoder.process_line(line)

# Processing of Galien takes ~ 3s
# Lemmatization of Galien takes ~ 22min

# for it in decoder.count()[0:100]:
#    print(it)


print("Generating direct index")
with DocxGenerator("out/index.docx") as generator:
    for i in decoder.index():
        generator.write(i[0], bold=True)
        generator.write(f": {i[1]}\n")

print("Generating inverted index")
with DocxGenerator("out/index_inverse.docx") as generator:
    for i in decoder.index(reversed=True):
        generator.write(i[0], bold=True)
        generator.write(f": {i[1]}\n")

print("Generating frequency list")
with DocxGenerator("out/frequency.docx") as generator:
    for i in decoder.count():
        generator.write(i[0], bold=True)
        generator.write(f": {i[1]}\n")

print("Generating lemma list")
with DocxGenerator("out/lemma.docx") as generator:
    generator.write("Generated with the CLTK Backoff Lematizer\n\n", bold=True)
    for i in decoder.lemma(debug=True):
        generator.write(i[0], bold=True)
        generator.write(f": {', '.join(i[1])}\n")

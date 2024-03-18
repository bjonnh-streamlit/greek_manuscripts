# Yes some may be the same on each side, that's to facilitate when we need to add an entry
import textract

from lib.decoder import Decoder
from lib.docxgenerator import DocxGenerator
from lib.normalizer import Normalizer

if __name__ == "__main__":
    file = "data/Galen Simpl Med 06-08 checked December 10 2021.doc"
    print(file)
    full_text = textract.process(file, extension="doc").decode('utf-8')
    normalizer = Normalizer()

    full_text = normalizer.process(full_text)
    with DocxGenerator(file.replace(".doc", "_cleaned_20240317.doc"), two_columns=False) as doc:
        doc.write(full_text)
    decoder = Decoder()

    for line in full_text.splitlines():
        decoder.process_line(line, keep_full_text=True)
    for word, positions in decoder.word_occurrences.items():
        for char in word:
            if char not in normalizer.LEGIT_CHARS:
                print(f"Invalid character {char} ORD={ord(char)} in word {word}")
                for position in positions:
                    print(f"  at section {position.section} subsection {position.subsection} line {position.line}")

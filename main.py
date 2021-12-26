import os
from zipfile import ZipFile
import sys

import textract
from lib.decoder import Decoder
from lib.docxgenerator import DocxGenerator

FILE = sys.argv[1]
# Limits the output files size so they are easier to look through
DEBUG = False

full_text = textract.process(FILE).decode('utf-8')

decoder = Decoder()

count = 100

for line in full_text.splitlines():
    decoder.process_line(line)
    if DEBUG:
        count -= 1
        if count == 0:
            break

os.makedirs("out", exist_ok=True)

print("Generating direct index")
with DocxGenerator("out/index.docx") as generator:
    for i in decoder.index():
        generator.write(i[0], bold=True)
        generator.write(f": {i[1]}")
        generator.new_paragraph()

print("Generating inverted index")
with DocxGenerator("out/index_inverse.docx") as generator:
    for i in decoder.index(reverse=True):
        generator.write(i[0], bold=True)
        generator.write(f": {i[1]}")
        generator.new_paragraph()

print("Generating frequency list")
with DocxGenerator("out/frequency.docx") as generator:
    for i in decoder.count():
        generator.write(i[0], bold=True)
        generator.write(f": {i[1]}")
        generator.new_paragraph()

print("Generating lemma list")
with DocxGenerator("out/lemma.docx") as generator:
    for i in decoder.lemma(debug=True):
        generator.write(i[0], bold=True)
        generator.write(f": {', '.join(i[1])}")
        generator.new_paragraph()

ZIPFILENAME = os.path.splitext(FILE)[0] + ".zip"

with ZipFile(ZIPFILENAME, "w") as myzip:
    myzip.write("out/index.docx", arcname="index.docx")
    myzip.write("out/index_inverse.docx", arcname="index_inverse.docx")
    myzip.write("out/frequency.docx", arcname="frequency.docx")
    myzip.write("out/lemma.docx", arcname="lemma.docx")
    myzip.write(FILE, arcname=os.path.basename(FILE))

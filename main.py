#!/usr/bin/env python3
import os
from zipfile import ZipFile
import sys

import textract
from lib.decoder import Decoder
from lib.docxgenerator import DocxGenerator
from lib.logger import Logger

FILE = sys.argv[1]
OUT = sys.argv[2]
# Limits the output files size so they are easier to look through
DEBUG = False

full_text = textract.process(FILE).decode('utf-8')

logger = Logger()
logger.set_hook(lambda logentry: print(logentry))
decoder = Decoder(logger)

count = 100

for line in full_text.splitlines():
    decoder.process_line(line)
    if DEBUG:
        count -= 1
        if count == 0:
            break

os.makedirs("out", exist_ok=True)
logger.info(f"Analyzing {FILE}")
logger.info("Generating direct index")
with DocxGenerator(f"{OUT}/index.docx") as generator:
    for i in decoder.index():
        generator.write(i[0], bold=True)
        generator.write(f": {i[1]}")
        generator.new_paragraph()

logger.info("Generating inverted index")
with DocxGenerator(f"{OUT}/index_inverse.docx") as generator:
    for i in decoder.index(reverse=True):
        generator.write(i[0], bold=True)
        generator.write(f": {i[1]}")
        generator.new_paragraph()

logger.info("Generating frequency list")
with DocxGenerator(f"{OUT}/frequency.docx") as generator:
    for i in decoder.count():
        generator.write(i[0], bold=True)
        generator.write(f": {i[1]}")
        generator.new_paragraph()

logger.info("Generating lemma list")
with DocxGenerator(f"{OUT}/lemma.docx") as generator:
    for i in decoder.lemma(debug=True):
        generator.write(i[0], bold=True)
        generator.write(f": {', '.join(i[1])}")
        generator.new_paragraph()

ZIPFILENAME = OUT + "/" + os.path.split(os.path.splitext(FILE)[0])[-1] + ".zip"

with ZipFile(ZIPFILENAME, "w") as myzip:
    myzip.write(f"{OUT}/index.docx", arcname="index.docx")
    myzip.write(f"{OUT}/index_inverse.docx", arcname="index_inverse.docx")
    myzip.write(f"{OUT}/frequency.docx", arcname="frequency.docx")
    myzip.write(f"{OUT}/lemma.docx", arcname="lemma.docx")
    myzip.write(FILE, arcname=os.path.basename(FILE))

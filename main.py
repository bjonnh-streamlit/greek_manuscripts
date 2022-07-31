#!/usr/bin/env python3
import os
import io
import time
from zipfile import ZipFile
import tempfile
import sys

import textract
from lib.decoder import Decoder
from lib.docxgenerator import DocxGenerator
from lib.logger import Logger

import streamlit as st

# Limits the output files size so they are easier to look through
DEBUG = False


def processor(file, original_file_name, out):
    output_zip = io.BytesIO()
    full_text = textract.process(file, extension="docx").decode('utf-8')

    log_file = open(f"{out}/log.txt", "w")
    logger = Logger()

    def write_log(logentry):
        log_file.write(logentry.__str__())

    logger.set_hook(lambda logentry: write_log(logentry))
    decoder = Decoder(logger)

    count = 100

    for line in full_text.splitlines():
        decoder.process_line(line)
        if DEBUG:
            count -= 1
            if count == 0:
                break

    logger.info(f"Analyzing {original_file_name}")
    logger.info("Generating direct index")
    with DocxGenerator(f"{out}/index.docx") as generator:
        for i in decoder.index():
            generator.write(i[0], bold=True)
            generator.write(f": {i[1]}")
            generator.new_paragraph()

    logger.info("Generating inverted index")
    with DocxGenerator(f"{out}/index_inverse.docx") as generator:
        for i in decoder.index(reverse=True):
            generator.write(i[0], bold=True)
            generator.write(f": {i[1]}")
            generator.new_paragraph()

    logger.info("Generating frequency list")
    with DocxGenerator(f"{out}/frequency.docx") as generator:
        for i in decoder.count():
            generator.write(i[0], bold=True)
            generator.write(f": {i[1]}")
            generator.new_paragraph()

    logger.info("Generating lemma list")
    with DocxGenerator(f"{out}/lemma.docx") as generator:
        for i in decoder.lemma(debug=True):
            generator.write(i[0], bold=True)
            generator.write(f": {', '.join(i[1])}")
            generator.new_paragraph()

    log_file.close()
    myzip = ZipFile(output_zip, "w")
    myzip.write(f"{out}/index.docx", arcname="index.docx")
    myzip.write(f"{out}/index_inverse.docx", arcname="index_inverse.docx")
    myzip.write(f"{out}/frequency.docx", arcname="frequency.docx")
    myzip.write(f"{out}/lemma.docx", arcname="lemma.docx")
    myzip.write(f"{out}/log.txt", arcname="log.txt")
    myzip.write(file, arcname=original_file_name)

    st.download_button("Download zip file with processed document", output_zip,
                        file_name=original_file_name.replace("doc", "zip"))
    messages = ""
    for message in logger.messages:
        messages += message.__str__() + "\n"
    st.code(messages)


st.title("Greek manuscript processor")


uploaded_file = st.file_uploader("Manuscript file", type="docx", help="Please upload a manuscript file in the right format")

if uploaded_file is not None:
    def process_streamlit():
        with tempfile.TemporaryDirectory() as out:
            with tempfile.NamedTemporaryFile() as in_file:
                in_file.write(uploaded_file.read())
                in_file.flush()
                processor(in_file.name, uploaded_file.name, out)
    process = st.button("Process", on_click=process_streamlit)

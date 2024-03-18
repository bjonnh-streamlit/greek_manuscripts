import textract

from lib.decoder import Decoder

decoder = Decoder()
file = "data/Galen Simpl Med 06-08 checked December 10 2021.doc"
print(file)
full_text = textract.process(file, extension="doc").decode('utf-8')

for line in full_text.splitlines():
    decoder.process_line(line, keep_full_text=True)

with open(file.replace("doc", "html"), "w") as f:
    f.write(decoder.to_html())


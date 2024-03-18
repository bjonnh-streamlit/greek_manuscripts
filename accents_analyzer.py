#!/usr/bin/env python3
import greek_accentuation.characters
from cltk.alphabet.text_normalization import cltk_normalize
import textract
from itertools import groupby

def lye(c):
    return greek_accentuation.characters.base(c)

full_text = textract.process("data/Galen Simpl Med 06-08 checked December 10 2021.doc").decode('utf-8')
#full_text += textract.process("data/Galen Simpl Med 09-11 checked December 10 2021.doc").decode('utf-8')
chars = set(full_text)-{str(i) for i in range(0, 10)} - {".", ";", " ", ",", "'", "[", "]", "-", "\n"}

print(f"We have {len(chars)} unique characters that are not numbers or standard punctuation")

chars_normalized = {cltk_normalize(char) for char in chars}

invalids = []
for char in chars:
    if char != cltk_normalize(char):
        print(f" {char} (ord={ord(char)}) -> {cltk_normalize(char)} (ord={[ord(i) for i in cltk_normalize(char)]})")

    if ord(lye(cltk_normalize(char))[0]) == 32:
        invalids += char

print("Invalids:")
print(invalids)

print(f"We have {len(chars_normalized)} unique characters after normalization")


chars_normalized_sorted = sorted(chars_normalized, key=lye)

for key,value in groupby(chars_normalized_sorted, lye):
    print([ord(c) for c in key])
    values = list(value)
    print(key + " : " + "  -  ".join(values))
    print(values)

import unittest
from lib.decoder import Decoder

class Replacement(unittest.TestCase):
    def test_replacement_word(self):
        decoder = Decoder()
        decoder.process_text_line("a,b.c·d[e]f:g")
        self.assertListEqual(["abcdefg"], list(decoder.word_occurrences.keys()))

if __name__ == '__main__':
    unittest.main()

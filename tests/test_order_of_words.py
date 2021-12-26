import unittest

from lib.decoder import greek_word_basifier, Decoder


class TestOrder(unittest.TestCase):
    def test_order(self):
        self.assertEqual(["ἀγρία","ἀγρίας"], sorted(["ἀγρία", "ἀγρίας"]))
        self.assertEqual(["ἀγρία","ἀγρίας"], sorted(["ἀγρίας", "ἀγρία"]))

    def test_with_basifier(self):
        decoder = Decoder()
        decoder.process_text_line("ἀγρία ἀγρίας")
        out = list(decoder.index())
        self.assertEqual("ἀγρία", out[0][0])

if __name__ == '__main__':
    unittest.main()

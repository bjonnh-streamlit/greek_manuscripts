import unittest
from lib.decoder import Decoder


class TestCleanup(unittest.TestCase):
    def test_filtered_words(self):
        decoder = Decoder()
        decoder.process_text_line("foo bar tit")
        self.assertListEqual(["foo", "bar"], list(decoder.word_occurrences.keys()))


if __name__ == '__main__':
    unittest.main()

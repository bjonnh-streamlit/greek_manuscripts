import unittest
from lib.decoder import Decoder


class TestCesure(unittest.TestCase):
    def test_cesure(self):
        decoder = Decoder()
        decoder.process_line("ἀγρία γρ-")
        decoder.process_line("ίας")
        out = list(decoder.index())
        self.assertEqual("ἀγρία", out[0][0])
        self.assertEqual("γρίας", out[1][0])


if __name__ == '__main__':
    unittest.main()

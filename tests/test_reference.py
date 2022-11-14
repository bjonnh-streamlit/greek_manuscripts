import unittest
from lib.decoder import Reference


class TestReference(unittest.TestCase):
    def test_section(self):
        reference = Reference("1")
        self.assertEqual(reference.__str__(), "1")

    def test_subsection(self):
        reference = Reference("1", "2")
        self.assertEqual(reference.__str__(), "1 (2)")

    def test_line(self):
        reference = Reference("1", "2", 3)
        self.assertEqual(reference.__str__(), "1 (2.3)")

    def test_word(self):
        reference = Reference("1", "2", 3, 1)
        self.assertEqual(reference.__str__(), "1 (2.3.1)")


if __name__ == '__main__':
    unittest.main()

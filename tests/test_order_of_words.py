import unittest

class TestOrder(unittest.TestCase):
    def test_order(self):
        self.assertEqual(["ἀγρία","ἀγρίας"], sorted(["ἀγρία", "ἀγρίας"]))
        self.assertEqual(["ἀγρία","ἀγρίας"], sorted(["ἀγρίας", "ἀγρία"]))

if __name__ == '__main__':
    unittest.main()

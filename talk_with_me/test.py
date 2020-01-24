import unittest
from data4ml import Data4ML


class TestData4ML(unittest.TestCase):
    def setUp(self):
        self.data4ml = Data4ML()

    def test_clear_message(self):
        samples = {
            "Привет, как дела?": "Привет, как дела?",
            "   Привет, как дела?   ": "Привет, как дела?",
        }

        for key, value in samples.items():
            self.assertEqual(self.data4ml.clear_message([key]), [value])


if __name__ == "__main__":
    unittest.main()

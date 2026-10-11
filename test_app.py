import unittest

def count_vowels(text: str) -> int:
    vowels = "аеєиіїоуюяАЕЄИІЇОУЮЯaeiouAEIOU"
    return sum(1 for char in text if char in vowels)

class TestVowels(unittest.TestCase):
    def test_vowels_basic(self):
        self.assertEqual(count_vowels("hello"), 2)

    def test_vowels_empty(self):
        self.assertEqual(count_vowels(""), 0)

    def test_vowels_ukrainian(self):
        self.assertEqual(count_vowels("Привіт"), 2)

    def test_vowels_numbers(self):
        self.assertEqual(count_vowels("12345"), 0)

if __name__ == "__main__":
    unittest.main()
import unittest
import os
from unittest.mock import patch, mock_open
from generate_cards_md import (
    chn_char_into_eng_char,
    read_words_from_file,
    gen_card_prompt,
    split_a_card,
    write_to_card_file,
    google_translate,
)


# python3 -m unittest test_generate_cards_md.py
class TestChnCharIntoEngChar(unittest.TestCase):
    def test_chn_char_into_eng_char(self):
        # Test case 1: Chinese quotation marks
        self.assertEqual(chn_char_into_eng_char("”Hello”"), '"Hello"')
        # Test case 1: Chinese quotation marks
        self.assertEqual(chn_char_into_eng_char("“Hello”"), '"Hello"')

        # Test case 2: Mixed Chinese and English quotation marks
        self.assertEqual(
            chn_char_into_eng_char('"Hello" and "World"'), '"Hello" and "World"'
        )

        # Test case 3: No Chinese quotation marks
        self.assertEqual(chn_char_into_eng_char("Hello World"), "Hello World")

        # Test case 4: Empty string
        self.assertEqual(chn_char_into_eng_char(""), "")


#  py3 -m unittest generate_cards_md.TestReadWordsFromFile
class TestReadWordsFromFile(unittest.TestCase):
    def test_read_words_from_file_success(self):
        with patch("builtins.open", mock_open(read_data="word1\nword2\nword3")):
            words = read_words_from_file("test.txt")
            self.assertEqual(words, ["word1", "word2", "word3"])

    def test_read_words_from_empty_file(self):
        with patch("builtins.open", mock_open(read_data="")):
            with self.assertRaises(SystemExit):
                read_words_from_file("empty.txt")

    def test_file_not_found(self):
        with patch("builtins.open", side_effect=FileNotFoundError):
            with self.assertRaises(SystemExit):
                read_words_from_file("nonexistent.txt")


class TestGeneratePrompt(unittest.TestCase):
    def test_generate_prompt(self):
        input_text = "test"
        prompt = gen_card_prompt(input_text)
        self.assertIn(input_text, prompt)
        self.assertIn("I am a native Chinese speaker", prompt)


class TestSplitACard(unittest.TestCase):
    def test_split_a_card(self):
        test_card = "## Front content\nBack content line 1\nBack content line 2"
        front, back = split_a_card(test_card)
        self.assertEqual(front, "## Front content\n")
        self.assertEqual(back, "Back content line 1\nBack content line 2")


class TestWriteToFile(unittest.TestCase):
    @patch("os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    def test_write_to_file(self, mock_file, mock_makedirs):
        content = "Test content"
        write_to_card_file(content)
        mock_makedirs.assert_called_once_with("data", exist_ok=True)
        mock_file.assert_called_once_with("data/cards.md", "a")
        mock_file().write.assert_called_once_with(content)


# run 100 times card gen eng, then chn.
# 9.504998 to 9.39 -> 0.11
# 1 card: 0.11/100 = 0.0011
# 5k cards: 0.0011 * 5000 = 5.5



class TestGoogleTranslate(unittest.TestCase):
    def test_google_translate_success(self):
        result = google_translate("Hello, world!", "zh-CN")
        self.assertEqual(result, "你好，世界！")

    def test_google_translate_request_exception(self):
        # Test with a very long text that might cause an error
        long_text = "Hello, world! " * 1000
        result = google_translate(long_text, "zh-CN")
        self.assertEqual(result, long_text)  # Should return original text on error

    def test_google_translate_empty_response(self):
        # Test with an empty string
        result = google_translate("", "zh-CN")
        self.assertEqual(result, "")  # Should return empty string for empty input

    def test_google_translate_default_language(self):
        result = google_translate("Hello, world!")  # No language specified
        self.assertIsNotNone(result)  # We can't predict the exact translation, but it should not be None
        self.assertNotEqual(result, "Hello, world!")  # It should be translated

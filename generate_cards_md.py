from openai import OpenAI
import httpx
import os
import sys


class LLM_Client:
    def __init__(self):
        self.client = self._create_openai_client()

    def _get_api_token(self):
        api_token = os.environ.get("LLM_API_KEY")
        if api_token is None:
            print(
                "Error: shell env key not found: LLM_API_KEY is not set.",
                file=sys.stderr,
            )
            sys.exit(1)  # Exit the program with a non-zero status
        return api_token

    def _create_openai_client(self):
        api_token = self._get_api_token()
        return OpenAI(
            base_url="https://api.xty.app/v1",
            api_key=api_token,
            http_client=httpx.Client(
                base_url="https://api.xty.app/v1",
                follow_redirects=True,
            ),
        )

    def get_completion(self, prompt):
        try:
            completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                # model="gpt-4o",
                messages=[
                    {"role": "user", "content": prompt},
                ],
            )
            return completion.choices[0].message.content + "\n\n"
        except Exception as e:
            print(f"Error generating completion: {e}", file=sys.stderr)
            sys.exit(1)


def read_words_from_file(filename):
    try:
        with open(filename, "r") as file:
            words = [line.strip() for line in file]
        if not words:
            print(f"Error: File '{filename}' is empty.", file=sys.stderr)
            sys.exit(1)
        return words
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"Error reading file '{filename}': {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error reading file '{filename}': {e}", file=sys.stderr)
        sys.exit(1)


def generate_prompt(input_text):
    # The answer should be derived from the English corpus to solve the problem and translated into Chinese:
    return f"""
I am a native Chinese speaker and need to learn English a word: {input_text}
The requirements are as follows:
1. Please answer in plain text format, do not use Markdown.
2. The answer should only include the following content:
  01. Start with 2 #, followed by a space, and use appropriate and brief wording to make a sentence. The sentence should be short and accurately use the most common usage of the word to be learned, with the word wrapped in ** **, then start a new line.
  02. Briefly and comprehensively explain the root and affixes, and the origin of the word in English.
  03. Brief and accurate definition.  
"""


def write_to_file(content):
    os.makedirs("data", exist_ok=True)
    try:
        with open("data/cards.md", "a") as file:
            file.write(content)
    except IOError as e:
        print(f"Error writing to file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error writing to file: {e}", file=sys.stderr)
        sys.exit(1)


def generate_card(openai_client, input_text):
    prompt = generate_prompt(input_text)
    eng_res = openai_client.get_completion(prompt)
    return eng_res


def translate_to_chinese(openai_client, src_text):
    translate_prompt = (
        "translate the following text into Chinese , your answer  dont modify any symbols"
        + src_text
    )
    ret = openai_client.get_completion(translate_prompt)
    return chn_char_into_eng_char(ret)


def chn_char_into_eng_char(text):
    return text.replace(""", '"').replace(""", '"')


def split_a_card(src_text):
    lines = src_text.split("\n")
    front = []
    back = []
    for line in lines:
        if line.startswith("##"):
            front.append(line)
        else:
            back.append(line)
    return "\n".join(front) + "\n", "\n".join(back)


def main():
    input_text = "chronic"
    llm_client = LLM_Client()
    card_eng = generate_card(llm_client, input_text)
    print(card_eng)
    front, back_eng = split_a_card(card_eng)
    card_chn = front + translate_to_chinese(llm_client, back_eng)
    # print(card_chn)
    write_to_file(card_chn)


if __name__ == "__main__":
    main()

import unittest
import os
from unittest.mock import patch, mock_open


#  py3 -m unittest generate_cards_md.TestChnCharIntoEngChar
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

class TestReadWordsFromFile(unittest.TestCase):
    def test_read_words_from_file_success(self):
        with patch('builtins.open', mock_open(read_data="word1\nword2\nword3")):
            words = read_words_from_file("test.txt")
            self.assertEqual(words, ["word1", "word2", "word3"])

    def test_read_words_from_empty_file(self):
        with patch('builtins.open', mock_open(read_data="")):
            with self.assertRaises(SystemExit):
                read_words_from_file("empty.txt")

    def test_file_not_found(self):
        with patch('builtins.open', side_effect=FileNotFoundError):
            with self.assertRaises(SystemExit):
                read_words_from_file("nonexistent.txt")

class TestGeneratePrompt(unittest.TestCase):
    def test_generate_prompt(self):
        input_text = "test"
        prompt = generate_prompt(input_text)
        self.assertIn(input_text, prompt)
        self.assertIn("I am a native Chinese speaker", prompt)

class TestSplitACard(unittest.TestCase):
    def test_split_a_card(self):
        test_card = "## Front content\nBack content line 1\nBack content line 2"
        front, back = split_a_card(test_card)
        self.assertEqual(front, "## Front content\n")
        self.assertEqual(back, "Back content line 1\nBack content line 2")

class TestWriteToFile(unittest.TestCase):
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_write_to_file(self, mock_file, mock_makedirs):
        content = "Test content"
        write_to_file(content)
        mock_makedirs.assert_called_once_with("data", exist_ok=True)
        mock_file.assert_called_once_with("data/cards.md", "a")
        mock_file().write.assert_called_once_with(content)

class TestLLMClient(unittest.TestCase):
    @patch.dict(os.environ, {"LLM_API_KEY": "test_key"})
    def test_get_api_token(self):
        client = LLM_Client()
        self.assertEqual(client._get_api_token(), "test_key")

    @patch.dict(os.environ, clear=True)
    def test_get_api_token_missing(self):
        with self.assertRaises(SystemExit):
            LLM_Client()

    @patch('openai.OpenAI')
    def test_create_openai_client(self, mock_openai):
        with patch.dict(os.environ, {"LLM_API_KEY": "test_key"}):
            LLM_Client()
            mock_openai.assert_called_once()

if __name__ == '__main__':
    unittest.main()

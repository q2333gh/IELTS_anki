from openai import OpenAI
import httpx
import os
import sys
import threading

file_lock = threading.Lock()


class LLM_Client:
    # available models:
    # gpt-3.5-turbo, gpt-4o
    # model = "gpt-4o"  1000 times of 150q 60a for 10usd .
    model = "gpt-3.5-turbo"  # 25K times

    def __init__(self):
        self.client = self._create_llm_client()

    def _get_api_token(self):
        api_token = os.environ.get("LLM_API_KEY")
        if api_token is None:
            print(
                "Error: shell env key not found: LLM_API_KEY is not set.",
                file=sys.stderr,
            )
            sys.exit(1)  # Exit the program with a non-zero status
        return api_token

    def _create_llm_client(self):
        api_token = self._get_api_token()
        return OpenAI(
            base_url="https://api.xty.app/v1",
            api_key=api_token,
            http_client=httpx.Client(
                base_url="https://api.xty.app/v1",
                follow_redirects=True,
            ),
        )

    # default use gpt3.5turbo, if you want to use gpt4o, set model="gpt-4o"
    def ask(self, prompt, model=model):
        try:
            completion = self.client.chat.completions.create(
                model=model,
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


def gen_card_prompt(input_text):
    # The answer should be derived from the English corpus to solve the problem and translated into Chinese:
    return f"""
I need to learn English a word: {input_text}
Requirements are as follows:
1. Please answer in plain text format, do not use Markdown.
2. The answer should only include the following content:
  01. Start with 2 #, followed by a space, use appropriate and brief wording to make a sentence, the word must wrapped in ** **, newline
  02. give 2 most equivalent and common used english word alternative, newline
  03. Briefly and comprehensively explain the target word root words and affixes, newline
  04. Brief and accurate definition, newline
"""


def write_to_card_file(content):
    os.makedirs("data", exist_ok=True)
    try:
        with file_lock:  # Acquire the lock before writing
            with open("data/cards02.md", "a") as file:
                file.write(content)
    except IOError as e:
        print(f"Error writing to file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error writing to file: {e}", file=sys.stderr)
        sys.exit(1)


def generate_card(llm_client, input_text):
    prompt = gen_card_prompt(input_text)
    # eng_res = llm_client.ask(prompt, model="gpt-4o")
    eng_res = llm_client.ask(prompt)
    return eng_res


def translate_to_chinese(llm_client, src_text):
    translate_prompt = (
        "translate the following text into Chinese , your answer  dont modify any symbols"
        + src_text
    )
    ret = llm_client.ask(translate_prompt)
    return chn_char_into_eng_char(ret)


#### WARN: this function is can be changed by cursor. It dont recognize: "
def chn_char_into_eng_char(text):
    return text.replace("“", '"').replace("”", '"')


def split_a_card(src_text):
    lines = [line for line in src_text.split("\n") if line.strip()]
    front = lines[:2]
    back = lines[2:]
    return "\n".join(front) + "\n", "\n".join(back)


def read_words_from_file():
    try:
        with open("data/filtered_words.txt", "r") as file:
            words = [line.strip() for line in file]
        return words
    except FileNotFoundError:
        print("Error: 'data/filtered_words.txt' not found.", file=sys.stderr)
        exit(1)
    except IOError as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        exit(1)


def main():
    import concurrent.futures
    import multiprocessing

    words = read_words_from_file()  # about 4000 words.
    selected_words = words[2000:2003]
    words = selected_words
    llm_client = LLM_Client()

    def process_word(word):
        card_eng = generate_card(llm_client, word)
        front, back_eng = split_a_card(card_eng)
        card_chn = front + translate_to_chinese(llm_client, back_eng)
        write_to_card_file(card_chn + "\n")

    max_workers = multiprocessing.cpu_count()

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=max_workers
    ) as executor:
        executor.map(process_word, words)


import requests


def google_translate(text, target_language="zh-CN"):
    """
    Translate text using Google Translate API (free method).

    :param text: The text to translate
    :param target_language: The target language code (default is 'zh-CN' for Chinese)
    :return: Translated text
    """
    base_url = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",
        "sl": "auto",
        "tl": target_language,
        "dt": "t",
        "q": text,
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        result = response.json()
        translated_text = "".join(
            [sentence[0] for sentence in result[0] if sentence[0]]
        )
        return translated_text
    except requests.RequestException as e:
        print(f"Error occurred while translating: {e}")
        exit(1)
        return text  # Return original text if translation fails


if __name__ == "__main__":
    main()

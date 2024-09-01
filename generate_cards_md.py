from openai import OpenAI
import httpx
import os
import sys
import threading
import requests
import concurrent.futures
import multiprocessing
import uuid

file_lock = threading.Lock()


class Back:
    def __init__(self, alternative_words, src_explain, word_def):
        self.alternative_words = alternative_words
        self.src_explain = src_explain
        self.word_def = word_def


class LearnCard:
    def __init__(self, front, alternative_words, src_explain, word_def):
        self.front = front
        self.back = Back(alternative_words, src_explain, word_def)

    def __str__(self):
        return f"{self.front}\n{self.back.alternative_words}\n{self.back.src_explain}\n{self.back.word_def}\n"


class LLM_Client:
    # available models:
    # gpt-3.5-turbo, gpt-4o
    # model = "gpt-4o"  #1000 times of 150q 60a for 10usd .
    # model = "gpt-3.5-turbo"  # 25K times
    model = "gpt-3.5-turbo-0125"  # cheapest

    def __init__(self):
        self.client = self._create_llm_client()

    def _get_api_token(self):
        # api_token = os.environ.get("LLM_API_KEY") #/home/btwl/.config/fish/config.fish
        api_token = os.environ.get("LLM_API_KEY2") # 3.5 only key.
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
            conversation_id = str(
                uuid.uuid4()
            )  # Generate a unique identifier for each conversation
            completion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt, "conversation_id":    conversation_id},
                ],
            )
            return completion.choices[0].message.content
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

# key prompt:  `meaningful` !
def gen_card_prompt(input_text):
    return f"""
I am learning an English word: {input_text}
Requirements are as follows:
  The answer should only include the following content:
  make a sentence which is precise,comprehensive,conciseness,vivid,meaningful;only  the target word should wrapped in ** **, newline
  give 2 most equivalent and common used english word alternative, newline
  Briefly and comprehensively explain the target word root words and affixes, newline
  Brief and accurate definition, newline
"""


def write_to_card_file(content):
    if not content:
        print("No content to write.")
        return

    try:
        with file_lock:
            # with statement ensures that the lock is properly acquired and released
            with open("data/cards_might_good.md", "a") as file:
                file.write(content)
    except Exception as e:
        print(f"An error occurred by write_to_card_file(): {e}")


def gen_card_eng(llm_client, input_text):
    prompt = gen_card_prompt(input_text)
    # eng_res = llm_client.ask(prompt, model="gpt-4o")
    eng_res = llm_client.ask(prompt)
    return eng_res


def trans_to_chn(llm_client, src_text):
    translate_prompt = "translate the following text into Chinese:" + src_text
    ret = llm_client.ask(translate_prompt)
    return chn_char_into_eng_char(ret)


#### WARN: this function is can be changed by cursor. It dont recognize: "
def chn_char_into_eng_char(text):
    return text.replace("“", '"').replace("”", '"')


def parse_card_content(content):
    lines = [line.strip() for line in content.split("\n") if line.strip()]
    front = "## " + str(lines[0])
    alternative_words = str(lines[1])
    src_explain = str(lines[2])
    word_def = lines[3]
    return LearnCard(front, alternative_words, src_explain, word_def)


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


def process_word(word, llm_client):
    card_text_eng = gen_card_eng(llm_client, word)
    card = parse_card_content(card_text_eng)
    src_explain_chn = trans_to_chn(llm_client, card.back.src_explain)
    word_def_chn = trans_to_chn(llm_client, card.back.word_def)
    card.back.src_explain += f"\n{src_explain_chn}"
    card.back.word_def += f"\n{word_def_chn}"
    print(card)
    write_to_card_file(str(card) + "\n")
    # TODO: write_to_card_file(card + "\n")  never raise TypeError, why? Especailly here. it run it in ut. it will raise TypeError. Which make this bug a little subtle to detect.


def main():
    words = read_words_from_file("data/words4000.txt")
    # selected_words = words[3000:3010]
    # words = selected_words
    # # words = ["deficit"]
    llm_client = LLM_Client()

    max_workers = multiprocessing.cpu_count()
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(lambda word: process_word(word, llm_client), words)


if __name__ == "__main__":
    main()

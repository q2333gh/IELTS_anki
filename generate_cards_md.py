from openai import OpenAI
import httpx
import os
import sys


class LLM_Client:
    # available models:
    # gpt-3.5-turbo, gpt-4o
    model = "gpt-3.5-turbo" # 25K times
    # model = "gpt-4o"  1000 times of 150q 60a for 10usd .

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


def generate_card(llm_client, input_text):
    prompt = generate_prompt(input_text)
    eng_res = llm_client.ask(prompt, model="gpt-4o")
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

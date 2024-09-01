from openai import OpenAI
import httpx
import os
import sys

class OpenAIClient:
    def __init__(self):
        self.client = self._create_openai_client()

    def _get_api_token(self):
        api_token = os.environ.get("LLM_API_KEY")
        if api_token is None:
            print("Error: shell env key not found: LLM_API_KEY is not set.", file=sys.stderr)
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
  01. Start with 2 #, followed by a space, and use appropriate wording to make a sentence. The sentence should be short and accurately use the most common usage of the word to be learned, with the word wrapped in ** **, then start a new line.
  02. Briefly and comprehensively explain the root and affixes, and the origin of the word in English.
  03. Brief and accurate definition.  
"""

'''
prompt_cn=f"""
回答应该是从英文语料库解决问题,并翻译为中文回答:
我是中文母语者,需要学习英文单词:  {input_text}
要求如下:
1. 请用纯文本格式回答，不要使用Markdown。
2. 回答只包含如下内容:
  01.格式为 2个# 开头,接上一个空格,使用合适的措辞造句一句,要求造句简短且准确地使用这个词最常用的用法,将要学习的词 包裹在** ** 中,然后回车新的一行
  02. 简要且无遗漏地用中文解释词根词缀,来源  
  03. 释义
"""

prompt_eng=f"""
The answer should be derived from the English corpus to solve the problem and translated into Chinese:
I am a native Chinese speaker and need to learn English words: {input_text}
The requirements are as follows:
1. Please answer in plain text format, do not use Markdown.
2. The answer should only include the following content:
  01. Start with 2 #, followed by a space, and use appropriate wording to make a sentence. The sentence should be short and accurately use the most common usage of the word to be learned, with the word wrapped in ** **, then start a new line.
  02. Briefly and comprehensively explain the root and affixes, and the origin of the word in Chinese.
  03. Definition.
"""
'''

def write_to_file(content):
    os.makedirs('data', exist_ok=True)
    try:
        with open('data/cards.md', 'a') as file:
            file.write(content)
    except IOError as e:
        print(f"Error writing to file: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: File 'data/cards.md' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error writing to file: {e}", file=sys.stderr)
        sys.exit(1)

def generate_card(openai_client, input_text):
    prompt = generate_prompt(input_text)
    eng_res = openai_client.get_completion(prompt)
    return eng_res

def translate_to_chinese(openai_client, text):
    translate_prompt = (
        "translate the following text into Chinese: all symbols should using English characters"
        + text
    )
    return openai_client.get_completion(translate_prompt)

def main():
    input_text = "chronic"

    openai_client = OpenAIClient()

    card_eng = generate_card(openai_client, input_text)
    print(card_eng)

    card_chn = translate_to_chinese(openai_client, card_eng)
    print(card_chn)

    write_to_file(card_chn)

if __name__ == "__main__":
    main()

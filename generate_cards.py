from openai import OpenAI
import httpx
import os
import sys

def get_api_token():
    api_token = os.environ.get("LLM_API_KEY")
    if api_token is None:
        print("Error: shell env key not found: LLM_API_KEY is not set.", file=sys.stderr)
        sys.exit(1)  # Exit the program with a non-zero status
    return api_token

def create_openai_client(api_token):
    return OpenAI(
        base_url="https://api.xty.app/v1",
        api_key=api_token,
        http_client=httpx.Client(
            base_url="https://api.xty.app/v1",
            follow_redirects=True,
        ),
    )

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
    return f"""
我是中文母语者,需要学习英文单词:  {input_text}
要求如下:
0. 回答应该是从英文语料库查找,并翻译为中文回答:
1. 请用纯文本格式回答，不要使用Markdown。
2. 回答只包含如下内容:
01.格式为 2个# 开头,接上一个空格,使用合适的措辞造句一句,要求造句简短且准确地使用这个词最常用的用法,将要学习的词包裹在** ** 中,然后回车新的一行
02. 完整无遗漏地解释词根词缀,来源  
03. 释义
"""

def get_completion(client, prompt):
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error generating completion: {e}", file=sys.stderr)
        return None

def write_to_file(content):
    os.makedirs('data', exist_ok=True)
    try:
        with open('data/cards.md', 'a') as file:
            file.write(content)
    except IOError as e:
        print(f"Error writing to file: {e}", file=sys.stderr)

def main():
    api_token = get_api_token()
    client = create_openai_client(api_token)
    
    words = read_words_from_file("path_to_your_word_file.txt")  # Replace with actual file pat

    print(words)
    input_text = words[0]  # input_text = "chronic"

    prompt = generate_prompt(input_text)
    print(prompt)

    res = get_completion(client, prompt)
    if res:
        print(res)
        write_to_file(res)
    else:
        print("Failed to generate completion.", file=sys.stderr)

if __name__ == "__main__":
    main()
from openai import OpenAI
import httpx
import os
import sys

api_token = os.environ.get("LLM_API_KEY")
if api_token is None:
    print("Error: shell env key not found: LLM_API_KEY is not set.", file=sys.stderr)
    sys.exit(1)  # Exit the program with a non-zero status

client = OpenAI(
    base_url="https://api.xty.app/v1",
    api_key=api_token,
    http_client=httpx.Client(
        base_url="https://api.xty.app/v1",
        follow_redirects=True,
    ),
)

# Read all words into a list (vector)
with open("filtered_words.txt", "r") as file:
    words = [line.strip() for line in file]

print(words)
input_text = words[0]  # input_text = "chronic"

# if web llm testing prompt use to avoid md file render:
# 1. 将整个回答包裹在``` ``` 之中
prompt = f"""
我需要学习英文单词:  {input_text}
要求如下:
1. 请用纯文本格式回答，不要使用Markdown。
2. 回答只包含如下内容:
01.格式为 2个# 开头,接上一个空格,使用合适的措辞造句一句,要求造句简短且准确地使用这个词最常用的用法,将要学习的词包裹在** ** 中,然后回车新的一行
02. 完整无遗漏地解释词根词缀,来源  
03. 释义
"""
print(prompt)
completion = client.chat.completions.create(
    # model="gpt-4",
    # model="gpt-4-32k",
    # gpt-3.5-turbo
    model="gpt-4",
    messages=[
        {"role": "user", "content": prompt},
    ],
)
# print(completion.choices[0].message["content"])
print(completion.choices[0].message)
# TODO this completion finish too slow when using 3.5 turbo. also generate quality not good.  gpt4 is good and fast  
res = completion.choices[0].message.content  # Accessing content directly
print(res)

with open("cards.md", "a") as file: # append mode write
    # Write the text you want to append
    file.write(res)

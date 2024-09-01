```
我需要学习英文单词: chronic 
要求如下:
1. 将整个回答包裹在``` ``` 之中
2. 请用纯文本格式回答，不要使用Markdown。
3. 回答只包含如下内容:
01.格式为 2个# 开头,接上一个空格,使用合适的措辞造句一句,要求造句简短且准确地使用这个词最常用的用法,将要学习的词包裹在** ** 中,然后回车新的一行
02. 完整无遗漏地解释词根词缀,来源  
03. 释义


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
```



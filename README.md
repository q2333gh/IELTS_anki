Thanks to

1. words list src: https://github.com/lzrk/nglsh/blob/master/IELTS-4000.txt
https://github.com/fanhongtao/IELTS/blob/master/IELTS%20Word%20List.txt

2. convert .md file to anki cards import format: https://github.com/ashlinchak/mdanki?tab=readme-ov-file#cards

3. inspired by 新东方 雅思词汇词根+联想记忆法：乱序版

# get lib for python3.12_executable on ubuntu2204:

sudo python3.12 -m ensurepip --upgrade && sudo python3.12 -m pip install --upgrade pip setuptools && sudo python3.12 -m pip install openai httpx
sudo python3.12 get-pip.py this use curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
sudo python3.12 -m pip install --upgrade pip setuptools && sudo python3.12 -m pip install openai httpx

mdanki cards.md cards.apkg



# debug yourself: (i use fish shell)
python3 -m venv myenv && source myenv/bin/activate.fish && pip install -r requirements.txt

from flask import Flask
from collections import deque
import re
import MeCab
import random
import os

app = Flask(__name__)

#いくつもの文章を分かち書きし、要素をリストに格納する
def wakati(text):
    t = MeCab.Tagger("-Owakati")
    parsed_text = ""
    for one_line_text in one_sentence_generator(text):
        parsed_text += " "
        parsed_text += t.parse(one_line_text)
    wordlist = parsed_text.rstrip("\n").split(" ")
    return wordlist
#1つずつの文章に区切って渡す
def one_sentence_generator(long_text):
    sentences = re.findall(".*?。", long_text)
    for sentence in sentences:
        yield sentence

#マルコフ連鎖用のモデルを生成する
def make_model(text, order):
    model = {}
    wordlist = wakati(text)
    queue = deque([], order)
    queue.append("[BOS]")
    for markov_value in wordlist:
        if len(queue) < order:
            queue.append(markov_value)
            continue
        if queue[-1] == "。":
            markov_key = tuple(queue)
            if markov_key not in model:
                model[markov_key] = []
            model.setdefault(markov_key, []).append("[BOS]")
            queue.append("[BOS]")
        markov_key = tuple(queue)
        model.setdefault(markov_key, []).append(markov_value)
        queue.append(markov_value)
    return model

#モデルを用いて文章を生成する
def make_sentence(model, sentence_num, seed="[BOS]", max_words = 1000):    
    sentence_count = 0
    key_candidates = [key for key in model if key[0] == seed]
    if not key_candidates:
        print("Not find Keyword")
        return
    markov_key = random.choice(key_candidates)
    queue = deque(list(markov_key), len(list(model.keys())[0]))
    sentence = "".join(markov_key)
    for _ in range(max_words):
        markov_key = tuple(queue)           #1文にある程度単語数がないと、"。"には繋げられないようにするか...？
        next_word = random.choice(model[markov_key])
        sentence += next_word
        queue.append(next_word)
        if next_word == "。":
            sentence_count += 1
            if sentence_count == sentence_num:
                break
    result = sentence.replace(seed, "")
    return result

#適切なファイルパスを指定し、テキストデータを返す           current_dir\texts\(どのお話か)\(stepは何か).txt  を戻り値に
def get_text(current_dir, storytype_i, step):
  path = os.path.join(current_dir, "texts", storytype_i, step)
  with open(path, "r", encoding="utf-8") as file:
    return file.read()
  
#stepに応じて、"テキストデータの取得→文章生成→return" の一連の流れを行う
def get_result(current_dir, storytype_1, storytype_2, step, order, sentence_num):
  text_1 = get_text(current_dir, storytype_1, step)
  text_2 = get_text(current_dir, storytype_2, step)
  text_sum = text_1 + text_2
  model = make_model(text_sum, order)
  return make_sentence(model, sentence_num)


@app.route("/")
def main():
  current_dir = os.path.dirname(__file__)
  storytype_1 = "issunbousi"
  storytype_2 = "hanasaka"
  result = ""
  #beginningについての文章生成
  step = "beginning.txt"
  order = 1
  sentence_num = 1
  result += get_result(current_dir, storytype_1, storytype_2, step, order, sentence_num)
  result += "(@-@)"
  #middleについての文章生成
  step = "middle.txt"
  order = 2
  sentence_num = 20
  result += get_result(current_dir, storytype_1, storytype_2, step, order, sentence_num)
  result += "(@-@)"
  #endについての文章生成
  step = "end.txt"
  order = 1
  sentence_num = 1
  result += get_result(current_dir, storytype_1, storytype_2, step, order, sentence_num)
  result += "(@-@)おしまい。"
  return result
from flask import Flask, render_template, request
from collections import deque
import re
import MeCab
import random
import os

app = Flask(__name__)

#文章を分かち書きし、要素をwordlistに格納する
def wakati(text_total):
    t = MeCab.Tagger("-Owakati")
    parsed_text = ""
    for one_line_text in one_sentence_generator(text_total):
        parsed_text += " "
        parsed_text += t.parse(one_line_text)
    wordlist = parsed_text.rstrip("\n").split(" ")
    return wordlist
#1つずつの文章に区切って渡す
def one_sentence_generator(text_total):
    sentences = re.findall(".*?。", text_total)
    for sentence in sentences:
        yield sentence

#マルコフ連鎖用のモデルを生成する
def make_model(text_total, order):
    model = {}
    wordlist = wakati(text_total)
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
        markov_key = tuple(queue)
        next_word = random.choice(model[markov_key])
        sentence += next_word
        queue.append(next_word)
        if next_word == "。":
            sentence_count += 1
            if sentence_count == sentence_num:
                break
    result = sentence.replace(seed, "")
    return result

#適切なファイルパスを指定し、テキストデータを返す
def get_text(current_dir, text, step):
  path = os.path.join(current_dir, "texts", text, step)
  with open(path, "r", encoding="utf-8") as file:
    return file.read()


@app.route("/")
def view_form():
  return render_template("index.html")

@app.route("/view_result", methods = ["POST"])
def view_result():
  selected_options = request.form.getlist('options')
  result = ""
  current_dir = os.path.dirname(__file__)
  container = [
     ["beginning.txt", 1, 1],
     ["middle.txt", 2, 15],
     ["end.txt", 1, 1]
  ]
  for i in range(0, 3):
    step, order, sentence_num = container[i]
    text_total = ""
    for text in selected_options:
      text_total += get_text(current_dir, text, step)
    model = make_model(text_total, order)
    result += make_sentence(model, sentence_num)
  result += "おしまい。"
  return render_template("result.html", result = result)
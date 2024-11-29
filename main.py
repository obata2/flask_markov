from flask import Flask
from collections import deque
import re
import MeCab

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

@app.route("/")
def main():
  text = "昔々、小さな村に子どもを授かることを願う老夫婦が住んでいました。ある日、神さまに祈りを捧げると、「たとえ小さな子どもでもよいから授けてほしい」と願いが通じ、一寸（約3センチ）ほどの小さな男の子が生まれました。その子は「一寸法師」と名付けられました。一寸法師は小さな体ながらも心が強く、成長するにつれて立派な若者となりました。そして、「都に出て立派な侍になる」と夢を語り、旅立つ決意をしました。老夫婦は愛情を込めて、針の剣とお椀の船、箸のオールを一寸法師に持たせ、送り出しました。お椀の船に乗り、川を下って都に着いた一寸法師は、美しい姫が住む立派な屋敷を訪ね、そこで仕えることになりました。ある日、姫を狙う鬼が屋敷を襲います。一寸法師は姫を守るため、針の剣を持って鬼に立ち向かいました。小さな体でも勇気と機転を駆使して戦い、ついに鬼を追い払うことに成功します。逃げた鬼が落としていった不思議な打ち出の小槌を手に入れた一寸法師。姫と共に屋敷に戻り、小槌を振ると、「大きくなりたい」という願いが叶い、一寸法師はたちまち立派な大人の姿になりました。その後、姫と結ばれ、幸せに暮らしました。おしまい。"
  order = 2
  result = make_model(text, order)
  return text
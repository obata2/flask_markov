from flask import Flask
from collections import deque
import re
import MeCab
import random

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
        markov_key = tuple(queue)
        next_word = random.choice(model[markov_key])
        sentence += next_word
        queue.append(next_word)
        if next_word == "。":
            sentence_count += 1
            if sentence_count == sentence_num:
                break
    return sentence

@app.route("/")
def main():
  text_1 = "昔々、小さな村に子どもを授かることを願う老夫婦が住んでいました。ある日、神さまに祈りを捧げると、たとえ小さな子どもでもよいから授けてほしいと願いが通じ、一寸ほどの小さな男の子が生まれました。その子は一寸法師と名付けられました。一寸法師は小さな体ながらも心が強く、成長するにつれて立派な若者となりました。そして、都に出て立派な侍になる、と夢を語り、旅立つ決意をしました。老夫婦は愛情を込めて、針の剣とお椀の船、箸のオールを一寸法師に持たせ、送り出しました。お椀の船に乗り、川を下って都に着いた一寸法師は、美しい姫が住む立派な屋敷を訪ね、そこで仕えることになりました。ある日、姫を狙う鬼が屋敷を襲います。一寸法師は姫を守るため、針の剣を持って鬼に立ち向かいました。小さな体でも勇気と機転を駆使して戦い、ついに鬼を追い払うことに成功します。逃げた鬼が落としていった不思議な打ち出の小槌を手に入れた一寸法師。姫と共に屋敷に戻り、小槌を振ると、大きくなりたいという願いが叶い、一寸法師はたちまち立派な大人の姿になりました。その後、姫と結ばれ、幸せに暮らしました。おしまい。"
  text_2 = "昔々、あるところに心優しいおじいさんとおばあさんが住んでいました。二人は子どもがいなかったので、一匹のかわいい犬をとても大切に育てていました。犬の名前はポチといいます。ある日、ポチが庭で吠えながらおじいさんを呼びました。ポチが掘った穴を見てみると、中からたくさんの黄金が出てきました。おじいさんとおばあさんは喜び、ポチに感謝しました。その様子を見ていた隣の欲張りなおじいさんとおばあさんは、ポチを貸してほしいと頼みました。優しいおじいさんは快くポチを貸しましたが、隣の家でポチが掘った穴からは何も出ませんでした。腹を立てた隣の夫婦はポチを叩き、ひどい目にあわせました。悲しんだおじいさん夫婦はポチを連れ帰り、大切に世話をしましたが、やがてポチは亡くなってしまいました。おじいさんはポチを埋め、そばに小さな木を植えました。その木はぐんぐん育ち、大きな木になりました。ある日、おじいさんがその木を切り倒し臼を作ると、その臼でお餅をつくたびに黄金が出てきました。それをまた隣のおじいさんが見つけ、自分も使わせてほしいと頼みました。しかし、隣の家で臼を使うと黄金は出ず、隣の夫婦は腹を立てて臼を壊してしまいました。壊された臼の灰をおじいさんは持ち帰り、大切に保管していました。あるとき風に乗った灰が枯れ木に降りかかると、不思議なことに木が花を咲かせました。この出来事を知った殿様はおじいさんを褒め、花咲か爺さんと呼びました。その後、隣の夫婦も同じように灰を使いましたが、失敗して殿様に怒られてしまいました。優しいおじいさんとおばあさんはその後も仲良く暮らしました。おしまい。"
  order = 2
  text = text_1 + text_2
  model = make_model(text, order)
  sentence_num = 20
  result = make_sentence(model, sentence_num)
  return result
  
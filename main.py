from flask import Flask
import MeCab

app = Flask(__name__)

@app.route("/")
def main():
  mecab = MeCab.Tagger()
  text = "私は日本語を勉強しています。"
  nodes = mecab.parseToNode(text)
  tokens = []
  while nodes:
    if nodes.surface != "":
      tokens.append(nodes.surface)
      nodes = nodes.next
  return tokens
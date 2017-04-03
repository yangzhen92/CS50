from flask import Flask, redirect, render_template, request, url_for
import helpers
from tweets import p, n, ne, positives, negatives
from analyzer import Analyzer
from termcolor import colored

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search")
def search():
    pa = 0
    na = 0
    nea = 0

    # validate screen_name
    screen_name = request.args.get("screen_name", "").lstrip("@")
    if not screen_name:
        return redirect(url_for("index"))

    # get screen_name's tweets
    tweetss = helpers.get_user_timeline(screen_name)
    if not tweetss:
        return redirect(url_for("index"))

    # TODO
    b = Analyzer(positives, negatives)
    for text in tweetss:   #函数返回推特list，每条推以str形式存储
        b.analyze(text)        #把推特传给分析器
        if b.score > 0:
            pa += 1
            print(b.score,colored(text, "green"))
        elif b.score < 0:
            na += 1
            print(b.score,colored(text, "red"))
        else:
            nea += 1
            print(b.score,colored(text, "yellow"))
    positive, negative, neutral = pa, na, nea

    # generate chart
    chart = helpers.chart(positive, negative, neutral)

    # render results
    return render_template("search.html", chart=chart, screen_name=screen_name)

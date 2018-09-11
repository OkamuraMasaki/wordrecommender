# -*- coding: utf-8 -*-
import matplotlib as mpl
mpl.use("Agg")

import sys

from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns
import redis

#r = redis.StrictRedis(host='localhost', port=6379, db=0)
from datetime import datetime, date, timedelta
import numpy as np
import pandas as pd

from flask import Flask, render_template, request
import os

crawl_address = os.getenv("CRAWL_ADDRESS")
r = redis.StrictRedis(host=crawl_address, port=6379, db=0)
app = Flask(__name__)
@app.route('/')
def index():
    today = datetime.today().strftime("%Y-%m-%d")
    return render_template('index.html',today=today)


@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    if request.method == 'GET':
        res = request.args.get('get_value')
        return res
    elif request.method == 'POST':
        num = int(request.form['num_char'])
        count = int(request.form['word_count'])
        date = request.form['date']
        #num=2
        #count=20
        mpl.rcParams['axes.xmargin'] = 0
        mpl.rcParams['axes.ymargin'] = 0
        sites = request.form["sites"]
        rens = r.zrevrange(sites+"/"+date,0,-1,withscores=True)
        arnoldoy = [int(ren[1]) for ren in rens if len(ren[0].decode('utf-8'))>num and ren[1]>count]
        arnoldox = [ren[0].decode('utf-8') for ren in rens if len(ren[0].decode('utf-8'))>num and ren[1]>count]
        #arnoldo = [(ren[0].decode('utf-8'),ren[1]) for ren in rens if len(ren[0].decode('utf-8'))>1 and ren[1]>10]
        df = pd.DataFrame({"word_count":arnoldoy,"word":arnoldox,"date":"2018-08-29"})

        word=df["word"]
        y_pos = np.arange(len(word))

        fig, ax = plt.subplots(figsize=(12,len(word)/4))
        ax.barh(y_pos,df["word_count"],height=0.5)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(word)
        #ax.set_ylabel(word)
        img= BytesIO()
        ax.invert_yaxis()  # labels read top-to-bottom
        plt.savefig(img,format="png")
        plt.savefig('./static/figure.png')
        return render_template("confirm.html")



if __name__ == '__main__':
    app.debug = True
    app.run(debug=True,host='0.0.0.0')

# -*- coding: utf-8 -*-
import matplotlib as mpl
mpl.use("Agg")

import sys

from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns
import redis
import glob
#r = redis.StrictRedis(host='localhost', port=6379, db=0)
from datetime import datetime, date, timedelta
import numpy as np
import pandas as pd

from flask import Flask, session,render_template,url_for, redirect,request,flash
import os
env = os.getenv("RECOMMENDER_ENV","development")
crawl_address = os.getenv("CRAWL_ADDRESS")
r = redis.StrictRedis(host=crawl_address, port=6379, db=0)
app = Flask(__name__)
app.secret_key = 'hogeshu'
app.config['SESSION_TYPE'] = 'filesystem'
@app.route('/')
def index():
    today = datetime.today().strftime("%Y-%m-%d")
    
    return render_template('index.html',today=today,num=2,count=20,sites="all_urls")


@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    if request.method == 'GET':
        res = request.args.get('get_value')
        return res
    elif request.method == 'POST':
        num = int(request.form['num_char'])
        count = int(request.form['word_count'])
        date = request.form['date']
        sites = request.form["sites"]
        imgname = str(sites)+str(num)+str(count)+str(date)
        if './static/'+imgname+'.png' in glob.glob('./static/*'):
          return render_template("confirm.html",img_name=imgname)
        mpl.rcParams['axes.xmargin'] = 0
        mpl.rcParams['axes.ymargin'] = 0
        mpl.rcParams.update({'figure.autolayout': True})
        rens = r.zrevrange(sites+"/"+date,0,-1,withscores=True)
        arnoldoy = [int(ren[1]) for ren in rens if len(ren[0].decode('utf-8'))>num and ren[1]>count]
        arnoldox = [ren[0].decode('utf-8') for ren in rens if len(ren[0].decode('utf-8'))>num and ren[1]>count]
        if arnoldox == []:
           flash("その範囲では単語を見つけられませんでした","error")
           return render_template('index.html',today=date,num=num,count=count,sites=sites)
           #return redirect(url_for('index'))
        df = pd.DataFrame({"word_count":arnoldoy,"word":arnoldox,"date":"2018-08-29"})

        word=df["word"]
        y_pos = np.arange(len(word))

        fig, ax = plt.subplots(figsize=(8,len(word)/3))
        ax.barh(y_pos,df["word_count"],height=0.5)
        for i, v in enumerate(df["word_count"]):
          ax.text(v + 3, i + .25, str(v), color='blue', fontweight='bold')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(word)
        #ax.set_ylabel(word)
        ax.set_title("文字数"+str(num)+"以上、頻出数"+str(count)+"以上の"+str(date)+"のグラフ")
        img= BytesIO()
        ax.invert_yaxis()  # labels read top-to-bottom
        plt.savefig(img,format="png")
        plt.savefig('./static/'+imgname+'.png')
        return render_template("confirm.html",img_name=imgname)



if __name__ == '__main__':
    if env != "production":
      app.run(debug=True,host='0.0.0.0',port=5000)
    else:
      app.run(debug=False,host='0.0.0.0',port=5000)

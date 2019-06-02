from flask import Flask, render_template, request
import pymysql
from source import *

app = Flask(__name__)

@app.route('/')
def welcome():
    return render_template('index.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method=='POST':
        name = request.form['T1']
        address = request.form['T2']
        usertype = request.form['T3']
        email = request.form['T4']
        password = request.form['T5']

        # dependency injection
        conn = pymysql.connect(host=gethost(), port=getdbport(), user=getdbuser(), passwd=getdbpass(), db=getdb(),
                               autocommit=True)

        cur = conn.cursor()
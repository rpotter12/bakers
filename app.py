from flask import Flask, render_template, request, url_for, redirect,session
import pymysql
from source import *

app = Flask(__name__)

@app.route('/')
def welcome():
    return render_template('index.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/loginpage')
def loginpage():
    return render_template('login.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        email = request.form['T1']
        password = request.form['T2']

        # dependency injection
        conn = pymysql.connect(host=gethost(), port=getdbport(), user=getdbuser(), passwd=getdbpass(), db=getdb(),
                               autocommit=True)

        cur = conn.cursor()
        sql="select * from home where email='"+email+"' AND password='"+password+"'"
        cur.execute(sql)
        n=cur.rowcount
        data = cur.fetchone()
        usertype = data[2]

        if usertype == 'shop':
            return redirect(url_for('shop'))
        else:
            return redirect(url_for('buyer'))
    else:
        return render_template('login.html')

@app.route('/signuppage')
def signuppage():
    return render_template('signup.html')

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
        s1 = "insert into home values('" + name + "','" + address + "','" + usertype + "','" + email + "','" + password + "')"

        cur.execute(s1)
        n = cur.rowcount

        msg = "error"
        if n == 1:
            msg = "only data saved"
        return render_template('index.html', data=msg)
    else:
        return render_template('signup.html')

if __name__ == "__main__":
    app.run(debug=True)
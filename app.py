from flask import Flask, render_template, request, url_for, redirect,session
import pymysql
from source import *
from werkzeug.utils import secure_filename
import os
import time

app = Flask(__name__)
app.secret_key = "super secret key"

app.config['UPLOAD_FOLDER']='./static/photos'

# to show main welcome page
@app.route('/')
def welcome():
    return render_template('index.html')

# to show main welcome page
@app.route('/index')
def index():
    return render_template('index.html')

# clear session data, and logout the user
@app.route('/logout')
def logout():
    if 'usertype' in session:
        session.pop('usertype', None)
        session.pop('email', None)
        session.pop('name', None)
        session.pop('address', None)
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

# to show signup page
@app.route('/signuppage')
def signuppage():
    return render_template('signup.html')

# to insert signup page information
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

# to show login page
@app.route('/loginpage')
def loginpage():
    return render_template('login.html')

# to check the email and password for login
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        email = request.form['T1']
        password = request.form['T2']

        # dependency injection
        conn = pymysql.connect(host=gethost(), port=getdbport(), user=getdbuser(), passwd=getdbpass(), db=getdb(), autocommit=True)

        cur = conn.cursor()
        sql="select * from home where email='"+email+"' AND password='"+password+"'"
        cur.execute(sql)
        n=cur.rowcount
        if n > 0:
            data = cur.fetchone()
            usertype = data[2]
            name = data[0]
            address = data[1]

            session["email"] = email
            session["usertype"] = usertype
            session["name"] = name
            session["address"] = address

            if usertype == 'shop':
                return redirect(url_for('shop'))
            else:
                return redirect(url_for('buyer'))
        else:
            return redirect(url_for('loginpage'))
    else:
        return render_template('login.html')

# to show shopkeepers page
@app.route('/shop')
def shop():
    if "usertype" in session:
        usertype = session['usertype']
        name = session['name']
        if usertype == 'shop':
            return render_template('shop.html', sname = name)
        else:
            return redirect(url_for('loginpage'))
    else:
        return redirect(url_for('loginpage'))

# to show add item page
@app.route('/additempage')
def additempage():
    if "usertype" in session:
        usertype = session['usertype']
        name = session['name']
        if usertype == 'shop':
            return render_template('additem.html', sname = name)
        else:
            return redirect(url_for('loginpage'))
    else:
        return redirect(url_for('loginpage'))

# to insert item in database table
@app.route('/additem', methods=['GET','POST'])
def additem():
    if 'usertype' in session:
        usertype = session['usertype']
        if usertype == 'shop':
            if request.method == 'POST':
                file = request.files['F1']
                itemname = request.form['T1']
                description = request.form['T2']
                price = request.form['T3']
                piece = request.form['T4']
                email = session['email']
                name = session['name']

                if file:
                    path = os.path.basename(file.filename)
                    file_ext = os.path.splitext(path)[1][1:]
                    filename = str(int(time.time())) + '.' + file_ext
                    filename = secure_filename(filename)

                    # dependency injection
                    conn = pymysql.connect(host=gethost(), port=getdbport(), user=getdbuser(), passwd=getdbpass(),
                                           db=getdb(),
                                           autocommit=True)
                    cur = conn.cursor()
                    s1 = "insert into item values('" + itemname + "','" + description + "','" + price + "','" + piece + "','" + email + "','"+ filename +"')"

                    try:
                        cur.execute(s1)
                        n = cur.rowcount
                        if n == 1:
                            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                            return render_template('additem.html', sname = name)
                        else:
                            return render_template('additem.html', sname = name)
                    except:
                        return render_template('additem.html', sname = name)
            else:
                return redirect(url_for('additempage'))
        else:
            return redirect(url_for('loginpage'))
    else:
        return redirect(url_for('loginpage'))

# to show shopkeepers items
@app.route('/shopshow')
def shopshow():
    if "usertype" in session:
        usertype = session['usertype']
        email = session['email']
        if usertype == 'shop':
            conn = pymysql.connect(host=gethost(), port=getdbport(), user=getdbuser(), passwd=getdbpass(), db=getdb(),
                                   autocommit=True)
            cur = conn.cursor()
            sql = "select * from item where email='"+ email +"'"
            cur.execute(sql)
            n = cur.rowcount
            name = session['name']
            if n > 0:
                out = cur.fetchall()
                return render_template('shopshow.html', data=out, sname = name)
            else:
                return render_template('shopshow.html', msg="no data found")
        else:
            return redirect(url_for('loginpage'))
    else:
        return redirect(url_for('loginpage'))

# to show item edit page
@app.route('/shopitemeditpage')
def shopitemeditpage():
    if "usertype" in session:
        usertype = session['usertype']
        name = session['name']
        if usertype == 'shop':
            if request.method == 'POST':
                email = session['email']
                conn = pymysql.connect(host=gethost(),
                                       port=getdbport(),
                                       user=getdbuser(),
                                       passwd=getdbpass(),
                                       db=getdb(),
                                       autocommit=True)

                cur = conn.cursor()
                sql = "select * from item where email='" + email + "'"
                cur.execute(sql)
                n = cur.rowcount
                if n > 0:
                    data = cur.fetchone()
                    return render_template('shopedit.html', data=data, sname=name)
                else:
                    return render_template('shopedit.html', msg="No data found")
        else:
            return redirect(url_for('loginpage'))
    else:
        return redirect(url_for('loginpage'))

# to update item information
@app.route('/shopitemedit', methods=['GET','POST'])
def shopitemedit():
    if 'usertype' in session:
        usertype = session['usertype']
        if usertype == 'shop':
            if request.method == 'POST':
                file = request.files['F1']
                itemname = request.form['T1']
                description = request.form['T2']
                price = request.form['T3']
                piece = request.form['T4']
                email = session['email']
                name = session['name']

                if file:
                    path = os.path.basename(file.filename)
                    file_ext = os.path.splitext(path)[1][1:]
                    filename = str(int(time.time())) + '.' + file_ext
                    filename = secure_filename(filename)

                    # dependency injection
                    conn = pymysql.connect(host=gethost(), port=getdbport(), user=getdbuser(), passwd=getdbpass(),
                                           db=getdb(),
                                           autocommit=True)
                    cur = conn.cursor()
                    s1 = "update item set itemname='" + itemname + "',description='" + description + "',price='" + price + "',piece='"+ piece +"', filename='"+ filename +"' where email='"+ email +"'"

                    try:
                        cur.execute(s1)
                        n = cur.rowcount
                        if n == 1:
                            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                            return redirect(url_for('shopshow'))
                        else:
                            return redirect(url_for('shopitemedit'))
                    except:
                        return redirect(url_for('loginpage'))
            else:
                return redirect(url_for('shopitemedit'))
        else:
            return redirect(url_for('loginpage'))
    else:
        return redirect(url_for('loginpage'))

# to show items which have come for order by the user
@app.route('/ordershow')
def ordershow():
    if "usertype" in session:
        usertype = session['usertype']
        email = session['email']
        if usertype == 'shop':
            conn = pymysql.connect(host=gethost(), port=getdbport(), user=getdbuser(), passwd=getdbpass(), db=getdb(),
                                   autocommit=True)
            cur = conn.cursor()
            sql = "select * from order where email='"+ email +"'"
            cur.execute(sql)
            n = cur.rowcount
            name = session['name']
            if n > 0:
                out = cur.fetchall()
                return render_template('order.html', data=out, sname = name)
            else:
                return render_template('order.html', msg="no data found")
        else:
            return redirect(url_for('loginpage'))
    else:
        return redirect(url_for('loginpage'))

# to show account update page
@app.route('/accountupdatepage')
def accountupdatepage():
    if "usertype" in session:
        usertype = session['usertype']
        name = session['name']
        email = session['email']
        if usertype == 'shop':
            conn = pymysql.connect(host=gethost(), port=getdbport(), user=getdbuser(), passwd=getdbpass(), db=getdb(),
                                   autocommit=True)
            cur = conn.cursor()
            sql = "select * from home where email='" + email + "'"
            cur.execute(sql)
            n = cur.rowcount
            name = session['name']
            if n > 0:
                out = cur.fetchone()
                return render_template('shopaccount.html', data=out, sname=name)
            else:
                return render_template('shop.html', msg="no data found")
        else:
            return redirect(url_for('loginpage'))
    else:
        return redirect(url_for('loginpage'))

# to update shopkeeper account information
@app.route('/accountupdate', methods=['GET','POST'])
def accountupdate():
    if request.method == 'POST':
        name = request.form['T1']
        address = request.form['T2']
        password = request.form['T3']
        email = session['email']

        # dependency injection
        conn = pymysql.connect(host=gethost(), port=getdbport(), user=getdbuser(), passwd=getdbpass(), db=getdb(),
                               autocommit=True)

        cur = conn.cursor()
        s1 = "update home set name='" + name + "',address='" + address + "',password='" + password + "'"

        cur.execute(s1)
        n = cur.rowcount

        msg = "no data saved"
        if n == 1:
            msg = "data saved"
        return render_template('shop.html', sname = name)
    else:
        return render_template('shopaccount.html')

# to show buyer's home page
@app.route('/buyer')
def buyer():
    if "usertype" in session:
        usertype = session['usertype']
        name = session['name']
        if usertype == 'buyer':
            return render_template('buyer.html', bname = name)
        else:
            return redirect(url_for('loginpage'))
    else:
        return redirect(url_for('loginpage'))

# to show all items page
@app.route('/buyershow')
def buyershow():
    if "usertype" in session:
        usertype = session['usertype']
        email = session['email']
        if usertype == 'buyer':
            conn = pymysql.connect(host=gethost(), port=getdbport(), user=getdbuser(), passwd=getdbpass(), db=getdb(),
                                   autocommit=True)
            cur = conn.cursor()
            sql = "select * from item"
            cur.execute(sql)
            n = cur.rowcount
            name = session['name']
            if n > 0:
                out = cur.fetchall()
                return render_template('products.html', data=out, sname = name)
            else:
                return render_template('products.html', msg="no data found")
        else:
            return redirect(url_for('loginpage'))
    else:
        return redirect(url_for('loginpage'))

# to add item in cart
@app.route('/addproduct', methods=['GET','POST'])
def addproduct():
    if "usertype" in session:
        usertype = session['usertype']
        name = session['name']
        if usertype == 'buyer':
            if request.method == 'POST':
                itemname = request.form['T1']
                price = request.form['T2']
                email = session['email']
                address = session['address']

                # dependency injection
                conn = pymysql.connect(host=gethost(), port=getdbport(), user=getdbuser(), passwd=getdbpass(),
                                       db=getdb(),
                                       autocommit=True)

                cur = conn.cursor()
                s1 = "insert into cart values('" + itemname + "','" + price + "','" + address + "','" + email + "')"

                cur.execute(s1)
                n = cur.rowcount

                msg = "no data saved"
                if n == 1:
                    msg = "data saved"
                return render_template('cart.html', data=msg, sname=name)
            else:
                return render_template('products.html')
        else:
            return redirect(url_for('loginpage'))
    else:
        return redirect(url_for('loginpage'))

# to show cart item
@app.route('/showcart')
def showcart():
    if "usertype" in session:
        usertype = session['usertype']
        email = session['email']
        if usertype == 'buyer':
            conn = pymysql.connect(host=gethost(), port=getdbport(), user=getdbuser(), passwd=getdbpass(), db=getdb(),
                                   autocommit=True)
            cur = conn.cursor()
            sql = "select * from cart where email='"+ email +"'"
            cur.execute(sql)
            n = cur.rowcount
            name = session['name']
            if n > 0:
                out = cur.fetchall()
                return render_template('cart.html', data=out, sname = name)
            else:
                return render_template('cart.html', msg="no data found")
        else:
            return redirect(url_for('loginpage'))
    else:
        return redirect(url_for('loginpage'))

# to show buyer account update page
@app.route('/buyeraccountupdatepage')
def buyeraccountupdatepage():
    if "usertype" in session:
        usertype = session['usertype']
        name = session['name']
        email = session['email']
        if usertype == 'buyer':
            conn = pymysql.connect(host=gethost(), port=getdbport(), user=getdbuser(), passwd=getdbpass(), db=getdb(),
                                   autocommit=True)
            cur = conn.cursor()
            sql = "select * from home where email='" + email + "'"
            cur.execute(sql)
            n = cur.rowcount
            name = session['name']
            if n > 0:
                out = cur.fetchall()
                return render_template('buyeraccount.html', data=out, sname=name)
            else:
                return render_template('buyer.html', msg="no data found")
        else:
            return redirect(url_for('loginpage'))
    else:
        return redirect(url_for('loginpage'))

# to update buyer account information
@app.route('/buyeraccountupdate', methods=['GET','POST'])
def buyeraccountupdate():
    if request.method == 'POST':
        name = request.form['T1']
        address = request.form['T2']
        password = request.form['T3']
        email = session['email']

        # dependency injection
        conn = pymysql.connect(host=gethost(), port=getdbport(), user=getdbuser(), passwd=getdbpass(), db=getdb(),
                               autocommit=True)

        cur = conn.cursor()
        s1 = "update home set name='" + name + "',address='" + address + "',password='" + password + "' where email='"+ email +"'"

        cur.execute(s1)
        n = cur.rowcount

        msg = "no data saved"
        if n == 1:
            msg = "data saved"
        return render_template('buyer.html', bname = name)
    else:
        return render_template('shopaccount.html')

if __name__ == "__main__":
    app.run(debug=True)
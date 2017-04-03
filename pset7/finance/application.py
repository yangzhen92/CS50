from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import gettempdir

from helpers import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# custom filter
app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = gettempdir()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

@app.route("/")
@login_required
def index():
    return apology("TODO")

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock."""
    if request.method == "POST":
        dict = lookup(request.form.get("stockname"))
        if dict == None:
            return apology("stockname invaild")
        shares = int(request.form.get("shares"))
        #if shares != int:
        #    return apology("sharenum invaild")
        umoney = db.execute("SELECT cash FROM users WHERE id = :id",id = session["user_id"])
        tmoney = shares*dict["price"]
        if tmoney <= umoney[0]["cash"]:
            newcash = umoney[0]["cash"]-tmoney
            db.execute("UPDATE users SET cash = :cash WHERE id = 1",cash=newcash)
            db.execute("INSERT INTO history (user,symbol,price,share) VALUES(:user, :symbol, :price, :share)", user=session["user_id"], symbol=dict["symbol"], price=dict["price"], share=shares)
            info = db.execute("SELECT symbol,SUM(share) FROM history WHERE user=:user GROUP BY symbol",user = session["user_id"])
            print(info)
            assets = 0
            for i in info:
                assets += i["SUM(share)"]*lookup(i["symbol"])["price"]
            total = assets + newcash
            print(assets)
            return render_template("indexb.html",total=total,newcash=newcash,info=info,lookup=lookup)
        return apology("not enough money")
    return render_template("buy.html")

@app.route("/history")
@login_required
def history():
    """Show history of transactions."""
    info = db.execute("SELECT symbol,price,share,time FROM history WHERE user=:user",user=session["user_id"])
    return render_template("history.html",info = info,lookup=lookup)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("quote"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        dict = lookup(request.form.get("stockname"))
        if dict==None:
            return apology("stock not exist")
        return render_template("stockquote.html",name=dict["name"],price=dict["price"],symbol=dict["symbol"])
    return render_template("quote.html")
    

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("Missing username!")
        if request.form.get("password") != request.form.get("repassword"):
            return apology("password match failed")
        if not request.form.get("password"):
            return apology("please input password")
        pwhash = pwd_context.encrypt(request.form.get("password"))
        result = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        if result:
            return apology("user already exist")
        db.execute("INSERT INTO users (username,hash) VALUES(:username, :hash)", username=request.form.get("username"), hash=pwhash)
        #return render_template("register.html")
        session["user_id"] = result[0]["id"]
        return render_template("quote.html")
        
    else:
        return render_template("register.html")
        

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock."""
   
    if request.method == "POST":
        
        if not db.execute("SELECT symbol FROM history WHERE symbol=:symbol and user=:user",symbol = request.form.get("stockname"),user = session["user_id"]):
            return apology("stock not buy yet")
        if int(request.form.get("shares")) > db.execute("SELECT symbol,SUM(share) FROM history WHERE user=:user and symbol=:symbol",user=session["user_id"],symbol=request.form.get("stockname"))[0]["SUM(share)"]:
            return apology("not enough shares")
        dict = lookup(request.form.get("stockname"))
        db.execute("INSERT INTO history (user,symbol,price,share) VALUES(:user, :symbol, :price, :share)", user=session["user_id"], symbol=dict["symbol"], price=dict["price"], share=-int(request.form.get("shares")))
        newcash = dict["price"]*int(request.form.get("shares"))+db.execute("SELECT cash FROM users WHERE id=1")[0]["cash"]
        db.execute("UPDATE users SET cash = :cash WHERE id = 1",cash=newcash)
        info = db.execute("SELECT symbol,SUM(share) FROM history WHERE user=:user GROUP BY symbol",user = session["user_id"])
        total = 0
        assets = 0
        for i in info:
            assets += i["SUM(share)"]*lookup(i["symbol"])["price"]
        total = assets + newcash
        return render_template("indexs.html",total=total,newcash=newcash,info=info,lookup=lookup)
    return render_template("sell.html") 

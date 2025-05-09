# Bad Bunnies
# SoftDev
# P05:
# 2025-06-XX
# Time Spent: not enough hours

import random
import os
import sqlite3
import sys
from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
import db

DB_FILE = "db.py"
app = Flask(__name__)
app.secret_key = os.urandom(32)
anchor = False

if (not os.path.isfile("cipher.db")):
    db.setup()

@app.route("/", methods=['GET', 'POST'])
def home():
    loggedIn = 'username' in session
    if loggedIn:
        return render_template("home.html", logged_in=loggedIn, username=session['username'])
    return render_template("home.html", logged_in=loggedIn)

@app.route("/upload", methods=['GET', 'POST'])
def upload():
    loggedIn = 'username' in session
    return redirect("/train", logged_in=loggedIn)

@app.route('/train', methods=['GET', 'POST'])
def train():
    loggedIn = 'username' in session

    return render_template("train.html", logged_in = loggedIn)

@app.route("/results", methods=['GET', 'POST'])
def results():
    loggedIn = 'username' in session
    return render_template("results.html", logged_in=loggedIn)

@app.route("/history", methods=['GET', 'POST'])
def history():
    loggedIn = 'username' in session

    return render_template("history.html", logged_in=loggedIn)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if not request.form:
        flash("You must use the menu to register", 'error')
        return redirect("/")
    else:
        username = request.form['username']
        password = request.form['password']
        password2 = request.form.get('password2')
        if password != password2:
            flash("Passwords do not match", 'error')
            return redirect("/")
        elif db.checkUser(username) >= 0:
            flash("Username already exists", 'error')
            return redirect("/")
        else:
            session['username'] = username
            flash("Registered Successfully!", "success")
            db.addUser(username, password)
            return redirect("/")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if not request.form:
        flash("You must use the menu to log in", 'error')
        return redirect("/")
    else:
        username = request.form['username']
        password = request.form['password']
        if db.checkUser(username) >= 0 and db.getTableData("users", "username", username)[2] == password:
            session['username'] = username
            db.updateLoginTime(session['username'])
            flash("Logged in", 'success')
        else:
            flash("Incorrect username or password.", 'error')
        return redirect("/")

@app.route("/logout", methods=['GET', 'POST'])
def logout():
    if 'username' in session:
        flash("Logged out", 'success')
        session.pop('username', None)
    return redirect("/")

if __name__=="__main__":
    app.run(host='0.0.0.0')

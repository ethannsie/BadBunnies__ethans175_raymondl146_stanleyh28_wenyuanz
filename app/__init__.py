import random
import datetime
import os
import sqlite3
import sys
from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify, Response
import json
import pandas as pd
import db
import cv2

DB_FILE = "db.py"
app = Flask(__name__)
app.secret_key = os.urandom(32)
anchor = False

if (not os.path.isfile("keyboard.db")):
    db.setup()

camera = cv2.VideoCapture(2)  # 0 for default webcam

def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route("/", methods=['GET', 'POST'])
def home():
    loggedIn = 'username' in session
    if loggedIn:
        return render_template("home.html", logged_in=loggedIn, username=session['username'], stockNames=uniqueStocks)
    return render_template("home.html", logged_in=loggedIn)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/stock_list", methods=['GET', 'POST'])
def list():

    triggerView = False
    if request.form.get('trigger') == "True":
        triggerView = True
    else:
        triggerView = False

    loggedIn = 'username' in session

    stockName = request.form.get('stock')
    stockDates = sp500Stocks[sp500Stocks['Name'] == stockName]['date'].tolist()
    stockHighs = sp500Stocks[sp500Stocks['Name'] == stockName]['high'].tolist()

    return render_template(
        "stock_list.html",
        logged_in=loggedIn,
        stockNames=uniqueStocks,
        stock = stockName,
        stockDates=stockDates,
        stockHigh=stockHighs,
        view = triggerView
    )

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

@app.route('/explore', methods=['GET', 'POST'])
def explore():
    loggedIn = 'username' in session
    publicUsers = []
    portfolioList = []

    users = db.getAllTableData("users", "Privacy", "Public")
    if users != -1:
        for user in users:
            publicUsers.append(user[1])
    print(publicUsers)

    for user in publicUsers:
        port = db.getAllTableData("portfolio", "username", user)
        compile = []
        try:
            for item in port:
                compile.append(item[2])
        except:
            compile = []
        portfolioList.append(compile)

    print(portfolioList)
    return render_template("explore.html", publicUsers = publicUsers, logged_in = loggedIn)

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

if __name__ == "__main__":
    app.run(host='0.0.0.0')

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
from werkzeug.utils import secure_filename
from emojiTesting import emojiTranslator
import subprocess

from inferenceModel import predict_handwriting

DB_FILE = "cipher.db"
app = Flask(__name__)
app.secret_key = os.urandom(32)
anchor = False
app.config['UPLOAD_FOLDER'] = 'uploads'

if (not os.path.isfile("cipher.db")):
    db.setup()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

@app.route("/history", methods=['GET', 'POST'])
def history():
    loggedIn = 'username' in session

    emoji_history = []
    handwriting_history = []

    if loggedIn:
        user_id = session.get('user_id')
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        c = conn.cursor()

        c.execute("SELECT input, output FROM emoji WHERE user_id = ?", (user_id,))
        emoji_history = c.fetchall()

        c.execute("SELECT image_path, output FROM handwriting WHERE user_id = ?", (user_id,))
        handwriting_history = c.fetchall()

        conn.close()

    return render_template(
        "history.html",
        logged_in=loggedIn,
        emoji_history=emoji_history,
        handwriting_history=handwriting_history
    )


@app.route("/emoji", methods=['GET', 'POST'])
def emoji():
    logged_in = 'username' in session

    saved_text = ""
    processed_text = ""

    if request.method == 'POST':
        saved_text = request.form.get('user_text', '')
        processed_text = emojiTranslator.text_to_emoji_faiss(saved_text)  ## Ethan use this to do whatever you need to do with the text
        
        if logged_in:
            user_id = session['user_id']
            db.insert_emoji(user_id, user_input=saved_text, model_output=processed_text)


    return render_template("emoji.html", logged_in=logged_in, saved_text=saved_text, processed_text=processed_text)

@app.route("/handwriting", methods=['GET', 'POST'])
def handwriting():
    loggedIn = 'username' in session
    if request.method == 'POST':
        return render_template('handwriting.html', logged_in=loggedIn)
    return render_template('handwriting.html', logged_in=loggedIn)

@app.route("/handwriting-ajax", methods=["POST"])
def handwriting_ajax():
    file = request.files.get('image')
    if not file or file.filename == '' or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file"}), 400

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(save_path)

    result = predict_handwriting(save_path)

    return jsonify({"result_text": result})

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
            session['user_id'] = db.getUserID(username)
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
            session['user_id'] = db.getUserID(username)
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
    app.run(host='0.0.0.0', debug=False)

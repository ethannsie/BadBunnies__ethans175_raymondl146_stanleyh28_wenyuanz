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

DB_FILE = "db.py"
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

@app.route('/train', methods=['GET', 'POST'])
def train():
    loggedIn = 'username' in session
    result_text = None

    if request.method == 'POST':
        file = request.files.get('image')
        if not file or file.filename == '' or not allowed_file(file.filename):
            flash('Please upload a valid image.', 'error')
            return redirect(url_for('train'))

        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)

        result_text = process_image_file(save_path)

    # render whichever template contains your <main> form
    return render_template('train.html',
                           logged_in=loggedIn,
                           result_text=result_text)

@app.route("/results", methods=['GET', 'POST'])
def results():
    loggedIn = 'username' in session
    return render_template("results.html", logged_in=loggedIn)

@app.route("/history", methods=['GET', 'POST'])
def history():
    loggedIn = 'username' in session

    return render_template("history.html", logged_in=loggedIn)

@app.route("/emoji", methods=['GET', 'POST'])
def emoji():
    logged_in = 'username' in session

    saved_text = ""
    processed_text = ""

    if request.method == 'POST':
        saved_text = request.form.get('user_text', '')
        processed_text = emojiTranslator.text_to_emoji_faiss(saved_text)  ## Ethan use this to do whatever you need to do with the text

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

    result = subprocess.run(['python3', 'inferenceModel.py', save_path], capture_output=True, text=True)
    
    result_text = result.stdout.strip()
    result_text = ' '.join(result_text.split('\n', 1)[1:])

    return jsonify({"result_text": result_text})

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
    app.run(port=3000, debug = True, host='0.0.0.0')

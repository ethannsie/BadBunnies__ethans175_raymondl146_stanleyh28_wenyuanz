# Bad Bunnies
# SoftDev
# P05:
# 2025-06-XX
# Time Spent: not enough hours

import random
import os
import sqlite3
from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify, send_from_directory
import db
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from emojiTesting import emojiTranslator
import uuid
from pdf2image import convert_from_path
from PIL import Image
from google import genai
import secrets

# from inferenceModel import predict_handwriting

DB_FILE = "cipher.db"
app = Flask(__name__)
app.secret_key = os.urandom(32)
REGISTRATION_KEY = secrets.token_urlsafe(32)
anchor = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 MB


if (not os.path.isfile("cipher.db")):
    db.setup()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def predict_handwriting(folder_path):
    client = genai.Client(api_key=gemini_key)

    result = ""

    _, _, files = next(os.walk(folder_path))
    file_count = len(files)
    for i in range(file_count):
        img_file = os.path.join(folder_path, files[i])

        my_file = client.files.upload(file=img_file)

        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-05-20",
            contents=[my_file, "Extract text from this image, return just the text extracted."],
        )

        result += response.text

    return result.strip()

def is_admin():
    if 'username' in session:
        username = session['username']
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        c = conn.cursor()
        c.execute("SELECT is_admin FROM users WHERE username = ?", (username,))
        result = c.fetchone()
        conn.close()
        return result and result[0] == 1
    return 0

with open('keys/key_gemini.txt', 'r') as file:
    gemini_key = file.readline().strip()

@app.route("/", methods=['GET', 'POST'])
def home():
    loggedIn = 'username' in session
    if loggedIn:
        if is_admin():
            return render_template("home.html", logged_in=loggedIn, username=session['username'], admin=True)
        return render_template("home.html", logged_in=loggedIn, username=session['username'])
    return render_template("home.html", logged_in=loggedIn)


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


    print(handwriting_history)
    if is_admin():
        return render_template(
            "history.html",
            logged_in=loggedIn,
            emoji_history=emoji_history,
            handwriting_history=handwriting_history,
            admin=True
        )
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

    if is_admin():
        return render_template("emoji.html", logged_in=logged_in, saved_text=saved_text, processed_text=processed_text, admin=True)
    return render_template("emoji.html", logged_in=logged_in, saved_text=saved_text, processed_text=processed_text)

# Handwriting page
@app.route("/handwriting", methods=['GET', 'POST'])
def handwriting():
    loggedIn = 'username' in session
    if is_admin():
        return render_template('handwriting.html', logged_in=loggedIn, admin=True)
    return render_template('handwriting.html', logged_in=loggedIn)

# Gets handwriting predicted result
@app.route("/handwriting-ajax", methods=["POST"])
def handwriting_ajax():
    file = request.files.get('image')
    if not file or file.filename == '' or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file"}), 400

    session_id = str(uuid.uuid4())
    session_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    os.makedirs(session_dir, exist_ok=True)

    ext = os.path.splitext(file.filename)[1].lower()
    save_path = os.path.join(session_dir, secure_filename(file.filename))

    # # If PDF save each page as image
    # if ext == '.pdf':
    #     temp_pdf = os.path.join(session_dir, 'input.pdf')
    #     file.save(temp_pdf)

    #     # Convert each page of the PDF to an image
    #     images = convert_from_path(temp_pdf)
    #     for i, img in enumerate(images):
    #         img_path = os.path.join(session_dir, f'page_{i}.jpg')
    #         img.save(img_path, 'JPEG')
    # else:
    file.save(save_path)

    result = predict_handwriting(session_dir)

    if 'username' in session:
        user_id = session['user_id']
        db.insert_handwriting(user_id, image_path=save_path.removeprefix("uploads/"), model_output=result)

    return jsonify({"result_text": result})

@app.route("/transcriptions", methods=['GET', 'POST'])
def transcriptions():
    loggedIn = 'username' in session

    # 1. Fetch all approved handwriting rows (each row is an sqlite3.Row)
    approved_rows = db.get_approved_history()

    # 2. For each Row, look up the corresponding username
    enriched = []
    conn = sqlite3.connect(db.DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    for row in approved_rows:
        user_id = row['user_id']

        # Query the users table to get username for this user_id
        c.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
        user_row = c.fetchone()
        username = user_row['username'] if user_row else "Unknown"

        enriched.append({
            "username": username,
            "image_path": row['image_path'],
            "output": row['output']
        })

    conn.close()

    # 3. Pass this new list of dicts into the template
    if is_admin():
        return render_template(
            'transcriptions.html',
            logged_in=loggedIn,
            transcriptions=enriched,
            admin=True
        )
    else:
        return render_template(
            'transcriptions.html',
            logged_in=loggedIn,
            transcriptions=enriched
        )
@app.route("/admin", methods=['GET', 'POST'])
def admin():
    if is_admin():
        loggedIn = 'username' in session
        images= db.get_unapproved_images()
        return render_template(
            'admin.html',
            logged_in=loggedIn,
            images=images,
            admin=True
        )
    else:
        flash("You must be an admin to access this page", 'error')
        return redirect("/")

@app.route("/admin/approve/<int:image_id>", methods=["POST"])
def approve_image(image_id):
    if not is_admin():
        flash("Unauthorized", "error")
        return redirect("/")

    conn = sqlite3.connect(db.DB_FILE)
    c = conn.cursor()
    # Flip approved from 0 → 1
    c.execute(
        "UPDATE handwriting SET approved = 1 WHERE count = ?",
        (image_id,)
    )
    conn.commit()
    conn.close()

    flash(f"Image #{image_id} approved.", "success")
    return redirect("/admin")


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
        
@app.route('/register-admin', methods=['POST'])
def register_admin():
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        key = request.form.get('key')
        if key != REGISTRATION_KEY:
            return 'Invalid admin key — registration denied.'
        elif db.checkUser(username) >= 0:
            return "Username already exists. Please choose a different username."
        else:
            db.addUser(username, password, is_admin=True)
            return "Admin user registered successfully."
    except:
        return "Unable to register admin user. Please try again."

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

@app.route('/uploaded/<path:filename>')
def get_uploaded(filename):
    return send_from_directory('uploads', filename)


@app.errorhandler(RequestEntityTooLarge)
def handle_large_file(e):
    return jsonify({"error": "File too large. Max 500MB allowed."}), 413


if __name__=="__main__":
    print(f"Admin registration key: {REGISTRATION_KEY}")
    app.run(host='0.0.0.0', debug=True, port=3000)
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from config import Config
from database import db
from models import Question, UserProgress, User
import os
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bson import ObjectId

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app)
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

def send_email(to_email, subject, body):
    msg = MIMEMultipart('alternative')
    msg['From'] = app.config['MAIL_USERNAME']
    msg['To'] = to_email
    msg['Subject'] = subject

    html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reset Your Password</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;700&display=swap');
        body {{
            font-family: 'Space Grotesk', sans-serif;
            background: black;
            color: black;
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }}
        .email-container {{
            background: grey;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.3);
            max-width: 600px;
            padding: 20px;
            text-align: center;
        }}
        .logo-title {{
            display: flex;
            align-items: center;
            gap: 5px;
            justify-content: center;
            margin-bottom: 20px;
        }}
        .logo {{
            width: 24px;
            height: 24px;
            color: black;
        }}
        h1 {{
            font-size: 24px;
            font-weight: bold;
            margin: 0;
            text-align: center;
        }}
        p {{
            font-size: 16px;
            color: black;
        }}
        a {{
            display: inline-block;
            background: #61dafb;
            border: none;
            border-radius: 10px;
            color: black;
            padding: 10px 50px;
            text-decoration: none;
            margin-top: 20px;
            font-size: 16px;
            font-weight: 500;
        }}
        .footer {{
            margin-top: 20px;
            font-size: 12px;
            color: #aaaaaa;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="logo-title">
            <div class="logo">
                <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M6 6H42L36 24L42 42H6L12 24L6 6Z" fill="currentColor"></path>
                </svg>
            </div>
            <h1>Quantum Quest</h1>
        </div>
        <h1>Reset Your Password</h1>
        <p>Hi there,</p>
        <p>We received a request to reset your password. Click the button below to reset it.</p>
        <a href="{body}" target="_blank">Reset Password</a>
        <p>If you didn't request a password reset, please ignore this email or reply to let us know.</p>
        <p class="footer">This link will expire in 1 hour.</p>
    </div>
</body>
</html>
"""

    msg.attach(MIMEText(html_body, 'html'))

    try:
        with smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT']) as server:
            if app.config['MAIL_USE_TLS']:
                server.starttls()
            server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            server.sendmail(app.config['MAIL_USERNAME'], to_email, msg.as_string())
        print(f'Email sent to {to_email}')
        return True
    except Exception as e:
        print(f'Failed to send email to {to_email}: {e}')
        return False

@app.route('/')
def index():
    if 'user_id' in session:
        user = User.find_one({'_id': ObjectId(session['user_id'])})
        if user:
            welcome_message = f"Welcome back, {user['username']}!"
            flash(welcome_message)
            return render_template('index.html', welcome_message=welcome_message)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.find_one({'email': email})
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            return jsonify({'status': 'success', 'redirect': url_for('index')})
        else:
            return jsonify({'status': 'error', 'message': 'Invalid credentials'})
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        
        existing_user = User.find_one({'email': email})
        if existing_user:
            return jsonify({'status': 'error', 'message': 'Email already registered'})
        
        encoded_string = None
        if 'profile_picture' in request.files:
            profile_picture = request.files['profile_picture']
            if profile_picture.filename != '':
                try:
                    filename = secure_filename(profile_picture.filename)
                    profile_picture.save(os.path.join('uploads', filename))
                    
                    with open(os.path.join('uploads', filename), "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                except Exception as e:
                    return jsonify({'status': 'error', 'message': f'Error uploading file: {str(e)}'})
        
        try:
            user = User.insert_one({
                'username': username,
                'email': email,
                'password': password,
                'profile_picture': encoded_string
            })
            
            session['user_id'] = str(user.inserted_id)
            return jsonify({'status': 'success', 'redirect': url_for('index')})
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Error registering user: {str(e)}'})
    return render_template('register.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.find_one({'email': email})
        if user:
            token = s.dumps(email, salt='email-confirm')
            link = url_for('reset_password', token=token, _external=True)
            if send_email(email, 'Reset Your Password', link):
                return jsonify({'status': 'success', 'message': 'Email sent, check your inbox to reset your password'})
            else:
                return jsonify({'status': 'error', 'message': 'Failed to send email'})
        else:
            return jsonify({'status': 'error', 'message': 'Email is not registered with our app'})
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except SignatureExpired:
        return '<h1>The token is expired!</h1>'
    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            return jsonify({'status': 'error', 'message': 'Passwords do not match'})
        new_password = generate_password_hash(password)
        User.update_one({'email': email}, {'$set': {'password': new_password}})
        return jsonify({'status': 'success', 'message': 'Password reset successful', 'redirect': url_for('login')})
    return render_template('reset_password.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@socketio.on('message')
def handle_message(message):
    response_type = generate_response(message['text'])
    
    if response_type == "start_quiz":
        question = get_question(message['subject'], message['difficulty'])
        emit('question', {'id': str(question['_id']), 'text': question['question_text']})
    elif response_type == "answer_question":
        is_correct, explanation = check_answer(message['question_id'], message['answer'])
        update_user_progress(message['user_id'], message['subject'], is_correct)
        emit('result', {'correct': is_correct, 'explanation': explanation})
    elif response_type == "show_progress":
        progress = get_user_progress(message['user_id'])
        emit('progress', {'progress': progress})
    elif response_type == "provide_hint":
        question = Question.find_one({"_id": ObjectId(message['question_id'])})
        emit('hint', {'hint': f"Think about {question['subject']} concepts related to {question['question_text'].split()[0]}"})

def generate_response(text):
    if "start quiz" in text.lower():
        return "start_quiz"
    elif "answer" in text.lower():
        return "answer_question"
    elif "progress" in text.lower():
        return "show_progress"
    elif "hint" in text.lower():
        return "provide_hint"
    else:
        return "chat"

def get_question(subject, difficulty):
    return Question.find_one({"subject": subject, "difficulty": difficulty})

def check_answer(question_id, answer):
    question = Question.find_one({"_id": ObjectId(question_id)})
    is_correct = question["correct_answer"] == answer
    return is_correct, question["explanation"]

def update_user_progress(user_id, subject, is_correct):
    UserProgress.update_one(
        {"user_id": ObjectId(user_id), "subject": subject},
        {"$inc": {"correct_answers" if is_correct else "incorrect_answers": 1}},
        upsert=True
    )

def get_user_progress(user_id):
    return list(UserProgress.find({"user_id": ObjectId(user_id)}))

if __name__ == '__main__':
    socketio.run(app, debug=True)

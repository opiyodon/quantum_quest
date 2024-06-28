from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from models import User, Question, ChatHistory, UserProgress
from database import db
import openai
import os
import base64
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_object('config.Config')
socketio = SocketIO(app)
openai.api_key = os.getenv("OPENAI_API_KEY")
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
mail = Mail(app)

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
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.find_one({'_id': ObjectId(session['user_id'])})
    return render_template('index.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.find_one({'email': request.form['email']})
        if user and check_password_hash(user['password'], request.form['password']):
            session['user_id'] = str(user['_id'])
            return jsonify({'status': 'success', 'redirect': url_for('index')})
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

        if 'profile_picture' in request.files:
            profile_picture = request.files['profile_picture']
            if profile_picture.filename != '':
                filename = secure_filename(profile_picture.filename)
                profile_picture.save(os.path.join('uploads', filename))

                with open(os.path.join('uploads', filename), "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            else:
                encoded_string = None
        else:
            encoded_string = None

        user = User.insert_one({
            'username': username,
            'email': email,
            'password': password,
            'profile_picture': encoded_string
        })

        session['user_id'] = str(user.inserted_id)
        return jsonify({'status': 'success', 'redirect': url_for('index')})
    return render_template('register.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.find_one({'email': email})
        if user:
            token = s.dumps(email, salt='email-confirm')
            link = url_for('reset_password', token=token, _external=True)
            if send_email(email, 'Reset Your Password', f'Reset password link: {link}'):
                return jsonify({'status': 'success', 'message': 'Email sent, check your email to reset your password'})
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

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Not logged in'})

    user = User.find_one({'_id': ObjectId(session['user_id'])})
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'})

    updates = {}
    if 'username' in request.form:
        updates['username'] = request.form['username']
    if 'password' in request.form:
        updates['password'] = generate_password_hash(request.form['password'])
    if 'profile_picture' in request.files:
        file = request.files['profile_picture']
        if file:
            encoded_image = base64.b64encode(file.read()).decode('utf-8')
            updates['profile_picture'] = f"data:image/png;base64,{encoded_image}"

    if updates:
        User.update_one({'_id': ObjectId(session['user_id'])}, {'$set': updates})
        return jsonify({'status': 'success', 'message': 'Profile updated successfully'})
    return jsonify({'status': 'error', 'message': 'No updates provided'})

@socketio.on('user_message')
def handle_message(data):
    user_id = session.get('user_id')
    if not user_id:
        return

    user_message = data['message']

    # Call OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are Quantum Quest, an AI assistant specializing in science education."},
            {"role": "user", "content": user_message}
        ]
    )

    bot_response = response['choices'][0]['message']['content']

    # Save to chat history
    ChatHistory.create(user_id, user_message, bot_response)

    emit('bot_message', {'message': bot_response})

@app.route('/chat_history')
def chat_history():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Not logged in'})

    history = ChatHistory.find({'user_id': ObjectId(session['user_id'])})
    return jsonify({'status': 'success', 'history': list(history)})

@app.route('/delete_chat/<chat_id>')
def delete_chat(chat_id):
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Not logged in'})

    result = ChatHistory.delete_one({'_id': ObjectId(chat_id), 'user_id': ObjectId(session['user_id'])})
    if result.deleted_count:
        return jsonify({'status': 'success', 'message': 'Chat deleted'})
    return jsonify({'status': 'error', 'message': 'Chat not found or not authorized'})

@app.route('/clear_all_chats')
def clear_all_chats():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Not logged in'})

    result = ChatHistory.delete_many({'user_id': ObjectId(session['user_id'])})
    return jsonify({'status': 'success', 'message': f'{result.deleted_count} chats deleted'})

if __name__ == '__main__':
    socketio.run(app, debug=True)

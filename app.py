import json
import random
import numpy as np
import pickle
import os
import tempfile
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from config import Config
from database import db
from models import User, Chat
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bson import ObjectId
from pydub import AudioSegment
import speech_recognition as sr
from tensorflow import keras
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pyttsx3
import nltk
from nltk.stem import WordNetLemmatizer
from huggingface_models import text_generator, image_classifier, audio_classifier, video_classifier

nltk.download('punkt')
nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app)
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# Load trained model
model = keras.models.load_model('chatbot_model.keras')

# Load tokenizer object
with open('tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)

# Load label encoder object
with open('label_encoder.pickle', 'rb') as enc:
    lbl_encoder = pickle.load(enc)

# Load responses
with open('responses.pickle', 'rb') as resp:
    responses = pickle.load(resp)

# Load intents
with open('intents.json') as file:
    intents = json.load(file)

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
            return render_template('index.html', user=user)
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
        
        profile_picture_path = None
        if 'profile_picture' in request.files:
            profile_picture = request.files['profile_picture']
            if profile_picture.filename != '':
                try:
                    filename = secure_filename(profile_picture.filename)
                    filepath = os.path.join('static/uploads', filename)
                    
                    if not os.path.exists('static/uploads'):
                        os.makedirs('static/uploads')
                        
                    profile_picture.save(filepath)
                    
                    profile_picture_path = f'uploads/{filename}'
                except Exception as e:
                    return jsonify({'status': 'error', 'message': f'Error uploading file: {str(e)}'})
        
        try:
            user = User.insert_one({
                'username': username,
                'email': email,
                'password': password,
                'profile_picture': profile_picture_path
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

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'User not logged in'})

    user = User.find_one({'_id': ObjectId(session['user_id'])})
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'})

    username = request.form.get('username')
    password = request.form.get('password')
    profile_picture = request.files.get('profile_picture')

    update_data = {}

    if username and username != user['username']:
        update_data['username'] = username

    if password:
        update_data['password'] = generate_password_hash(password)

    if profile_picture:
        filename = secure_filename(profile_picture.filename)
        filepath = os.path.join('static/uploads', filename)
        
        if user.get('profile_picture'):
            old_filepath = os.path.join('static', user['profile_picture'])
            if os.path.exists(old_filepath):
                os.remove(old_filepath)
        
        profile_picture.save(filepath)
        update_data['profile_picture'] = f'uploads/{filename}'

    if update_data:
        User.update_one({'_id': ObjectId(session['user_id'])}, {'$set': update_data})
        return jsonify({'status': 'success', 'message': 'Profile updated successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'No changes made'})

@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'User not logged in'})

    user_id = ObjectId(session['user_id'])
    user = User.find_one({'_id': user_id})
    
    if user and user.get('profile_picture'):
        filepath = os.path.join('static', user['profile_picture'])
        if os.path.exists(filepath):
            os.remove(filepath)

    User.delete_one({'_id': user_id})
    Chat.delete_many({'user_id': str(user_id)})
    session.clear()
    return jsonify({'status': 'success', 'message': 'Account deleted successfully'})

@app.route('/chat_history')
def get_chat_history():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User not logged in'})

    chats = Chat.find({'user_id': user_id})
    history = []
    for chat in chats:
        if chat['messages']:
            history.append({'_id': str(chat['_id']), 'user_message': chat['messages'][0]['content']})
    return jsonify({'status': 'success', 'history': history})

@app.route('/load_chat/<chat_id>')
def load_chat(chat_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User not logged in'})

    chat = Chat.find_one({'_id': ObjectId(chat_id), 'user_id': user_id})
    if not chat:
        return jsonify({'status': 'error', 'message': 'Chat not found'})

    messages = [{'sender': msg['role'], 'content': msg['content']} for msg in chat['messages']]
    return jsonify({'status': 'success', 'chat': messages})

@app.route('/delete_chat/<chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User not logged in'})

    result = Chat.delete_one({'_id': ObjectId(chat_id), 'user_id': user_id})
    if result.deleted_count:
        return jsonify({'status': 'success', 'message': 'Chat deleted'})
    else:
        return jsonify({'status': 'error', 'message': 'Chat not found'})

@app.route('/clear_all_chats', methods=['POST'])
def clear_all_chats():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User not logged in'})

    result = Chat.delete_many({'user_id': user_id})
    return jsonify({'status': 'success', 'message': f'{result.deleted_count} chats deleted'})

@socketio.on('user_message')
def handle_user_message(data):
    user_message = data['message']
    response = generate_response(user_message)

    user_id = session.get('user_id')
    chat_id = session.get('chat_id')
    if not chat_id:
        chat_id = str(ObjectId())
        Chat.insert_one({'_id': ObjectId(chat_id), 'user_id': user_id, 'messages': []})
        session['chat_id'] = chat_id
    
    Chat.update_one(
        {'_id': ObjectId(chat_id)},
        {'$push': {'messages': {'role': 'user', 'content': user_message}}}
    )
    Chat.update_one(
        {'_id': ObjectId(chat_id)},
        {'$push': {'messages': {'role': 'bot', 'content': response}}}
    )

    emit('bot_message', {'message': response})

def generate_response(user_message):
    # Preprocess user_message
    padded_sequence = pad_sequences(tokenizer.texts_to_sequences([user_message]), maxlen=20, padding='post')
    
    # Predict intent of user_message using trained model
    prediction = model.predict(np.array(padded_sequence))
    tag = lbl_encoder.inverse_transform([np.argmax(prediction)])
    
    # Get response based on predicted tag
    if tag[0] in responses:
        local_response = random.choice(responses[tag[0]])
    else:
        local_response = "I'm not sure how to respond to that."

    enhanced_response = local_response

    # Text generation
    text_gen = text_generator(user_message, max_length=100, num_return_sequences=1)
    enhanced_response += f"\n\nAdditional context: {text_gen[0]['generated_text']}"

    # Image classification (if applicable)
    if 'image_data' in session:
        image_result = image_classifier(session['image_data'])
        enhanced_response += f"\n\nImage classification: {image_result[0]['label']}"

    # Audio classification (if applicable)
    if 'audio_path' in session:
        audio_result = audio_classifier(session['audio_path'])
        enhanced_response += f"\n\nAudio classification: {audio_result[0]['label']}"

    # Video classification (if applicable)
    if 'video_path' in session:
        video_result = video_classifier(session['video_path'])
        enhanced_response += f"\n\nVideo classification: {video_result[0]['label']}"

    return enhanced_response

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
        audio_file.save(temp_audio.name)
        try:
            audio = AudioSegment.from_file(temp_audio.name)
            audio.export(temp_audio.name, format="wav")

            recognizer = sr.Recognizer()
            with sr.AudioFile(temp_audio.name) as source:
                audio_data = recognizer.record(source)
                try:
                    text = recognizer.recognize_google(audio_data)
                    response_text = generate_response(text)
                    engine = pyttsx3.init()
                    engine.save_to_file(response_text, 'static/response.mp3')
                    engine.runAndWait()
                    return jsonify({'transcription': text, 'response': response_text, 'audio_response': '/static/response.mp3'})
                except sr.UnknownValueError:
                    return jsonify({'error': 'Could not understand audio'}), 400
                except sr.RequestError:
                    return jsonify({'error': 'Could not request results from speech recognition service'}), 500
        except Exception as e:
            return jsonify({'error': f'Error processing audio: {str(e)}'}), 500
        finally:
            os.unlink(temp_audio.name)

@app.route('/start_new_chat', methods=['POST'])
def start_new_chat():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User not logged in'})

    chat_id = str(ObjectId())
    Chat.insert_one({'_id': ObjectId(chat_id), 'user_id': user_id, 'messages': []})
    session['chat_id'] = chat_id

    return jsonify({'status': 'success', 'message': 'New chat started'})

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bow(sentence, words, show_details=True):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
                if show_details:
                    print(f"Found in bag: {w}")
    return np.array(bag)

def predict_class(sentence, model, words, classes):
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = [{"intent": classes[r[0]], "probability": str(r[1])} for r in results]
    return return_list

def get_response(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result

if __name__ == '__main__':
    socketio.run(app, debug=True)

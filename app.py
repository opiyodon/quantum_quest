from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from models import User, Question, ChatHistory
from database import db
from openai import OpenAI
import os
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
socketio = SocketIO(app)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are Quantum Quest, an AI assistant specializing in science education."},
            {"role": "user", "content": user_message}
        ]
    )
    
    bot_response = response.choices[0].message.content
    
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
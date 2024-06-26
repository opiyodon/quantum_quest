from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from config import Config
from database import db
from models import Question, UserProgress
from quiz_engine.question_handler import get_question, check_answer, update_user_progress, get_user_progress
from quiz_engine.response_generator import generate_response
from bson import json_util, ObjectId
import json

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

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
        emit('progress', {'progress': json.loads(json_util.dumps(list(progress)))})
    elif response_type == "provide_hint":
        question = Question.find_one({"_id": ObjectId(message['question_id'])})
        emit('hint', {'hint': f"Think about {question['subject']} concepts related to {question['question_text'].split()[0]}"})

if __name__ == '__main__':
    socketio.run(app, debug=True)
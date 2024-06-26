from models import Question, UserProgress
import random
from bson import ObjectId

def get_question(subject, difficulty):
    questions = list(Question.find({"subject": subject, "difficulty": difficulty}))
    return random.choice(questions) if questions else None

def check_answer(question_id, user_answer):
    question = Question.find_one({"_id": ObjectId(question_id)})
    is_correct = question["correct_answer"].lower() == user_answer.lower()
    return is_correct, question["explanation"]

def update_user_progress(user_id, subject, is_correct):
    UserProgress.update(
        {"user_id": user_id, "subject": subject},
        {
            "$inc": {
                "total_questions": 1,
                "correct_answers": 1 if is_correct else 0
            }
        }
    )

def get_user_progress(user_id):
    return UserProgress.find({"user_id": user_id})
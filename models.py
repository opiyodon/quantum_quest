from database import db
from bson import ObjectId

class Question:
    collection = db.questions

    @staticmethod
    def create(subject, difficulty, question_text, correct_answer, explanation):
        return Question.collection.insert_one({
            "subject": subject,
            "difficulty": difficulty,
            "question_text": question_text,
            "correct_answer": correct_answer,
            "explanation": explanation
        })

    @staticmethod
    def find(query):
        return Question.collection.find(query)

    @staticmethod
    def find_one(query):
        return Question.collection.find_one(query)

class UserProgress:
    collection = db.user_progress

    @staticmethod
    def create(user_id, subject, correct_answers=0, total_questions=0):
        return UserProgress.collection.insert_one({
            "user_id": user_id,
            "subject": subject,
            "correct_answers": correct_answers,
            "total_questions": total_questions
        })

    @staticmethod
    def find(query):
        return UserProgress.collection.find(query)

    @staticmethod
    def update(query, update):
        return UserProgress.collection.update_one(query, update, upsert=True)

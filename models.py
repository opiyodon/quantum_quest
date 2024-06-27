from database import db

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

class User:
    collection = db.users

    @staticmethod
    def create(username, email, password, profile_picture):
        return User.collection.insert_one({
            "username": username,
            "email": email,
            "password": password,
            "profile_picture": profile_picture
        })

    @staticmethod
    def find_one(query):
        return User.collection.find_one(query)

    @staticmethod
    def update_one(query, update):
        return User.collection.update_one(query, update)

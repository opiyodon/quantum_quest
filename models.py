from database import db
from bson import ObjectId

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

    @staticmethod
    def delete_one(query):
        return User.collection.delete_one(query)

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

class ChatHistory:
    collection = db.chat_history

    @staticmethod
    def create(user_id, user_message, bot_response):
        return ChatHistory.collection.insert_one({
            "user_id": ObjectId(user_id),
            "user_message": user_message,
            "bot_response": bot_response,
            "timestamp": datetime.utcnow()
        })

    @staticmethod
    def find(query):
        return ChatHistory.collection.find(query).sort("timestamp", -1)

    @staticmethod
    def delete_one(query):
        return ChatHistory.collection.delete_one(query)

    @staticmethod
    def delete_many(query):
        return ChatHistory.collection.delete_many(query)
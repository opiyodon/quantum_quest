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
    def insert_one(data):
        return User.collection.insert_one(data)

    @staticmethod
    def delete_one(query):
        return User.collection.delete_one(query)

class Chat:
    collection = db.chats

    @staticmethod
    def create(user_id, chat_id):
        return Chat.collection.insert_one({
            "_id": ObjectId(chat_id),
            "user_id": user_id,
            "messages": []
        })

    @staticmethod
    def add_message(chat_id, role, content):
        return Chat.collection.update_one(
            {"_id": ObjectId(chat_id)},
            {"$push": {"messages": {"role": role, "content": content}}}
        )

    @staticmethod
    def find(query):
        return Chat.collection.find(query)

    @staticmethod
    def find_one(query):
        return Chat.collection.find_one(query)

    @staticmethod
    def delete_one(query):
        return Chat.collection.delete_one(query)

    @staticmethod
    def delete_many(query):
        return Chat.collection.delete_many(query)

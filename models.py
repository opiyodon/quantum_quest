from pymongo import MongoClient
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

client = MongoClient('mongodb://localhost:27017/')
db = client['chatbot']

class User:
    @staticmethod
    def insert_one(user_data):
        try:
            result = db.users.insert_one(user_data)
            return result
        except Exception as e:
            raise e

    @staticmethod
    def find_one(query):
        try:
            user = db.users.find_one(query)
            return user
        except Exception as e:
            raise e

    @staticmethod
    def update_one(query, update_data):
        try:
            result = db.users.update_one(query, update_data)
            return result
        except Exception as e:
            raise e

class UserProgress:
    @staticmethod
    def insert_one(progress_data):
        try:
            result = db.user_progress.insert_one(progress_data)
            return result
        except Exception as e:
            raise e

    @staticmethod
    def find(query):
        try:
            progress = db.user_progress.find(query)
            return progress
        except Exception as e:
            raise e

class Chat:
    @staticmethod
    def insert_one(chat_data):
        try:
            result = db.chats.insert_one(chat_data)
            return result
        except Exception as e:
            raise e

    @staticmethod
    def find(query):
        try:
            chats = db.chats.find(query)
            return chats
        except Exception as e:
            raise e

class Question:
    @staticmethod
    def insert_one(question_data):
        try:
            result = db.questions.insert_one(question_data)
            return result
        except Exception as e:
            raise e

    @staticmethod
    def find(query):
        try:
            questions = db.questions.find(query)
            return questions
        except Exception as e:
            raise e

from pymongo import MongoClient
from config import Config

client = MongoClient(Config.MONGODB_URI)
db = client.get_default_database()
from pymongo.errors import PyMongoError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from bson.objectid import ObjectId

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.password_hash = user_data['password']

class UserDAO:
    def __init__(self, mongo):
        self.mongo = mongo

    def create_user(self, username, password):
        try:
            hashed_password = generate_password_hash(password)
            self.mongo.db.users.insert_one({
                "username": username,
                "password": hashed_password
            })
            return True
        except PyMongoError as e:
            print(f"Error creating user: {e}")
            return False

    def get_user_by_username(self, username):
        try:
            user_data = self.mongo.db.users.find_one({"username": username})
            if user_data:
                return User(user_data)
        except PyMongoError:
            return None
        return None

    def get_user_by_id(self, user_id):
        try:
            user_data = self.mongo.db.users.find_one({"_id": ObjectId(user_id)})
            if user_data:
                return User(user_data)
        except:
            return None
        return None
    
    def check_credentials(self, username, password):
        user_data = self.mongo.db.users.find_one({"username": username})
        if user_data and check_password_hash(user_data['password'], password):
            return User(user_data)
        return None
from flask_pymongo import PyMongo
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId

class ClientDAO:
    def __init__(self, mongo: PyMongo):
        self.mongo = mongo

    def create_client(self, data):
        try:
            self.mongo.db.clients.insert_one(data)
            return True
        except PyMongoError as e:
            print(f"Error creating client: {e}")
            return False

    def read_client(self, id_client):
        try:
            return self.mongo.db.clients.find_one({"_id": ObjectId(id_client)})
        except PyMongoError as e:
            print(f"Error reading client: {e}")
            return None

    def update_client(self, id_client, data):
        try:
            result = self.mongo.db.clients.update_one({"_id": ObjectId(id_client)}, {"$set": data})
            return result.modified_count > 0
        except PyMongoError as e:
            print(f"Error updating client: {e}")
            return False

    def delete_client(self, id_client):
        try:
            # Verificar si el cliente existe antes de intentar eliminarlo
            client = self.mongo.db.clients.find_one({"_id": ObjectId(id_client)})
            if not client:
                print("Client not found")
                return False
            result = self.mongo.db.clients.delete_one({"_id": ObjectId(id_client)})
            return result.deleted_count > 0
        except PyMongoError as e:
            print(f"Error deleting client: {e}")
            return False



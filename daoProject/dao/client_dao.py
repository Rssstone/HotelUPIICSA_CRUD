from flask_pymongo import PyMongo
from pymongo.errors import PyMongoError, DuplicateKeyError
from bson.objectid import ObjectId
import pymongo

class ClientDAO:
    def __init__(self, mongo: PyMongo):
        self.mongo = mongo
        try:
            self.mongo.db.clients.create_index([("room", pymongo.ASCENDING)], unique=True)
            print("--- [SISTEMA] Índice único de habitaciones verificado ---")
        except Exception as e:
            print(f"--- [ADVERTENCIA] No se pudo activar la restricción única: {e} ---")

    def get_occupied_rooms(self):
        try:
            cursor = self.mongo.db.clients.find({}, {"room": 1, "_id": 0})
            return [int(doc['room']) for doc in cursor if 'room' in doc]
        except PyMongoError as e:
            print(f"Error fetching occupied rooms: {e}")
            return []

    def create_client(self, data):
        try:
            room_to_check = int(data.get('room'))
            
            if self.mongo.db.clients.find_one({"room": room_to_check}):
                return False

            new_client = {
                "name": data['name'],
                "email": data['email'],
                "days": int(data['days']),
                "room": room_to_check
            }
            
            self.mongo.db.clients.insert_one(new_client)
            return True

        except DuplicateKeyError:
            return False
        except (PyMongoError, ValueError) as e:
            print(f"Error creating client: {e}")
            return False

    def read_client(self, id_client):
        try:
            return self.mongo.db.clients.find_one({"_id": ObjectId(id_client)})
        except PyMongoError:
            return None

    def update_client(self, id_client, data):
        try:
            if 'room' in data:
                room_to_check = int(data['room'])
                existing = self.mongo.db.clients.find_one({"room": room_to_check})
                
                if existing and str(existing['_id']) != id_client:
                    raise ValueError("Error: La habitación ya está ocupada.")
                
                data['room'] = room_to_check

            result = self.mongo.db.clients.update_one({"_id": ObjectId(id_client)}, {"$set": data})
            return result.matched_count > 0
        except ValueError:
            raise
        except PyMongoError:
            return False

    def delete_client(self, id_client):
        try:
            result = self.mongo.db.clients.delete_one({"_id": ObjectId(id_client)})
            return result.deleted_count > 0
        except PyMongoError:
            return False
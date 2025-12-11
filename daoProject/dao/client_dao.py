from flask_pymongo import PyMongo
from pymongo.errors import PyMongoError, DuplicateKeyError # Importante: Importar DuplicateKeyError
from bson.objectid import ObjectId
import pymongo

class ClientDAO:
    def __init__(self, mongo: PyMongo):
        self.mongo = mongo
        # Configuración de Base de Datos: Crear Índice Único
        # Esto obliga a MongoDB a impedir habitaciones duplicadas físicamente.
        try:
            self.mongo.db.clients.create_index([("room", pymongo.ASCENDING)], unique=True)
            print("--- [SISTEMA] Índice único de habitaciones verificado ---")
        except Exception as e:
            # Si falla (por ejemplo, si ya tienes duplicados sucios en la BD), avisa en consola
            print(f"--- [ADVERTENCIA] No se pudo activar la restricción única: {e} ---")
            print("--- Por favor, elimina los registros duplicados manualmente para activar la protección. ---")

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
            
            # Validación de aplicación (rápida, pero no infalible ante clics dobles)
            if self.mongo.db.clients.find_one({"room": room_to_check}):
                print(f"Bloqueo App: Habitación {room_to_check} ocupada.")
                return False

            new_client = {
                "name": data['name'],
                "email": data['email'],
                "days": int(data['days']),
                "room": room_to_check
            }
            
            # La inserción real. Si pasa la validación de arriba por error,
            # el Índice Único de MongoDB detendrá esto y lanzará DuplicateKeyError.
            self.mongo.db.clients.insert_one(new_client)
            return True

        except DuplicateKeyError:
            print(f"Bloqueo DB: Intento de duplicar habitación {room_to_check} detenido.")
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
            # Nota: Si se permite cambiar habitación al editar, aquí también podría saltar DuplicateKeyError
            self.mongo.db.clients.update_one({"_id": ObjectId(id_client)}, {"$set": data})
            return True
        except PyMongoError:
            return False

    def delete_client(self, id_client):
        try:
            result = self.mongo.db.clients.delete_one({"_id": ObjectId(id_client)})
            return result.deleted_count > 0
        except PyMongoError:
            return False
from flask import Blueprint, request, jsonify, render_template
from dao.client_dao import ClientDAO
from pymongo.errors import PyMongoError
from flask_login import login_required

client_controller = Blueprint('client_controller', __name__)
client_dao = None

def init_controller(mongo):
    global client_dao
    client_dao = ClientDAO(mongo)

@client_controller.route('/clients/create/', methods=['GET', 'POST'])
@login_required
def create_client():
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify(message="No data provided"), 400
        try:
            client_dao.create_client(data)
            return jsonify(message="Client created"), 201
        except PyMongoError as e:
            return jsonify(message=f"Error creating client: {e}"), 500
    return render_template('create_client.html')

@client_controller.route('/clients/read/', methods=['GET'])
@login_required
def read_clients():
    try:
        clients = list(client_dao.mongo.db.clients.find())
        return render_template('read_clients.html', clients=clients)
    except PyMongoError as e:
        return jsonify(message=f"Error reading clients: {e}"), 500

@client_controller.route('/clients/read/<id_client>', methods=['GET'])
@login_required
def read_client(id_client):
    try:
        client = client_dao.read_client(id_client)
        if client:
            return jsonify(client), 200
        else:
            return jsonify(message="Client not found"), 404
    except PyMongoError as e:
        return jsonify(message=f"Error reading client: {e}"), 500

@client_controller.route('/clients/update/<id_client>', methods=['GET', 'POST'])
@login_required
def update_client(id_client):
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify(message="No data provided"), 400
            
            success = client_dao.update_client(id_client, data)
            if success:
                return jsonify(message="Client updated"), 200
            else:
                return jsonify(message="Client not found"), 404
        except PyMongoError as e:
            return jsonify(message=f"Error updating client: {e}"), 500

    client = client_dao.read_client(id_client)
    if client:
        return render_template('update_client.html', client=client)
    else:
        return jsonify(message="Client not found"), 404

@client_controller.route('/clients/delete/<id_client>', methods=['GET'])
@login_required
def delete_client(id_client):
    try:
        success = client_dao.delete_client(id_client)
        if success:
            return jsonify(message="Client deleted"), 200
        else:
            return jsonify(message="Client not found"), 404
    except PyMongoError as e:
        return jsonify(message=f"Error deleting client: {e}"), 500
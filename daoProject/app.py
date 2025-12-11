from flask import Flask, render_template, redirect, url_for, request, flash
from flask_pymongo import PyMongo
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from controllers.client_controller import client_controller, init_controller
from dao.user_dao import UserDAO

app = Flask(__name__)
app.secret_key = "upiicsa_hotel_secure_key_2025" 
app.config["MONGO_URI"] = "mongodb://localhost:27017/clients"

mongo = PyMongo(app)
user_dao = UserDAO(mongo)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return user_dao.get_user_by_id(user_id)

init_controller(mongo)
app.register_blueprint(client_controller) 

def ensure_admin_exists():
    admin_email = "jcruzadmin@upiicsa.com"
    admin_pass = "Upiicsa2025"
    
    with app.app_context():
        if not user_dao.get_user_by_username(admin_email):
            print(f"--- [HOTEL SYSTEM] Creando Cuenta Gerencial: {admin_email} ---")
            user_dao.create_user(admin_email, admin_pass)
        else:
            print(f"--- [HOTEL SYSTEM] Gerente {admin_email} verificado ---")

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = user_dao.check_credentials(username, password)
        
        if user:
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Credenciales de personal inválidas.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Turno finalizado. Sesión cerrada.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    ensure_admin_exists()
    app.run(debug=True, use_reloader=False)
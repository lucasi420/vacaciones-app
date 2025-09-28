from flask import Flask
from models import db, User
import os
import random

# --- Configuración (DEBE ser idéntica a app.py) ---
app = Flask(__name__)
app.config["SECRET_KEY"] = "clave-secreta-muy-dificil-y-larga-para-produccion"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(app.root_path, "vacaciones.db") 
db.init_app(app)

# Paleta de colores (debe ser la misma que en app.py)
COLOR_PALETTE = [
    "#4285F4", "#34A853", "#FBBC05", "#673AB7", "#009688", "#76A0D7", "#8E24AA",
    "#00BCD4", "#FF9800", "#795548", "#4CAF50", "#FFEB3B", "#03A9F4", "#CDDC39", 
    "#FFC107", "#E67C73", "#757575", "#00AEEF"
]

USUARIOS_A_CARGAR = [
    {"username": "SUPER", "password": "SUPER2025", "is_admin": True}, 
    {"username": "fionna.lucas", "password": "Mendoza2025", "is_admin": False},
    {"username": "orue.hernan", "password": "BuenosAires2025", "is_admin": False},
    {"username": "fazzi.juan", "password": "TDF2025", "is_admin": False},
]

def initialize_users():
    """Crea las tablas y precarga los usuarios si no existen."""
    
    # Asegura que la DB se cree
    db.create_all()     
    
    random.shuffle(COLOR_PALETTE)
    empleado_colors = iter(COLOR_PALETTE)

    for user_data in USUARIOS_A_CARGAR:
        if not User.query.filter_by(username=user_data['username']).first():
            
            # Asignar color si es empleado
            color = next(empleado_colors) if not user_data.get('is_admin') else "#000000"

            new_user = User(
                username=user_data['username'],
                password=user_data['password'], 
                is_admin=user_data.get('is_admin', False),
                color=color
            )
            db.session.add(new_user)
            
    db.session.commit()
    print("Base de datos y usuarios inicializados exitosamente.")
    
# Ejecutamos la inicialización
with app.app_context():
    initialize_users()

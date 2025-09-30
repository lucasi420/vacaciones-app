from flask import Flask
from models import db, User # Asumo que models.py tiene tus clases de SQLAlchemy
import os
import random

# --- Configuración (DEBE ser idéntica a app.py) ---
# Usamos la clase Flask para cargar la configuración, aunque no es un servidor
app = Flask(__name__)

# NOTA: En producción, Render inyectará SECRET_KEY y DATABASE_URL
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "clave-secreta-por-defecto") 
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL") 
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False # Siempre recomendado en Flask-SQLAlchemy

db.init_app(app)

# Paleta de colores para los empleados
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
    
    # 1. Crea las tablas en la DB conectada por DATABASE_URL
    db.create_all()     
    
    random.shuffle(COLOR_PALETTE)
    empleado_colors = iter(COLOR_PALETTE)

    for user_data in USUARIOS_A_CARGAR:
        # 2. Verifica si el usuario ya existe
        if not User.query.filter_by(username=user_data['username']).first():
            
            # 3. Asigna el color
            color = next(empleado_colors) if not user_data.get('is_admin') else "#000000"
            
            # 4. Crea el nuevo objeto de usuario
            new_user = User(
                username=user_data['username'],
                password=user_data['password'], 
                is_admin=user_data.get('is_admin', False),
                color=color
            )
            db.session.add(new_user)
            
    # 5. Guarda todos los cambios
    db.session.commit()
    print("Base de datos y usuarios inicializados exitosamente.")
    
# Ejecutamos la inicialización
with app.app_context():
    initialize_users()

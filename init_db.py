from flask import Flask
from models import db, User # Importamos User para poder crearlos
import os
import random

# --- Configuración (DEBE ser idéntica a app.py) ---
# Usamos una clave de fallback si no se encuentra SECRET_KEY en el entorno
from config import Config 

# Usamos Flask para crear el contexto de la aplicación
app = Flask(__name__)
# Cargamos la configuración (que incluye DATABASE_URL de os.getenv)
app.config.from_object(Config)

# Inicializamos DB
db.init_app(app)

# Paleta de colores para empleados
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


def initialize_users_and_db():
    """Crea las tablas y precarga los usuarios si no existen."""
    
    print("Iniciando conexión y creación de tablas y usuarios iniciales...")
    
    try:
        # 1. Asegura que la DB y el contexto estén listos
        db.create_all()     
        
        random.shuffle(COLOR_PALETTE)
        empleado_colors = iter(COLOR_PALETTE)

        # 2. Carga de usuarios fijos
        for user_data in USUARIOS_A_CARGAR:
            # Verifica si el usuario ya existe para no duplicarlo
            if not User.query.filter_by(username=user_data['username']).first():
                
                # Asignar color (negro para admin, colores rotativos para otros)
                color = "#000000" if user_data.get('is_admin') else next(empleado_colors)
                
                # CREACIÓN DEL OBJETO (¡Constructor corregido!)
                new_user = User(
                    username=user_data['username'],
                    password=user_data['password'], 
                    is_admin=user_data.get('is_admin', False),
                    color=color
                )
                db.session.add(new_user)
                print(f"-> Usuario creado: {new_user.username}")
                
        db.session.commit()
        print("✅ Base de datos y usuarios inicializados exitosamente.")
        
    except Exception as e:
        print(f"❌ ERROR CRÍTICO al inicializar DB o usuarios: {e}")
        # Detenemos el proceso si hay fallo de conexión/driver
        raise e 
    
# Ejecutamos la inicialización
with app.app_context():
    initialize_users_and_db()

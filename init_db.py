from flask import Flask
from models import db, User 
from config import Config
import os
import random
from sqlalchemy.exc import ProgrammingError, OperationalError
# IMPORTACIÓN CRÍTICA PARA GENERAR HASHEOS
from werkzeug.security import generate_password_hash 


# --- Configuración (DEBE ser idéntica a app.py) ---
app = Flask(__name__)
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
        db.create_all()     
        
        print("✅ Tablas creadas (o ya existentes).")
        random.shuffle(COLOR_PALETTE)
        empleado_colors = iter(COLOR_PALETTE)

        # 2. Carga de usuarios fijos - Protegida con try/except
        try:
            for user_data in USUARIOS_A_CARGAR:
                if not User.query.filter_by(username=user_data['username']).first():
                    
                    color = "#000000" if user_data.get('is_admin') else next(empleado_colors)
                    
                    # 🔑 CORRECCIÓN DE SEGURIDAD: HASHEAMOS LA CONTRASEÑA ANTES DE GUARDARLA
                    hashed_password = generate_password_hash(user_data['password'])
                    
                    # CREACIÓN DEL OBJETO
                    new_user = User(
                        username=user_data['username'],
                        password=hashed_password,  # <-- Guardamos el hash
                        is_admin=user_data.get('is_admin', False),
                        color=color
                    )
                    db.session.add(new_user)
                    print(f"-> Usuario creado: {new_user.username}")
                    
            db.session.commit()
            print("✅ Usuarios inicializados exitosamente.")

        except (ProgrammingError, OperationalError) as e:
            db.session.rollback()
            print(f"⚠️ Aviso: Falló la creación de usuarios iniciales: {e}")
            print("         El servidor intentará continuar.")
            
    except Exception as e:
        print(f"❌ ERROR CRÍTICO al inicializar DB o usuarios: {e}")
        print("El servicio intentará continuar con Gunicorn...")
    
# Ejecutamos la inicialización
with app.app_context():
    initialize_users_and_db()

from flask import Flask
# Asumimos que models.py tiene 'db', 'User', y 'Vacation'
from models import db, User 
# Importamos la configuración local
from config import Config
import os
import random
# Usaremos esto para hashear las contraseñas
from werkzeug.security import generate_password_hash 


# --- Configuración (DEBE ser idéntica a app.py) ---
# La app necesita la configuración para saber cómo conectarse a la DB (DATABASE_URL)
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Paleta de colores para empleados
COLOR_PALETTE = [
    "#4285F4", "#34A853", "#FBBC05", "#673AB7", "#009688", "#76A0D7", "#8E24AA",
    "#00BCD4", "#FF9800", "#795548", "#4CAF50", "#FFEB3B", "#03A9F4", "#CDDC39", 
    "#FFC107", "#E67C73", "#757575", "#00AEEF"
]

# Usuarios iniciales
USUARIOS_A_CARGAR = [
    {"username": "SUPER", "password": "SUPER2025", "is_admin": True}, 
    {"username": "fionna.lucas", "password": "Mendoza2025", "is_admin": False},
    {"username": "orue.hernan", "password": "BuenosAires2025", "is_admin": False},
    {"username": "fazzi.juan", "password": "TDF2025", "is_admin": False},
]


def initialize_users_and_db():
    """
    Crea las tablas en la base de datos de Neon y precarga los usuarios iniciales 
    con contraseñas hasheadas. Esta función debe ejecutarse una sola vez.
    """
    
    print("--- 🛠️ Iniciando creación de tablas y usuarios iniciales en Neon... ---")
    
    # Intentamos crear todas las tablas definidas en models.py
    try:
        db.create_all()     
        print("✅ Tablas creadas (o ya existentes).")
    except Exception as e:
        print(f"❌ ERROR: No se pudieron crear las tablas. ¿Es correcta la DATABASE_URL? Detalle: {e}")
        # Si las tablas no se pueden crear, la carga de usuarios fallará
        return
        
    random.shuffle(COLOR_PALETTE)
    empleado_colors = iter(COLOR_PALETTE)

    # 2. Carga de usuarios fijos
    try:
        for user_data in USUARIOS_A_CARGAR:
            # Solo crea el usuario si no existe
            if not User.query.filter_by(username=user_data['username']).first():
                
                # Asigna un color aleatorio del pool o negro para el admin
                color = "#000000" if user_data.get('is_admin') else next(empleado_colors)
                
                # 🔑 IMPORTANTE: HASHEAMOS la contraseña
                hashed_password = generate_password_hash(user_data['password'])
                
                # CREACIÓN DEL OBJETO
                new_user = User(
                    username=user_data['username'],
                    password=hashed_password,  # Guardamos el hash
                    is_admin=user_data.get('is_admin', False),
                    color=color
                )
                db.session.add(new_user)
                print(f"-> Usuario creado y hasheado: {new_user.username}")
                
        db.session.commit()
        print("✅ Usuarios inicializados y guardados exitosamente.")

    except StopIteration:
        db.session.rollback()
        print("⚠️ Aviso: Se agotaron los colores para asignar a los usuarios.")
    except Exception as e:
        db.session.rollback()
        print(f"❌ ERROR al crear usuarios: {e}")


# Ejecutamos la inicialización dentro del contexto de la aplicación
with app.app_context():
    initialize_users_and_db()

print("--- 🏁 Inicialización de la base de datos terminada. ---")

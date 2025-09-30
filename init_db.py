from flask import Flask
from models import db, User 
from config import Config
import os
import random
from sqlalchemy.exc import ProgrammingError, OperationalError

# --- Configuración (DEBE ser idéntica a app.py) ---
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
        # 1. PASO CRÍTICO: CREAR LAS TABLAS. Esto debe ir primero.
        db.create_all()     
        
        print("✅ Tablas creadas (o ya existentes).")
        random.shuffle(COLOR_PALETTE)
        empleado_colors = iter(COLOR_PALETTE)

        # 2. Carga de usuarios fijos - Protegida con try/except
        try:
            for user_data in USUARIOS_A_CARGAR:
                # Verifica si el usuario ya existe para no duplicarlo
                # Esta consulta es la que fallaba al inicio
                if not User.query.filter_by(username=user_data['username']).first():
                    
                    # Asignar color (negro para admin, colores rotativos para otros)
                    color = "#000000" if user_data.get('is_admin') else next(empleado_colors)
                    
                    # CREACIÓN DEL OBJETO
                    new_user = User(
                        username=user_data['username'],
                        password=user_data['password'], 
                        is_admin=user_data.get('is_admin', False),
                        color=color
                    )
                    db.session.add(new_user)
                    print(f"-> Usuario creado: {new_user.username}")
                    
            db.session.commit()
            print("✅ Usuarios inicializados exitosamente.")

        except (ProgrammingError, OperationalError) as e:
            # Capturamos errores si la tabla aún no es visible para el query,
            # pero permitimos que el servidor arranque.
            db.session.rollback()
            print(f"⚠️ Aviso: Falló la creación de usuarios iniciales: {e}")
            print("         Esto es normal si las tablas acaban de ser creadas. El servidor continuará.")
            
    except Exception as e:
        # Si falla db.create_all() o algo más, logueamos el error y permitimos arrancar Gunicorn.
        print(f"❌ ERROR CRÍTICO al inicializar DB o usuarios: {e}")
        # NO usamos 'raise e' para evitar que Render detenga todo el despliegue.
        print("El servicio intentará continuar con Gunicorn...")
    
# Ejecutamos la inicialización
with app.app_context():
    initialize_users_and_db()

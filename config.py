import os
from sqlalchemy.pool import NullPool

class Config:
    # --- Configuración Estándar de Flask ---
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "clave-secreta-por-defecto")
    
    # --- Configuración CRÍTICA para Supabase (Pooler) ---
    
    # ¡IMPORTANTE! NullPool y un Timeout bajo previenen el Worker Timeout de Render.
    SQLALCHEMY_ENGINE_OPTIONS = {
        "poolclass": NullPool, 
        "pool_recycle": 300,
        "pool_pre_ping": True,
        
        # 🚨 AÑADE ESTO: Tiempo de espera bajo para la conexión
        # Si la base de datos no responde en 5 segundos, la conexión fallará rápido,
        # liberando el worker de Render antes de que expire.
        "connect_args": {
            "connect_timeout": 5  # 5 segundos
        }
    }

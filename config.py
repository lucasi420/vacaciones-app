import os
from sqlalchemy.pool import NullPool

class Config:
    # --- Configuración Estándar de Flask ---
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "clave-secreta-por-defecto")
    
    # --- Configuración CRÍTICA para Supabase (Pooler) ---
    
    # 1. CRÍTICO: Deshabilita el pool de conexiones de SQLAlchemy.
    # Esto evita conflictos con el Pooler de Supabase (Supavisor/Pgbouncer).
    # ¡Necesario para resolver errores de conexión y timeout!
    SQLALCHEMY_ENGINE_OPTIONS = {
        "poolclass": NullPool,  # <--- ESTE ES EL CAMBIO CLAVE
        
        # 2. Configuración de salud/vida de la conexión (Mantenido de tu código)
        "pool_recycle": 300,  # Recicla conexiones después de 5 minutos (300 segundos)
        "pool_pre_ping": True # Prueba la conexión antes de usarla
    }


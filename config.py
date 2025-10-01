import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "clave-secreta-por-defecto")
    
    # CRÍTICO: Configuración para trabajar con el Pooler de Supabase/Pgbouncer.
    # Esto asegura que las conexiones inactivas se cierren y se vuelvan a abrir correctamente.
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,  # Recicla conexiones después de 5 minutos de inactividad
        "pool_pre_ping": True # Prueba la conexión antes de usarla
    }

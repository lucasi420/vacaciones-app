FROM python:3.11-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# 🚀 NUEVOS PASOS CRÍTICOS: Instalar dependencias de PostgreSQL a nivel de sistema
# 1. Instalar herramientas de compilación (build-essential)
# 2. Instalar el paquete de desarrollo de PostgreSQL (libpq-dev)
# 3. Limpiar los archivos temporales para mantener la imagen pequeña
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copiar requisitos primero
COPY requirements.txt .

# Instalar dependencias de Python (que ahora podrán usar libpq-dev)
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Puerto que usará Render
ENV PORT=10000

# Ejecutar Gunicorn directamente
CMD gunicorn --bind 0.0.0.0:$PORT app:app

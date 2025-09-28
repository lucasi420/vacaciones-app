# 1. ESPECIFICAR LA VERSIÓN DE PYTHON 3.11
FROM python:3.11-slim

# 2. CONFIGURAR EL DIRECTORIO DE TRABAJO
WORKDIR /app

# 3. COPIAR REQUISITOS E INSTALAR DEPENDENCIAS
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. COPIAR EL RESTO DEL CÓDIGO
COPY . .

# 5. EXPONER EL PUERTO (Render usa la variable PORT automáticamente)
# EXPOSE 8080 

# 6. COMANDO DE INICIO (Ajuste 'mi_app:app' a su archivo y objeto Flask/FastAPI)
CMD gunicorn --bind 0.0.0.0:$PORT mi_app:app

FROM python:3.11-slim

# 1. Configurar variables de entorno para el entorno virtual (venv)
ENV VIRTUAL_ENV=/venv
# Añadimos /venv/bin al PATH para que Gunicorn se encuentre fácilmente
ENV PATH="/venv/bin:$PATH"

# 2. Establecer el directorio de trabajo
WORKDIR /app

# 3. Copiar requisitos e instalar dependencias DENTRO del venv
COPY requirements.txt .
# Crea el entorno virtual
RUN python3 -m venv $VIRTUAL_ENV
# Instala las dependencias en el entorno virtual
# Nota: La instalación es DENTRO del venv, gracias al PATH.
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiar el resto del código (incluyendo app.py, models.py, init_db.py y templates)
COPY . .

# 5. Comando de inicio
# CRÍTICO: Ejecutamos init_db.py (crea la DB y usuarios) y luego,
# si es exitoso (&&), iniciamos Gunicorn.
CMD python init_db.py && gunicorn --bind 0.0.0.0:$PORT app:app

FROM python:3.11-slim

# 1. Configurar variables de entorno para el entorno virtual (venv)
ENV VIRTUAL_ENV=/venv
ENV PATH="/venv/bin:$PATH"

# 2. Establecer el directorio de trabajo
WORKDIR /app

# 3. Copiar requisitos e instalar dependencias DENTRO del venv
COPY requirements.txt .
# Crea el entorno virtual
RUN python3 -m venv $VIRTUAL_ENV
# Instala las dependencias en el entorno virtual
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiar el resto del código
COPY . .

# 5. Comando de inicio
# Gunicorn ahora será encontrado a través del PATH /venv/bin
# Asegúrese de que 'mi_app:app' coincida con su archivo y objeto de aplicación
CMD gunicorn --bind 0.0.0.0:$PORT mi_app:app

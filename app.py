from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from models import db, User, Vacation
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import pandas as pd
import io

app = Flask(__name__)

# Clave secreta
app.config["SECRET_KEY"] = "clave-secreta-muy-dificil"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///vacaciones.db"

# Inicializamos DB y LoginManager
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' 
# ----------------------------------------------------------------------


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
@login_required
def home():
    return redirect(url_for("loading"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for("loading"))
        return "Usuario o contraseña incorrectos"

    return render_template("login.html")


@app.route("/loading")
@login_required
def loading():
    return render_template("loading.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/calendar")
@login_required
def calendar():
    return render_template("calendar.html")


@app.route("/add_vacation", methods=["POST"])
@login_required
def add_vacation():
    data = request.get_json()
    fecha = data.get("date")

    if fecha:
        vaca = Vacation(user_id=current_user.id, date=fecha)
        db.session.add(vaca)
        db.session.commit()
        return jsonify({"success": True}), 200
    return jsonify({"success": False}), 400


@app.route("/toggle_vacation", methods=["POST"])
@login_required
def toggle_vacation():
    data = request.get_json()
    fecha = data.get("date")

    if not fecha:
        return jsonify({"success": False}), 400

    vaca = Vacation.query.filter_by(user_id=current_user.id, date=fecha).first()
    if vaca:
        db.session.delete(vaca)  # Desmarca si existe
    else:
        vaca = Vacation(user_id=current_user.id, date=fecha)  # Marca si no existe
        db.session.add(vaca)

    db.session.commit()
    return jsonify({"success": True}), 200


@app.route("/get_vacations")
@login_required
def get_vacations():
    vacations = Vacation.query.all()
    events = []
    user_colors = {}
    color_palette = ["#ff5733", "#33c1ff", "#33ff57", "#ff33a8", "#ffa833"]

    color_index = 0
    for v in vacations:
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file, flash
# Nota: La línea de import 'models' debe funcionar.
from models import db, User, Vacation 
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from functools import wraps
import pandas as pd
import io
import random
import os

# --- Configuración de la Aplicación ---
app = Flask(__name__)
app.config["SECRET_KEY"] = "clave-secreta-muy-dificil-y-larga-para-produccion"
# Usamos un path absoluto para evitar problemas si el script se ejecuta desde otro directorio
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(app.root_path, "vacaciones.db") 

# Inicializamos DB y LoginManager
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' 

# -------------------------------------------------------------
# LÓGICA DE USUARIOS PRECARGADOS Y COLORES
# -------------------------------------------------------------

COLOR_PALETTE = [
    "#4285F4", "#34A853", "#FBBC05", "#673AB7", "#009688", "#76A0D7", "#8E24AA",
    "#00BCD4", "#FF9800", "#795548", "#4CAF50", "#FFEB3B", "#03A9F4", "#CDDC39", 
    "#FFC107", "#E67C73", "#757575", "#00AEEF" # Suficientes colores únicos no rosados/rojos fuertes
]

USUARIOS_A_CARGAR = [
    {"username": "SUPER", "password": "SUPER2025", "is_admin": True, "color": "#000000"}, # Admin
    {"username": "fionna.lucas", "password": "Mendoza2025", "is_admin": False},
    {"username": "orue.hernan", "password": "BuenosAires2025", "is_admin": False},
    {"username": "fazzi.juan", "password": "TDF2025", "is_admin": False},
    # ... Añade aquí los 14 empleados restantes de tu lista final
]

def initialize_users():
    """Crea los usuarios predefinidos en la DB si aún no existen, asignando colores."""
    random.shuffle(COLOR_PALETTE)
    empleado_colors = iter(COLOR_PALETTE)

    for user_data in USUARIOS_A_CARGAR:
        if not User.query.filter_by(username=user_data['username']).first():
            
            # Asignar color si es empleado
            if not user_data.get('is_admin'):
                user_data['color'] = next(empleado_colors)
            else:
                user_data['color'] = "#000000" # Color dummy para el admin

            # Crea el objeto User (usando el color, si tu modelo lo soporta)
            new_user = User(
                username=user_data['username'],
                password=user_data['password'], # ¡Ojo! En producción usa hashing (ej. Werkzeug)
                is_admin=user_data['is_admin'],
                color=user_data['color']
            )
            db.session.add(new_user)
    db.session.commit()

# -------------------------------------------------------------
# DECORADORES PERSONALIZADOS
# -------------------------------------------------------------

def admin_required(f):
    """Decorador para restringir el acceso solo a usuarios con is_admin=True."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Acceso denegado. Solo para administradores.', 'error')
            return redirect(url_for('calendar'))
        return f(*args, **kwargs)
    return decorated_function

# -------------------------------------------------------------
# FUNCIONES DE AUTENTICACIÓN Y NAVEGACIÓN
# -------------------------------------------------------------

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def splash():
    """Ruta inicial para el GIF/Chiste. Redirige al login después del tiempo."""
    # Usaremos el nombre 'splash.html' para la plantilla del chiste/GIF
    return render_template("splash.html") 


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        # **IMPORTANTE**: Aquí se hace la verificación de la contraseña
        if user and user.password == password: 
            login_user(user)
            flash(f"Bienvenido, {user.username}!", "success")
            return redirect(url_for("loading"))
        flash("Usuario o contraseña incorrectos.", "error")
        return redirect(url_for("login")) # Redirigimos al GET de login

    return render_template("login.html")


@app.route("/loading")
@login_required
def loading():
    """Página con barra de progreso DESPUÉS del login exitoso."""
    return render_template("loading.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for("login"))


@app.route("/calendar")
@login_required
def calendar():
    """Vista principal del calendario para todos los usuarios."""
    return render_template("calendar.html")

# -------------------------------------------------------------
# FUNCIONES DEL CALENDARIO (API)
# -------------------------------------------------------------

@app.route("/toggle_vacation", methods=["POST"])
@login_required
def toggle_vacation():
    """Marca o desmarca un día de vacación para el usuario actual."""
    data = request.get_json()
    fecha = data.get("date")

    if not fecha:
        return jsonify({"success": False, "message": "Falta la fecha"}), 400

    # Busca si ya existe una vacación para esta fecha y este usuario
    vaca = Vacation.query.filter_by(user_id=current_user.id, date=fecha).first()
    
    if vaca:
        # Existe: Desmarcar (borrar)
        db.session.delete(vaca)
    else:
        # No existe: Marcar (agregar)
        vaca = Vacation(user_id=current_user.id, date=fecha)
        db.session.add(vaca)

    db.session.commit()
    return jsonify({"success": True}), 200


@app.route("/get_vacations")
@login_required
def get_vacations():
    """Devuelve las vacaciones de TODOS los empleados para el calendario."""
    
    # 1. Obtener todas las vacaciones con la relación de usuario
    vacations = Vacation.query.all()
    events = []

    for v in vacations:
        # Obtener el color del usuario (asumimos que el modelo User tiene un campo 'color')
        user_color = v.user.color if hasattr(v.user, 'color') else "#333333" 
        
        events.append({
            # El título es el nombre de usuario (para mostrar quién lo tomó)
            "title": v.user.username,
            "start": v.date,
            "end": v.date, # Asegura que sea un evento de todo el día
            "backgroundColor": user_color,
            "id_usuario": v.user.id # Útil para lógica avanzada
        })
    
    return jsonify(events)

# -------------------------------------------------------------
# FUNCIONES DEL SÚPER USUARIO (ADMIN)
# -------------------------------------------------------------

# Se elimina la función `create_user` ya que los usuarios son precargados.

@app.route("/export_vacations")
@admin_required
def export_vacations():
    """Recopila todos los datos de vacaciones y los exporta a un archivo Excel."""
    
    vacations = Vacation.query.all()
    data = []

    for v in vacations:
        data.append({
            "Usuario": v.user.username,
            "Fecha": v.date,
            "Es Admin": "Sí" if v.user.is_admin else "No" # Datos extra útiles
        })

    df = pd.DataFrame(data)
    
    # Preparamos el archivo Excel en memoria
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Reporte Vacaciones")
    output.seek(0)

    # Devolvemos el archivo para su descarga
    return send_file(
        output, 
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f"Reporte_Vacaciones_SUPER_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx"
    )

# -------------------------------------------------------------
# INICIALIZACIÓN Y EJECUCIÓN
# -------------------------------------------------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()     # Crea las tablas si no existen
        initialize_users()  # Carga los usuarios de prueba/finales
    
    app.run(debug=True)


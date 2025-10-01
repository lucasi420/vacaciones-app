from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file, flash
from models import db, User, Vacation
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from functools import wraps
import pandas as pd
import io
import random
import os
from config import Config

# Ya no necesitamos werkzeug.security si usamos texto plano.

# --- Configuración de la Aplicación ---
app = Flask(__name__)
app.config.from_object(Config)

# Inicializamos DB y LoginManager
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, inicie sesión para acceder a esta página.'


# -------------------------------------------------------------
# DEFINICIONES DE LÓGICA
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
    """Ruta inicial para la página del GIF/Chiste."""
    return render_template("splash.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        # 🔑 COMPARACIÓN FINAL: Usamos texto plano (==) para que coincida con la DB.
        if user and user.password == password:
            login_user(user)
            flash(f"Bienvenido, {user.username}!", "success")
            return redirect(url_for("loading"))

        # Si el usuario no existe o la contraseña no coincide
        flash("Usuario o contraseña incorrectos.", "error")
        return redirect(url_for("login")) # Esto redirige a GET /login, que muestra splash.html

    # Si es GET, muestra el splash (que contiene el formulario)
    return render_template("splash.html")


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

    vaca = Vacation.query.filter_by(user_id=current_user.id, date=fecha).first()

    if vaca:
        db.session.delete(vaca)
    else:
        vaca = Vacation(user_id=current_user.id, date=fecha)
        db.session.add(vaca)

    db.session.commit()
    return jsonify({"success": True}), 200


@app.route("/get_vacations")
@login_required
def get_vacations():
    """Devuelve las vacaciones de TODOS los empleados para el calendario."""
    vacations = Vacation.query.all()
    events = []

    for v in vacations:
        user_color = v.user.color
        events.append({
            "title": v.user.username,
            "start": v.date,
            "end": v.date,
            "backgroundColor": user_color,
            "id_usuario": v.user.id
        })

    return jsonify(events)


# -------------------------------------------------------------
# FUNCIONES DEL SÚPER USUARIO (ADMIN)
# -------------------------------------------------------------

@app.route("/export_vacations")
@admin_required
def export_vacations():
    """Recopila todos los datos de vacaciones y los exporta a un archivo Excel."""
    vacations = Vacation.query.all()
    data = []

    for v in vacations:
        data.append({
            "Usuario": v.user.username,
            "Rol": "Admin" if v.user.is_admin else "Empleado",
            "Fecha": v.date,
        })

    df = pd.DataFrame(data)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Reporte Vacaciones")
    output.seek(0)

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f"Reporte_Vacaciones_SUPER_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx"
    )


if __name__ == "__main__":
    app.run(debug=True)
    

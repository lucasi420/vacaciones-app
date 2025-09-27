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
        if v.user.username not in user_colors:
            user_colors[v.user.username] = color_palette[color_index % len(color_palette)]
            color_index += 1
        events.append({
            "title": v.user.username,
            "start": v.date,
            "color": user_colors[v.user.username]
        })
    return jsonify(events)


@app.route("/holidays", methods=["GET", "POST"])
@login_required
def holidays():
    if not current_user.is_admin:
        return "Acceso denegado", 403

    if request.method == "POST":
        data = request.get_json()
        fecha = data.get("date")
        if fecha:
            vaca = Vacation(user_id=current_user.id, date=fecha)
            db.session.add(vaca)
            db.session.commit()
            return jsonify({"success": True}), 200
        return jsonify({"success": False}), 400

    return render_template("holidays.html")


@app.route("/create_user", methods=["GET", "POST"])
@login_required
def create_user():
    if not current_user.is_admin:
        return "Acceso denegado", 403

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        is_admin = request.form.get("is_admin") == "on"

        if not username or not password:
            return "Faltan datos", 400

        if User.query.filter_by(username=username).first():
            return "Usuario ya existe", 400

        nuevo_usuario = User(username=username, password=password, is_admin=is_admin)
        db.session.add(nuevo_usuario)
        db.session.commit()

        return redirect(url_for("create_user"))

    return render_template("create_user.html")


@app.route("/export_vacations")
@login_required
def export_vacations():
    if not current_user.is_admin:
        return "Acceso denegado", 403

    vacations = Vacation.query.all()
    data = []

    for v in vacations:
        data.append({
            "Usuario": v.user.username,
            "Fecha": v.date
        })

    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Vacaciones")
    output.seek(0)

    return send_file(output, download_name="vacaciones.xlsx", as_attachment=True)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

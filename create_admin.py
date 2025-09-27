from app import app, db
from models import User

with app.app_context():
    username = input("Ingrese nombre de usuario para el admin: ")
    password = input("Ingrese contraseña para el admin: ")

    if User.query.filter_by(username=username).first():
        print("⚠️ El usuario ya existe.")
    else:
        admin = User(username=username, password=password, is_admin=True)
        db.session.add(admin)
        db.session.commit()
        print(f"✅ Usuario administrador '{username}' creado correctamente.")

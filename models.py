from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import date

# Creamos la base de datos
db = SQLAlchemy()

# Modelo de usuario
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # True = superusuario
    
    # Columna para almacenar el color único de cada usuario en el calendario
    color = db.Column(db.String(7), nullable=False, default="#333333") 

class Vacation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.String(10), nullable=False)  # formato 'YYYY-MM-DD' 

    # Define la relación con el usuario
    user = db.relationship('User', backref=db.backref('vacations', lazy=True))
